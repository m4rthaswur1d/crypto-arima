from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class VolRegimeConfig:
    window: int = 30
    annualization: int = 365
    q_low: float = 0.33
    q_high: float = 0.67


def realized_volatility(
    r: pd.Series,
    window: int = 30,
    annualization: int = 365,
) -> pd.Series:
    if not isinstance(r, pd.Series):
        raise TypeError("r must be a pd.Series")
    if window <= 1:
        raise ValueError("window must be > 1")
    if annualization <= 0:
        raise ValueError("annualization must be positive")

    rv = r.dropna().rolling(window).std() * np.sqrt(annualization)
    rv.name = f"realized_vol_{window}"
    return rv


def label_vol_regimes_quantiles(
    vol: pd.Series,
    q_low: float = 0.33,
    q_high: float = 0.67,
    labels: tuple[str, str, str] = ("LowVol", "MidVol", "HighVol"),
) -> pd.Series:
    if not isinstance(vol, pd.Series):
        raise TypeError("vol must be a pd.Series")
    if not (0.0 < q_low < q_high < 1.0):
        raise ValueError("Require 0 < q_low < q_high < 1")
    if len(labels) != 3:
        raise ValueError("labels must have length 3")

    v = vol.dropna()
    lo = float(v.quantile(q_low))
    hi = float(v.quantile(q_high))

    out = pd.Series(index=vol.index, dtype="object", name="vol_regime")
    out.loc[vol < lo] = labels[0]
    out.loc[(vol >= lo) & (vol < hi)] = labels[1]
    out.loc[vol >= hi] = labels[2]

    return out


def build_regime_frame(
    r: pd.Series,
    cfg: VolRegimeConfig = VolRegimeConfig(),
) -> pd.DataFrame:
    if not isinstance(r, pd.Series):
        raise TypeError("r must be a pd.Series")

    r = r.dropna().astype(float)
    vol = realized_volatility(r, window=cfg.window, annualization=cfg.annualization)
    regime = label_vol_regimes_quantiles(vol, q_low=cfg.q_low, q_high=cfg.q_high)

    df = pd.DataFrame(
        {
            "ret": r,
            "abs_ret": r.abs(),
            "ret2": r.pow(2),
            "realized_vol": vol,
            "vol_regime": regime,
        }
    ).dropna()

    return df


def regime_summary(df: pd.DataFrame) -> pd.DataFrame:
    required = {"ret", "abs_ret", "ret2", "realized_vol", "vol_regime"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"df missing columns: {missing}")

    g = df.groupby("vol_regime", observed=True)

    out = pd.DataFrame(
        {
            "N": g.size(),
            "MeanRet": g["ret"].mean(),
            "StdRet": g["ret"].std(),
            "MeanAbsRet": g["abs_ret"].mean(),
            "MeanRet2": g["ret2"].mean(),
            "MeanRealizedVol": g["realized_vol"].mean(),
        }
    )

    # Add a simple drawdown proxy on cumulative returns within each regime segment is complex;
    # keep it simple: show tail risk via quantiles of returns.
    out["Ret_q05"] = g["ret"].quantile(0.05)
    out["Ret_q95"] = g["ret"].quantile(0.95)

    return out.sort_index()


def regime_transition_matrix(regime: pd.Series, normalize: bool = True) -> pd.DataFrame:
    if not isinstance(regime, pd.Series):
        raise TypeError("regime must be a pd.Series")

    r0 = regime.dropna()
    r1 = r0.shift(-1).dropna()
    r0 = r0.loc[r1.index]

    mat = pd.crosstab(r0, r1)

    if normalize:
        mat = mat.div(mat.sum(axis=1), axis=0)

    return mat


def regime_spans(df: pd.DataFrame) -> pd.DataFrame:
    if "vol_regime" not in df.columns:
        raise ValueError("df must contain 'vol_regime'")

    reg = df["vol_regime"].dropna()
    change = reg.ne(reg.shift()).cumsum()
    spans = (
        reg.groupby(change)
        .agg(regime="first", start=lambda x: x.index[0], end=lambda x: x.index[-1], n_days="size")
        .reset_index(drop=True)
    )
    return spans