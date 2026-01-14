# from __future__ import annotations
# import numpy as np
# import pandas as pd
# import warnings
# from statsmodels.tsa.arima.model import ARIMA
#
# def rolling_backtest(
#     y: pd.Series,
#     order: tuple[int,int,int],
#     train_size: float = 0.8,
#     refit_every: int = 7,
#     maxiter: int = 100,
# ) -> dict:
#     y = y.dropna().copy()
#
#     n = len(y)
#     split = int(n * train_size)
#     train = y.iloc[:split]
#     test = y.iloc[split:]
#
#     preds = []
#     actuals = []
#
#     history = train.copy()
#     res = None
#
#     for i, (tstamp, y_true) in enumerate(test.items()):
#         # refit periodically (or first time)
#         if (res is None) or (i % refit_every == 0):
#             with warnings.catch_warnings():
#                 warnings.simplefilter("ignore")
#                 model = ARIMA(history, order=order)
#                 res = model.fit(method_kwargs={"maxiter": maxiter})
#
#         # 1-step forecast
#         y_hat = float(res.forecast(1).iloc[0])
#         preds.append(y_hat)
#         actuals.append(float(y_true))
#
#         # expand history with the true observation (keep real timestamp)
#         history.loc[tstamp] = y_true
#
#     preds = np.array(preds)
#     actuals = np.array(actuals)
#
#     mae = float(np.mean(np.abs(preds - actuals)))
#     rmse = float(np.sqrt(np.mean((preds - actuals) ** 2)))
#
#     return {"mae": mae, "rmse": rmse, "n_test": len(test)}
