# Crypto Market Dynamics Research Project: Return Predictability vs Volatility Regimes

## Overview

This project investigates the short-horizon predictability of cryptocurrency markets through two complementary lenses:

1. **Mean return forecasting using ARIMA models**
2. **Volatility structure and regime behavior using realized volatility and regime classification**

Using daily Bitcoin (BTC) and Ethereum (ETH) data, the analysis demonstrates a key empirical result commonly observed in financial markets:  
**mean returns are difficult to predict, while volatility exhibits persistent, structured behavior.**

## Data

- Daily BTC-USD and ETH-USD prices (Yahoo Finance)
- Sample period: January 1st, 2018 – January 15th, 2025
- Log returns computed from adjusted close prices

## Methodology

### 1. Return Predictability (ARIMA)

Log returns are modeled using low-order **ARIMA(p,0,q)** specifications.

**Candidate models are selected using:**
- AIC: Akaike Information Criterion, evaluates model fit while applying a moderate penalty for additional parameters, making it useful for comparing models with an emphasis on predictive performance.
- \[
\mathrm{AIC} = -2 \log(L) + 2k
\]
- BIC: Bayesian Information Criterion, applies a stronger penalty for model complexity, favoring more parsimonious models and providing a complementary perspective for model selection and robustness checks.
- \[
\mathrm{BIC} = -2 \log(L) + k \log(n)
\]
- Ljung–Box residual diagnostics
- Rolling 1-step-ahead forecasts evaluated using MAE and RMSE

**Result:**  
Despite careful model selection and validation, ARIMA models show limited out-of-sample predictive power for daily returns, consistent with weak-form market efficiency.

### 2. Volatility Regime Analysis

- 30-day rolling realized volatility (annualized)
- Volatility regimes classified via cross-sectional quantiles:
  - Low volatility
  - Medium volatility
  - High volatility

**Regime characteristics analyzed via:**
- Return distributions
- Regime persistence
- Transition matrices
- Average regime duration

**Result:**  
Volatility exhibits strong regime persistence for both BTC and ETH, with high-volatility states remaining stable approximately **90–95%** of the time on a day-to-day basis.

## Key Findings

- **Returns:** Minimal linear autocorrelation and weak forecastability
- **Volatility:** Clear clustering and regime persistence
- **BTC vs ETH:** ETH displays consistently higher realized volatility and fatter tails
- **Risk Insight:** Volatility regimes provide more actionable structure than mean return forecasts

## Takeaway

While short-horizon return prediction remains challenging in crypto markets, volatility dynamics exhibit stable and interpretable structure.  
This suggests that **risk modeling and regime awareness may be more informative than return forecasting alone**, particularly for portfolio construction and risk management applications.
