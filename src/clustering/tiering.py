from __future__ import annotations

import hdbscan
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


DEFAULT_TIER_MULTIPLIERS = {"Tier 1": 1.0, "Tier 2": 0.5, "Tier 3": 0.05}


def load_pwc_coords(pwc_raw: pd.DataFrame) -> pd.DataFrame:
    """Standardize raw PWC columns (X, Y, MSOA21CD) to (msoa_code, easting, northing)."""
    return pwc_raw.rename(
        columns={"X": "easting", "Y": "northing", "MSOA21CD": "msoa_code"}
    )[["msoa_code", "easting", "northing"]]


def assign_tiers(
    forecasts: pd.DataFrame,
    pwc: pd.DataFrame,
    month: str,
    threshold: float,
    min_cluster_size: int = 5,
    min_samples: int = 3,
    intensity_cap_quantile: float | None = 0.95,
    hotspot_cluster_quantile: float = 0.80,
    tier_multipliers: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Cluster MSOAs with HDBSCAN on (easting, northing, intensity) and assign tiers.

    Parameters

    forecasts : DataFrame with columns ['msoa_code', 'month', 'intensity'].
    pwc : DataFrame with columns ['msoa_code', 'easting', 'northing'].
    month : Month to slice from forecasts, e.g. '2026-04-01'.
    threshold : Intensity cutoff that splits every non-hotspot MSOA (whether clustered or
        noise) into Tier 2 (above) vs Tier 3 (below).
    hotspot_cluster_quantile : A cluster is a "hotspot" if its MEAN intensity ranks at
        or above this quantile of all cluster means. Members of hotspot clusters become
        Tier 1; members of other clusters become Tier 2. This defines a hotspot by crime
        level (high intensity AND spatial coherence), not by cluster-membership
        confidence. Higher value => fewer, more selective Tier 1 areas. Default 0.80
        (top ~20% of clusters by mean intensity).
    min_cluster_size : Smallest group HDBSCAN will call a cluster. Default 5
        preserves smaller-city hotspots that 10+ would
        merge into larger neighbours. 
    intensity_cap_quantile : Winsorize intensity at this quantile before scaling so
        extreme outliers (central-London hotspots) don't distort the feature
        space and self-isolate as noise. Only affects the clustering input; 
        'intensity' and 'final_weight' use the original uncapped value.
        Set to None to disable. Default 0.95.

    Output
    DataFrame with columns
        ['msoa_code', 'easting', 'northing', 'intensity',
         'cluster_label', 'membership_prob', 'tier', 'final_weight'].
    """
    multipliers = tier_multipliers or DEFAULT_TIER_MULTIPLIERS

    month_slice = forecasts.loc[
        forecasts["month"] == month, ["msoa_code", "intensity"]
    ]
    merged = month_slice.merge(pwc, on="msoa_code", how="inner")
    if merged.empty:
        raise ValueError(f"No MSOAs left after merging forecasts for {month} with PWC.")
    if merged["intensity"].isna().any():
        raise ValueError("NaN intensities after merge; check forecast inputs.")

    # Intensity is treated as a third axis alongside coordinates so HDBSCAN groups
    # MSOAs that are both spatially close AND have similar crime intensity.
    # Winsorizing intensity prevents extreme hotspots from stretching the scaled
    # axis so far that they get isolated as noise (e.g. City of London).
    features = merged[["easting", "northing", "intensity"]].copy()
    if intensity_cap_quantile is not None:
        cap = features["intensity"].quantile(intensity_cap_quantile)
        features["intensity"] = features["intensity"].clip(upper=cap)
    scaled = MinMaxScaler().fit_transform(features.to_numpy())

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size, min_samples=min_samples
    )
    clusterer.fit(scaled)
    merged["cluster_label"] = clusterer.labels_
    merged["membership_prob"] = clusterer.probabilities_

    is_noise = merged["cluster_label"] == -1
    at_risk = merged["intensity"] > threshold

    # A cluster is a "hotspot" if its MEAN intensity is high relative to other clusters.
    # Tier 1 = members of hotspot clusters (high crime AND spatially coherent). This
    # replaces the old membership_prob rule, which rewarded cluster cohesion rather than
    # crime level and inflated Tier 1.
    cluster_mean = merged.loc[~is_noise].groupby("cluster_label")["intensity"].mean()
    hot_cutoff = cluster_mean.quantile(hotspot_cluster_quantile)
    hotspot_clusters = cluster_mean[cluster_mean >= hot_cutoff].index
    in_hotspot = merged["cluster_label"].isin(hotspot_clusters) & ~is_noise

    # Tier 1 is the hotspot clusters; everyone else is split purely by intensity vs the
    # threshold (above -> Tier 2, below -> Tier 3). Applying the threshold to clustered
    # AND noise points alike keeps Tiers 2/3 intensity-driven and stops low-crime cluster
    # members from defaulting into Tier 2.
    merged["tier"] = np.select(
        [in_hotspot, at_risk],
        ["Tier 1", "Tier 2"],
        default="Tier 3",
    )
    merged["final_weight"] = merged["intensity"] * merged["tier"].map(multipliers)

    return merged[
        [
            "msoa_code",
            "easting",
            "northing",
            "intensity",
            "cluster_label",
            "membership_prob",
            "tier",
            "final_weight",
        ]
    ]
