# Proxy replication: Optimal Trading with Price Impact

This repository is a proxy replication inspired by Patrick Chan, Ronnie Sircar, and Iosif Zimbidis, "Optimal Trading under Instantaneous and Persistent Price Impact, Predictable Returns and Multiscale Stochastic Volatility" (arXiv:2507.17162).

## Scope

The paper extends the constant-volatility Gârleanu-Pedersen strategy with predictable returns, temporary trading costs, persistent price impact, and fast/slow volatility corrections. This project implements the constant-volatility target-position baseline and a realized-volatility correction on SPY.

## Data

`data/spy.csv` contains daily SPY OHLCV and adjusted-close data downloaded from Yahoo Finance.

Source: https://finance.yahoo.com/quote/SPY/history/

## Run

```text
python replicate.py
```

The script writes `results.csv` comparing baseline and volatility-adjusted PnL, volatility, and Sharpe-like statistics.

## Limitations

The full paper derives asymptotic HJB corrections for a continuous-time model. This proxy uses daily prices, a rolling mean-reversion signal, and a discrete-time execution simulator; it is designed to demonstrate the baseline-to-extension logic, not to reproduce the paper's theorem numerically.

