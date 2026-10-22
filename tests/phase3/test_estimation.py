"""Phase 3 (S2) tests: estimating means and covariances from a finite history."""
import numpy as np
import pandas as pd

from quantlab.estimation import annualised_mean_cov, mean_standard_error
from quantlab.simulation import simulate_market

MU = np.array([0.06, 0.08, 0.10])
VOL = np.array([0.10, 0.20, 0.30])
CORR = np.array([[1.0, 0.9, 0.2], [0.9, 1.0, 0.3], [0.2, 0.3, 1.0]])
COV = np.outer(VOL, VOL) * CORR


def test_annualised_mean_cov_hand_computed():
    r = np.array([[0.01, 0.02], [0.03, 0.00], [0.02, -0.02]])
    mu, cov = annualised_mean_cov(r, periods_per_year=100)
    np.testing.assert_allclose(mu, [0.02 * 100, 0.0 * 100], atol=1e-12)
    # column 0 deviations: -0.01, 0.01, 0 -> variance 2e-4 / 2 = 1e-4
    # column 1 deviations: 0.02, 0, -0.02 -> variance 8e-4 / 2 = 4e-4
    # covariance: (-0.01 * 0.02 + 0 + 0) / 2 = -1e-4
    np.testing.assert_allclose(cov, np.array([[1e-4, -1e-4], [-1e-4, 4e-4]]) * 100, atol=1e-12)


def test_annualised_mean_cov_accepts_dataframes():
    r = pd.DataFrame(np.random.default_rng(0).normal(0.0005, 0.01, (300, 4)))
    mu, cov = annualised_mean_cov(r)
    assert mu.shape == (4,) and cov.shape == (4, 4)
    np.testing.assert_allclose(cov, cov.T, atol=1e-12)


def test_mean_standard_error_hand_computed():
    r = np.array([[0.01], [0.03], [0.02], [0.02]])      # n = 4, std (ddof=1) = sqrt(2e-4 / 3)
    se = mean_standard_error(r, periods_per_year=100)
    np.testing.assert_allclose(se, [np.sqrt(2e-4 / 3) / 2 * 100], atol=1e-12)


def test_the_mean_return_is_barely_estimable_but_the_covariance_is():
    # THE lesson of the project. 5 years of daily data, 300 independent histories of the same market.
    mus, covs = [], []
    for seed in range(300):
        p = simulate_market(MU, COV, n_days=252 * 5, seed=seed)
        mu_hat, cov_hat = annualised_mean_cov(p.pct_change().dropna())
        mus.append(mu_hat)
        covs.append(cov_hat)
    mus, covs = np.array(mus), np.array(covs)
    # spread of mu_hat across histories ~ sigma / sqrt(5 years): same order as mu itself!
    np.testing.assert_allclose(mus.std(axis=0), VOL / np.sqrt(5), rtol=0.2)
    assert np.all(mus.std(axis=0) > 0.5 * MU)
    # the variances are estimated within a few percent
    rel = covs.std(axis=0)[range(3), range(3)] / np.diag(COV)
    assert np.all(rel < 0.10)
    # and the estimated standard error predicts the real spread
    se = mean_standard_error(simulate_market(MU, COV, 252 * 5, seed=999).pct_change().dropna())
    np.testing.assert_allclose(se, VOL / np.sqrt(5), rtol=0.2)
