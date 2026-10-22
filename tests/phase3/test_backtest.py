"""Phase 3 tests: a backtester that does not lie."""
import numpy as np
import pandas as pd

from quantlab.backtest import (momentum_positions, backtest, max_drawdown, turnover,
                               rolling_min_variance_positions)
from quantlab.portfolio import min_variance_weights, shrink_covariance


def _prices_two_assets():
    idx = pd.date_range("2020-01-01", periods=8, freq="B")
    up = 100.0 + np.arange(8)            # always rising
    down = 100.0 - np.arange(8)          # always falling
    return pd.DataFrame({"UP": up, "DOWN": down}, index=idx)


def test_momentum_positions_hand_computed():
    p = _prices_two_assets()
    pos = momentum_positions(p, lookback=3, skip=1)
    assert pos.shape == p.shape
    assert list(pos.columns) == ["UP", "DOWN"]
    # Not enough history for the first `lookback` rows.
    assert pos.iloc[:3].isna().all().all()
    # From row 3 on: UP has positive momentum, DOWN negative; 2 assets -> weights +-0.5.
    np.testing.assert_allclose(pos.iloc[3].values, [0.5, -0.5])
    np.testing.assert_allclose(pos.iloc[7].values, [0.5, -0.5])


def test_momentum_signal_skips_the_most_recent_days():
    # Rise for 9 days, then crash on the last day. With skip=2 the crash is not seen yet.
    idx = pd.date_range("2020-01-01", periods=12, freq="B")
    prices = pd.DataFrame({"A": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 50.0]}, index=idx)
    pos = momentum_positions(prices, lookback=5, skip=2)
    assert pos.iloc[-1, 0] == 1.0       # signal built from P[t-2] / P[t-5]
    pos0 = momentum_positions(prices, lookback=5, skip=0)
    assert pos0.iloc[-1, 0] == -1.0     # without skipping, the crash flips the signal


def test_momentum_positions_have_no_lookahead():
    rng = np.random.default_rng(0)
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    prices = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, (300, 3)), axis=0)),
                          index=idx, columns=list("ABC"))
    base = momentum_positions(prices, lookback=100, skip=10)
    changed = prices.copy()
    changed.iloc[200:] = changed.iloc[200:] * 3.0          # rewrite the future after row 200
    new = momentum_positions(changed, lookback=100, skip=10)
    pd.testing.assert_frame_equal(base.iloc[:200], new.iloc[:200])


def test_backtest_hand_computed_with_costs():
    idx = pd.date_range("2020-01-01", periods=3, freq="B")
    prices = pd.DataFrame({"A": [100.0, 110.0, 121.0]}, index=idx)
    pos = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=idx)
    free = backtest(prices, pos, cost_bps=0.0)
    np.testing.assert_allclose(free.values, [0.0, 0.10, 0.10], atol=1e-12)
    paid = backtest(prices, pos, cost_bps=10.0)
    # Cost of entering the position (turnover 1.0) is paid on day 1: 10 bps = 0.001.
    np.testing.assert_allclose(paid.values, [0.0, 0.099, 0.10], atol=1e-12)
    assert paid.index.equals(prices.index)


def test_backtest_weights_decided_at_t_earn_the_return_of_t_plus_1():
    idx = pd.date_range("2020-01-01", periods=4, freq="B")
    prices = pd.DataFrame({"A": [100.0, 110.0, 121.0, 133.1]}, index=idx)
    pos = pd.DataFrame({"A": [0.0, 1.0, 0.0, 0.0]}, index=idx)   # hold only from the close of day 1
    net = backtest(prices, pos, cost_bps=0.0)
    assert abs(net.iloc[1]) < 1e-12          # the day-1 return was NOT earned
    assert abs(net.iloc[2] - 0.10) < 1e-12   # the day-2 return was
    assert abs(net.iloc[3]) < 1e-12


