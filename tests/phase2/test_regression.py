"""P4 tests: OLS from scratch (used to test whether order flow predicts price moves)."""
import numpy as np

from quantlab.regression import ols, vif


def test_ols_hand_computed_example():
    # x = 1..5, y = [2, 4, 5, 4, 5]  ->  intercept 2.2, slope 0.6, SSE 2.4, sigma^2 = 0.8
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([2.0, 4.0, 5.0, 4.0, 5.0])
    res = ols(x, y)
    np.testing.assert_allclose(res["beta"], [2.2, 0.6], atol=1e-10)
    np.testing.assert_allclose(res["se"], [np.sqrt(0.88), np.sqrt(0.08)], atol=1e-10)
    np.testing.assert_allclose(res["t"], [2.2 / np.sqrt(0.88), 0.6 / np.sqrt(0.08)], atol=1e-10)
    np.testing.assert_allclose(res["resid"], [-0.8, 0.6, 1.0, -0.6, -0.2], atol=1e-10)
    assert abs(res["r2"] - 0.6) < 1e-10
    assert res["df"] == 3


def test_ols_matches_numpy_lstsq():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 3))
    y = 1.0 + X @ np.array([0.5, -2.0, 1.0]) + rng.normal(size=200)
    res = ols(X, y)
    A = np.column_stack([np.ones(200), X])
    expected, *_ = np.linalg.lstsq(A, y, rcond=None)
    np.testing.assert_allclose(res["beta"], expected, atol=1e-8)


def test_ols_residuals_are_orthogonal_to_regressors():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(300, 2))
    y = rng.normal(size=300)
    res = ols(X, y)
    A = np.column_stack([np.ones(300), X])
    np.testing.assert_allclose(A.T @ res["resid"], 0.0, atol=1e-8)


def test_ols_recovers_true_parameters_within_standard_errors():
    rng = np.random.default_rng(2)
    n = 2000
    X = rng.normal(size=(n, 3))
    true = np.array([1.0, 2.0, -1.0, 0.5])
    y = true[0] + X @ true[1:] + rng.normal(scale=0.5, size=n)
    res = ols(X, y)
    assert np.all(np.abs(res["beta"] - true) < 4 * res["se"])
    assert res["r2"] > 0.9


def test_ols_without_intercept():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(100, 2))
    y = X @ np.array([1.0, 2.0]) + rng.normal(scale=0.1, size=100)
    res = ols(X, y, add_intercept=False)
    assert res["beta"].shape == (2,)
    assert res["df"] == 98
    expected, *_ = np.linalg.lstsq(X, y, rcond=None)
    np.testing.assert_allclose(res["beta"], expected, atol=1e-8)


def test_ols_standard_errors_are_calibrated():
    # About 95% of the time, the true slope must lie within 2 standard errors of the estimate.
    rng = np.random.default_rng(4)
    hits = 0
    reps = 400
    for _ in range(reps):
        x = rng.normal(size=50)
        y = 1.0 + 2.0 * x + rng.normal(size=50)
        res = ols(x, y)
        hits += abs(res["beta"][1] - 2.0) < 2 * res["se"][1]
    assert 0.90 < hits / reps < 0.99


def test_ols_t_stat_detects_a_real_effect_and_not_a_fake_one():
    rng = np.random.default_rng(5)
    n = 500
    x_real = rng.normal(size=n)
    x_noise = rng.normal(size=n)
    y = 0.5 * x_real + rng.normal(size=n)
    res = ols(np.column_stack([x_real, x_noise]), y)
    assert abs(res["t"][1]) > 5      # real effect (index 0 is the intercept)
    assert abs(res["t"][2]) < 3      # noise regressor


def test_vif_for_two_columns_is_one_over_one_minus_rho_squared():
    rng = np.random.default_rng(6)
    x1 = rng.normal(size=1000)
    x2 = 0.8 * x1 + 0.6 * rng.normal(size=1000)
    rho = np.corrcoef(x1, x2)[0, 1]
    out = vif(np.column_stack([x1, x2]))
    np.testing.assert_allclose(out, [1 / (1 - rho**2)] * 2, rtol=1e-8)


def test_vif_flags_collinearity():
    rng = np.random.default_rng(7)
    a = rng.normal(size=500)
    b = rng.normal(size=500)
    c = a + b + 0.01 * rng.normal(size=500)    # almost a linear combination of a and b
    out = vif(np.column_stack([a, b, c]))
    assert np.all(out > 100)
    out_indep = vif(rng.normal(size=(500, 3)))
    assert np.all(out_indep < 1.1)
