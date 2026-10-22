"""S5: a small, honest backtester."""
from __future__ import annotations

import pandas as pd


def momentum_positions(prices: pd.DataFrame, lookback: int = 252, skip: int = 21) -> pd.DataFrame:
    """Time-series momentum target weights.

    For each asset and each date t: signal = sign(P[t - skip] / P[t - lookback] - 1).
    Weight = signal / n_assets (so the gross exposure is at most 1).
    The weight at date t may only use prices up to and including date t.
    Dates without enough history are NaN.
    Return a DataFrame with the same index and columns as prices.
    """
    raise NotImplementedError


def backtest(prices: pd.DataFrame, positions: pd.DataFrame, cost_bps: float = 5.0) -> pd.Series:
    """Daily net strategy returns.

    Weights decided at the close of day t earn the return of day t + 1.
      gross[t] = sum_i w[t-1, i] * r[t, i]          with r[t] = P[t] / P[t-1] - 1
      cost[t]  = cost_bps / 10_000 * sum_i |w[t-1, i] - w[t-2, i]|
      net[t]   = gross[t] - cost[t]
    NaN weights count as 0 and weights before the first date are 0.
    Return a Series with the same index as prices (the first value is 0.0).
    """
    raise NotImplementedError


def max_drawdown(returns) -> float:
    """Largest peak-to-trough loss of the equity curve (1 + r).cumprod(), as a NEGATIVE number (e.g. -0.35)."""
    raise NotImplementedError


def turnover(positions: pd.DataFrame) -> float:
    """Average over days of sum_i |w[t, i] - w[t-1, i]| (NaN weights count as 0; skip the first day)."""
    raise NotImplementedError


def rolling_min_variance_positions(prices: pd.DataFrame, window: int = 252,
                                   rebalance_every: int = 21, delta: float = 0.2) -> pd.DataFrame:
    """Walk-forward minimum-variance portfolio (links stages S2, S4 and S5).

    r = prices.pct_change(). At the close of day t (t = window, window + rebalance_every, ...):
      - take the `window` most recent returns r[t-window+1 .. t]  (nothing after t!);
      - sample covariance (np.cov, rowvar=False), shrink it with shrink_covariance(., delta);
      - weights = min_variance_weights(shrunk covariance).
    Weights are held unchanged until the next rebalance date.
    Rows before the first rebalance date are NaN. Same index and columns as prices.
    """
    raise NotImplementedError