def test_backtest_treats_nan_weights_as_zero():
    idx = pd.date_range("2020-01-01", periods=4, freq="B")
    prices = pd.DataFrame({"A": [100.0, 110.0, 121.0, 133.1]}, index=idx)
    pos = pd.DataFrame({"A": [np.nan, np.nan, 1.0, 1.0]}, index=idx)
    net = backtest(prices, pos, cost_bps=0.0)
    assert not net.isna().any()
    np.testing.assert_allclose(net.values, [0.0, 0.0, 0.0, 0.10], atol=1e-12)


def test_max_drawdown_hand_computed():
    assert abs(max_drawdown(pd.Series([0.1, -0.5, 0.2])) - (-0.5)) < 1e-12
    # The deepest drawdown is the LAST one: equity 1.5, 1.35, 2.7, 1.08 -> 1.08 / 2.7 - 1 = -0.6
    assert abs(max_drawdown(pd.Series([0.5, -0.1, 1.0, -0.6])) - (-0.6)) < 1e-12
    assert abs(max_drawdown(pd.Series([0.01, 0.02, 0.03]))) < 1e-12     # never below a previous peak


def test_turnover_hand_computed():
    idx = pd.date_range("2020-01-01", periods=4, freq="B")
    pos = pd.DataFrame({"A": [0.0, 0.5, 0.5, -0.5], "B": [0.0, -0.5, -0.5, 0.5]}, index=idx)
    # daily turnover on days 1..3: 1.0, 0.0, 2.0  -> average 1.0
    assert abs(turnover(pos) - 1.0) < 1e-12


def test_turnover_counts_nan_as_zero():
    idx = pd.date_range("2020-01-01", periods=3, freq="B")
    pos = pd.DataFrame({"A": [np.nan, 0.5, 0.5]}, index=idx)
    assert abs(turnover(pos) - 0.25) < 1e-12     # days 1..2: 0.5, 0.0


def test_end_to_end_on_random_walks_costs_hurt():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2015-01-01", periods=1500, freq="B")
    prices = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, (1500, 5)), axis=0)),
                          index=idx, columns=list("ABCDE"))
    pos = momentum_positions(prices, lookback=120, skip=10)
    free = backtest(prices, pos, cost_bps=0.0)
    costly = backtest(prices, pos, cost_bps=50.0)
    assert len(free) == len(prices)
    assert not free.isna().any()
    assert (free.iloc[:120] == 0).all()                 # nothing traded during the warm-up
    assert costly.sum() < free.sum()
    assert turnover(pos) > 0
    assert max_drawdown(free) < 0


def _random_prices(n=400, p=4, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, (n, p)), axis=0)),
                        index=idx, columns=list("ABCD")[:p])


def test_rolling_min_variance_shape_warmup_and_weights():
    prices = _random_prices()
    pos = rolling_min_variance_positions(prices, window=100, rebalance_every=20, delta=0.2)
    assert pos.shape == prices.shape
    assert pos.iloc[:100].isna().all().all()
    assert not pos.iloc[100:].isna().any().any()
    np.testing.assert_allclose(pos.iloc[100:].sum(axis=1).values, 1.0, atol=1e-9)
    # Weights only change on rebalance dates (100, 120, 140, ...).
    assert (pos.iloc[100:120].nunique() == 1).all()
    assert not np.allclose(pos.iloc[119].values, pos.iloc[120].values)


def test_rolling_min_variance_matches_a_direct_computation():
    prices = _random_prices()
    pos = rolling_min_variance_positions(prices, window=100, rebalance_every=20, delta=0.3)
    r = prices.pct_change().values
    S = shrink_covariance(np.cov(r[41:141], rowvar=False), 0.3)    # returns of days 41..140
    np.testing.assert_allclose(pos.iloc[140].values, min_variance_weights(S), atol=1e-9)


def test_rolling_min_variance_has_no_lookahead():
    prices = _random_prices()
    base = rolling_min_variance_positions(prices, window=100, rebalance_every=20)
    changed = prices.copy()
    changed.iloc[250:] = changed.iloc[250:] * np.linspace(1, 3, len(prices) - 250)[:, None]
    new = rolling_min_variance_positions(changed, window=100, rebalance_every=20)
    pd.testing.assert_frame_equal(base.iloc[:250], new.iloc[:250])
