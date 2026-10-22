"""P0 tests: the fair price (GBM) and its validation (Black-Scholes, Monte Carlo)."""
import numpy as np
import pytest

from quantlab.simulation import simulate_gbm, simulate_gbm_at_times, bs_call, mc_call_price

S0, K, R, SIGMA, T = 100.0, 100.0, 0.05, 0.20, 1.0


def test_gbm_shape_and_start():
    paths = simulate_gbm(100.0, 0.05, 0.2, 1.0, n_steps=10, n_paths=7, seed=0)
    assert paths.shape == (7, 11)
    assert np.all(paths[:, 0] == 100.0)
    assert np.all(paths > 0)


def test_gbm_is_reproducible():
    a = simulate_gbm(100.0, 0.05, 0.2, 1.0, 5, 100, seed=42)
    b = simulate_gbm(100.0, 0.05, 0.2, 1.0, 5, 100, seed=42)
    c = simulate_gbm(100.0, 0.05, 0.2, 1.0, 5, 100, seed=43)
    np.testing.assert_array_equal(a, b)
    assert not np.array_equal(a, c)


def test_gbm_mean_and_variance_of_terminal_value():
    # E[S_T] = s0 e^{mu T};  Var[S_T] = s0^2 e^{2 mu T} (e^{sigma^2 T} - 1)
    mu, sigma, T_ = 0.08, 0.20, 1.0
    n = 200_000
    s_T = simulate_gbm(100.0, mu, sigma, T_, n_steps=4, n_paths=n, seed=1)[:, -1]
    mean_th = 100.0 * np.exp(mu * T_)
    var_th = 100.0**2 * np.exp(2 * mu * T_) * (np.exp(sigma**2 * T_) - 1)
    se_mean = s_T.std() / np.sqrt(n)
    assert abs(s_T.mean() - mean_th) < 4 * se_mean
    assert abs(s_T.var() / var_th - 1) < 0.03


def test_gbm_log_return_has_ito_drift():
    # ln(S_T / s0) ~ N((mu - sigma^2/2) T, sigma^2 T). The -sigma^2/2 is the Ito correction.
    mu, sigma, T_ = 0.30, 0.40, 1.0
    n = 200_000
    s_T = simulate_gbm(100.0, mu, sigma, T_, n_steps=1, n_paths=n, seed=2)[:, -1]
    log_ret = np.log(s_T / 100.0)
    expected = (mu - 0.5 * sigma**2) * T_
    assert abs(log_ret.mean() - expected) < 4 * sigma * np.sqrt(T_) / np.sqrt(n)
    assert abs(log_ret.std() / (sigma * np.sqrt(T_)) - 1) < 0.01


def test_gbm_is_exact_whatever_the_number_of_steps():
    # With the exact scheme, the law of S_T does not depend on n_steps.
    n = 100_000
    a = simulate_gbm(100.0, 0.05, 0.3, 2.0, n_steps=1, n_paths=n, seed=5)[:, -1]
    b = simulate_gbm(100.0, 0.05, 0.3, 2.0, n_steps=50, n_paths=n, seed=6)[:, -1]
    assert abs(np.log(a).mean() - np.log(b).mean()) < 0.01
    assert abs(np.log(a).std() - np.log(b).std()) < 0.01


def test_bs_call_known_value():
    assert abs(bs_call(S0, K, R, SIGMA, T) - 10.4506) < 1e-4


def test_bs_call_limits_and_monotonicity():
    # Deep in the money with r = 0: call is worth about s0 - k.
    assert abs(bs_call(1000.0, 100.0, 0.0, 0.2, 1.0) - 900.0) < 1e-6
    # Far out of the money: worth about 0.
    assert bs_call(50.0, 100.0, 0.0, 0.2, 0.25) < 1e-6
    # A call is worth more when volatility is higher.
    assert bs_call(S0, K, R, 0.30, T) > bs_call(S0, K, R, 0.20, T)


def test_mc_price_is_within_four_standard_errors_of_bs():
    price, se = mc_call_price(S0, K, R, SIGMA, T, n_paths=200_000, seed=3)
    assert se > 0
    assert abs(price - bs_call(S0, K, R, SIGMA, T)) < 4 * se


def test_mc_standard_error_decays_like_one_over_sqrt_n():
    _, se_small = mc_call_price(S0, K, R, SIGMA, T, n_paths=50_000, seed=4)
    _, se_big = mc_call_price(S0, K, R, SIGMA, T, n_paths=200_000, seed=4)
    # 4x more paths -> standard error divided by 2.
    assert 0.45 < se_big / se_small < 0.55


def test_antithetic_variates_reduce_the_standard_error():
    p0, se_plain = mc_call_price(S0, K, R, SIGMA, T, n_paths=100_000, seed=7, antithetic=False)
    p1, se_anti = mc_call_price(S0, K, R, SIGMA, T, n_paths=100_000, seed=7, antithetic=True)
    assert se_anti < 0.8 * se_plain
    assert abs(p1 - bs_call(S0, K, R, SIGMA, T)) < 4 * se_anti


def test_antithetic_requires_an_even_number_of_paths():
    with pytest.raises(ValueError):
        mc_call_price(S0, K, R, SIGMA, T, n_paths=1001, seed=0, antithetic=True)




# ---- GBM on an irregular time grid (event times of the order flow) ------------------------------
def test_gbm_at_times_shape_and_reproducibility():
    times = np.array([0.1, 0.15, 0.4, 1.0])
    p = simulate_gbm_at_times(100.0, 0.0, 0.2, times, n_paths=5, seed=1)
    assert p.shape == (5, 4)
    assert np.all(p > 0)
    np.testing.assert_array_equal(p, simulate_gbm_at_times(100.0, 0.0, 0.2, times, n_paths=5, seed=1))


def test_gbm_at_times_has_exact_increments_for_unequal_steps():
    # log(S_t2 / S_t1) ~ N((mu - sigma^2/2) dt, sigma^2 dt) with dt = t2 - t1, whatever the grid.
    mu, sigma = 0.10, 0.30
    times = np.array([0.02, 0.5, 0.53])
    n = 200_000
    p = simulate_gbm_at_times(100.0, mu, sigma, times, n_paths=n, seed=2)
    first = np.log(p[:, 0] / 100.0)                      # dt = 0.02
    mid = np.log(p[:, 1] / p[:, 0])                      # dt = 0.48
    last = np.log(p[:, 2] / p[:, 1])                     # dt = 0.03
    for x, dt in ((first, 0.02), (mid, 0.48), (last, 0.03)):
        assert abs(x.mean() - (mu - 0.5 * sigma**2) * dt) < 4 * sigma * np.sqrt(dt) / np.sqrt(n)
        assert abs(x.std() / (sigma * np.sqrt(dt)) - 1) < 0.01
    # increments over disjoint intervals are independent
    assert abs(np.corrcoef(first, mid)[0, 1]) < 4 / np.sqrt(n)


def test_gbm_at_times_with_zero_volatility_is_deterministic():
    times = np.array([0.5, 1.0, 2.0])
    p = simulate_gbm_at_times(100.0, 0.05, 0.0, times, seed=0)[0]
    np.testing.assert_allclose(p, 100.0 * np.exp(0.05 * times))


def test_gbm_at_times_rejects_bad_times():
    with pytest.raises(ValueError):
        simulate_gbm_at_times(100.0, 0.0, 0.2, np.array([0.5, 0.4]))
    with pytest.raises(ValueError):
        simulate_gbm_at_times(100.0, 0.0, 0.2, np.array([0.0, 0.4]))
