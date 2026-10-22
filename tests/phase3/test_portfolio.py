"""Phase 3 tests: mean-variance portfolios."""
import numpy as np

from quantlab.portfolio import (min_variance_weights, max_sharpe_weights,
                                long_only_min_variance, shrink_covariance)

# 3 assets with vols 10%, 20%, 30% and strongly correlated first two.
VOL = np.array([0.10, 0.20, 0.30])
CORR = np.array([[1.0, 0.9, 0.2], [0.9, 1.0, 0.3], [0.2, 0.3, 1.0]])
COV3 = np.outer(VOL, VOL) * CORR
MU3 = np.array([0.06, 0.08, 0.10])


def _vol(w, cov):
    return float(np.sqrt(w @ cov @ w))


def test_min_variance_two_uncorrelated_assets():
    cov = np.diag([0.01, 0.06])
    np.testing.assert_allclose(min_variance_weights(cov), [6 / 7, 1 / 7], atol=1e-12)


def test_min_variance_two_correlated_assets():
    cov = np.array([[0.04, 0.01], [0.01, 0.09]])
    # w1 = (s22 - s12) / (s11 + s22 - 2 s12) = 0.08 / 0.11
    np.testing.assert_allclose(min_variance_weights(cov), [8 / 11, 3 / 11], atol=1e-12)


def test_min_variance_three_assets_properties():
    w = min_variance_weights(COV3)
    assert abs(w.sum() - 1.0) < 1e-10
    # Optimality condition: every entry of cov @ w is the same number (the Lagrange multiplier).
    g = COV3 @ w
    np.testing.assert_allclose(g, g[0] * np.ones(3), atol=1e-10)
    # Shorting is allowed and used here.
    assert w.min() < 0
    # It beats equal weights and the best single asset.
    assert _vol(w, COV3) < _vol(np.ones(3) / 3, COV3)
    assert _vol(w, COV3) < VOL.min()


def test_max_sharpe_known_case():
    w = max_sharpe_weights(MU3, COV3, rf=0.02)
    assert abs(w.sum() - 1.0) < 1e-10
    # w is proportional to inv(cov) @ (mu - rf); here it equals [147, -45, 16] / 118 (a short position!)
    np.testing.assert_allclose(w, np.array([147.0, -45.0, 16.0]) / 118.0, atol=1e-8)


def test_max_sharpe_beats_random_portfolios():
    rf = 0.02
    w = max_sharpe_weights(MU3, COV3, rf=rf)
    best = (w @ MU3 - rf) / _vol(w, COV3)
    rng = np.random.default_rng(0)
    for _ in range(500):
        v = rng.normal(size=3)
        v = v / v.sum()
        if abs(v.sum() - 1) < 1e-9 and v.sum() > 0:
            assert (v @ MU3 - rf) / _vol(v, COV3) <= best + 1e-9


def test_long_only_min_variance_known_case():
    w = long_only_min_variance(COV3)
    assert abs(w.sum() - 1.0) < 1e-6
    assert w.min() > -1e-6
    np.testing.assert_allclose(w, [0.9545, 0.0, 0.0455], atol=3e-3)


def test_long_only_costs_variance_compared_to_unconstrained():
    assert _vol(long_only_min_variance(COV3), COV3) >= _vol(min_variance_weights(COV3), COV3) - 1e-9


def test_long_only_respects_max_weight():
    w = long_only_min_variance(COV3, max_weight=0.5)
    assert abs(w.sum() - 1.0) < 1e-6
    assert w.min() > -1e-6
    assert w.max() < 0.5 + 1e-6
    assert _vol(w, COV3) >= _vol(long_only_min_variance(COV3), COV3) - 1e-9


def test_shrinkage_hand_computed():
    S = np.array([[4.0, 2.0], [2.0, 2.0]])
    out = shrink_covariance(S, 0.5)
    np.testing.assert_allclose(out, [[3.5, 1.0], [1.0, 2.5]], atol=1e-12)


def test_shrinkage_endpoints_and_conditioning():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(30, 20))                 # few observations: ill-conditioned covariance
    S = np.cov(X, rowvar=False)
    np.testing.assert_allclose(shrink_covariance(S, 0.0), S, atol=1e-12)
    target = np.trace(S) / 20 * np.eye(20)
    np.testing.assert_allclose(shrink_covariance(S, 1.0), target, atol=1e-12)
    mid = shrink_covariance(S, 0.2)
    assert abs(np.trace(mid) - np.trace(S)) < 1e-10
    assert np.linalg.cond(mid) < np.linalg.cond(S)
    assert np.linalg.eigvalsh(mid).min() > 0
