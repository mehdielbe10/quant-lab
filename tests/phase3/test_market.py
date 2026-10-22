"""Phase 3 tests: correlated market (Cholesky) and Black-Scholes delta."""
import numpy as np
import pandas as pd

from quantlab.simulation import simulate_market, bs_call, bs_delta

S0, K, R, SIGMA, T = 100.0, 100.0, 0.05, 0.20, 1.0


def test_bs_delta_matches_finite_difference():
    h = 1e-4
    fd = (bs_call(S0 + h, K, R, SIGMA, T) - bs_call(S0 - h, K, R, SIGMA, T)) / (2 * h)
    assert abs(bs_delta(S0, K, R, SIGMA, T) - fd) < 1e-6
    assert 0.0 < bs_delta(S0, K, R, SIGMA, T) < 1.0


# ---- the multi-asset laboratory --------------------------------------------------------------
MU3 = np.array([0.06, 0.08, 0.10])
VOL3 = np.array([0.10, 0.20, 0.30])
CORR3 = np.array([[1.0, 0.9, 0.2], [0.9, 1.0, 0.3], [0.2, 0.3, 1.0]])
COV3 = np.outer(VOL3, VOL3) * CORR3


def test_market_shape_index_and_columns():
    p = simulate_market(MU3, COV3, n_days=100, seed=0, names=["a", "b", "c"])
    assert isinstance(p, pd.DataFrame)
    assert p.shape == (101, 3)
    assert list(p.columns) == ["a", "b", "c"]
    assert isinstance(p.index, pd.DatetimeIndex)
    assert (p.iloc[0] == 100.0).all()
    assert (p > 0).all().all()
    assert list(simulate_market(MU3, COV3, 5, seed=0).columns) == ["A1", "A2", "A3"]


def test_market_is_reproducible():
    a = simulate_market(MU3, COV3, 200, seed=11)
    b = simulate_market(MU3, COV3, 200, seed=11)
    c = simulate_market(MU3, COV3, 200, seed=12)
    pd.testing.assert_frame_equal(a, b)
    assert not a.equals(c)


def test_market_log_returns_have_the_right_mean_and_covariance():
    # Over a very long history the sample moments must be close to the TRUE parameters.
    p = simulate_market(MU3, COV3, n_days=200_000, seed=1)
    r = np.diff(np.log(p.values), axis=0)
    years = 200_000 / 252
    mean_annual = r.mean(axis=0) * 252
    expected_mean = MU3 - 0.5 * np.diag(COV3)                      # Ito correction on log-returns
    assert np.all(np.abs(mean_annual - expected_mean) < 4 * VOL3 / np.sqrt(years))
    cov_annual = np.cov(r, rowvar=False) * 252
    np.testing.assert_allclose(cov_annual, COV3, rtol=0.04)


def test_market_assets_are_correlated_as_requested():
    p = simulate_market(MU3, COV3, n_days=100_000, seed=2)
    r = np.diff(np.log(p.values), axis=0)
    corr = np.corrcoef(r, rowvar=False)
    np.testing.assert_allclose(corr, CORR3, atol=0.02)


def test_market_ar1_adds_autocorrelation_but_keeps_the_variance():
    p = simulate_market(MU3, COV3, n_days=200_000, seed=3, ar1=0.05)
    r = np.diff(np.log(p.values), axis=0)
    for j in range(3):
        rho1 = np.corrcoef(r[1:, j], r[:-1, j])[0, 1]
        assert abs(rho1 - 0.05) < 4 / np.sqrt(len(r))
    np.testing.assert_allclose(np.cov(r, rowvar=False) * 252, COV3, rtol=0.05)
    p0 = simulate_market(MU3, COV3, n_days=200_000, seed=3, ar1=0.0)
    r0 = np.diff(np.log(p0.values), axis=0)
    assert abs(np.corrcoef(r0[1:, 0], r0[:-1, 0])[0, 1]) < 4 / np.sqrt(len(r0))
