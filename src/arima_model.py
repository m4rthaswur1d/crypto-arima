from __future__ import annotations
import warnings
import pandas as pd
from dataclasses import dataclass
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

@dataclass
class ARIMAResult:
    order: tuple[int, int, int]
    aic: float
    bic: float
    lb_pvalue_10: float
    lb_pvalue_20: float
    converged: bool

def fit_arima(y: pd.Series, order: tuple[int,int,int]) -> ARIMAResult:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        model = ARIMA(y, order=order)
        res = model.fit()

    resid = res.resid

    lb10 = acorr_ljungbox(resid, lags=[10], return_df=True)["lb_pvalue"].iloc[0]
    lb20 = acorr_ljungbox(resid, lags=[20], return_df=True)["lb_pvalue"].iloc[0]

    return ARIMAResult(
        order=order,
        aic=res.aic,
        bic=res.bic,
        lb_pvalue_10=lb10,
        lb_pvalue_20=lb20,
        converged=res.mle_retvals.get("converged", True)
    )


def evaluate_candidates(y: pd.Series, orders: list[tuple[int,int,int]]) -> pd.DataFrame:
    rows = []

    for order in orders:
        try:
            r = fit_arima(y, order)
            rows.append({
                "p": order[0],
                "d": order[1],
                "q": order[2],
                "aic": r.aic,
                "bic": r.bic,
                "lb_pvalue_10": r.lb_pvalue_10,
                "lb_pvalue_20": r.lb_pvalue_20,
                "converged": r.converged
            })
        except Exception as e:
            rows.append({
                "p": order[0],
                "d": order[1],
                "q": order[2],
                "aic": None,
                "bic": None,
                "lb_pvalue_10": None,
                "lb_pvalue_20": None,
                "converged": False,
                "error": str(e)
            })

    return pd.DataFrame(rows)
