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
    high_confidence_prob: float = 0.7,
    tier_multipliers: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Cluster MSOAs with HDBSCAN on (easting, northing, intensity) and assign tiers.

    Parameters

    forecasts : DataFrame with columns ['msoa_code', 'month', 'intensity'].
    pwc : DataFrame with columns ['msoa_code', 'easting', 'northing'].
    month : Month to slice from forecasts, e.g. '2026-04-01'.
    threshold : Intensity cutoff. Noise points above this become Tier 2 (at-risk),
        otherwise Tier 3. In-cluster points with membership_prob >= high_confidence_prob
        become Tier 1, otherwise Tier 2.
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
    high_conf = merged["membership_prob"] >= high_confidence_prob
    at_risk = merged["intensity"] > threshold

    merged["tier"] = np.select(
        [is_noise & at_risk, is_noise & ~at_risk, ~is_noise & high_conf],
        ["Tier 2", "Tier 3", "Tier 1"],
        default="Tier 2",
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
