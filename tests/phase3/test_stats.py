"""Phase 3 tests: Sharpe ratio, bootstrap, data-snooping."""
import numpy as np
import pytest

from quantlab.stats import (sharpe_ratio, bootstrap_sharpe_ci, expected_max_normal,
                            max_sharpe_of_random_strategies, bonferroni_threshold)


def test_sharpe_hand_computed():
    r = np.array([0.01, -0.01, 0.02, 0.0])
    # mean = 0.005, sum of squared deviations = 5e-4, sample variance = 5e-4 / 3
    expected = 0.005 / np.sqrt(5e-4 / 3) * np.sqrt(252)
    assert abs(sharpe_ratio(r) - expected) < 1e-9


def test_sharpe_annualisation_factor():
    r = np.array([0.01, -0.01, 0.02, 0.0])
    ratio = sharpe_ratio(r, periods_per_year=252) / sharpe_ratio(r, periods_per_year=12)
    assert abs(ratio - np.sqrt(252 / 12)) < 1e-9


def test_sharpe_is_invariant_to_leverage():
    rng = np.random.default_rng(0)
    r = rng.normal(0.0005, 0.01, 500)
    assert abs(sharpe_ratio(r) - sharpe_ratio(3.0 * r)) < 1e-9


def test_bootstrap_ci_basic_properties():
    rng = np.random.default_rng(1)
    r = rng.normal(0.0005, 0.01, 750)
    lo, hi = bootstrap_sharpe_ci(r, n_boot=1000, seed=0)
    assert lo < sharpe_ratio(r) < hi


def test_bootstrap_ci_is_reproducible_with_seed():
    rng = np.random.default_rng(2)
    r = rng.normal(0.0005, 0.01, 300)
    assert bootstrap_sharpe_ci(r, n_boot=500, seed=5) == bootstrap_sharpe_ci(r, n_boot=500, seed=5)


def test_bootstrap_ci_shrinks_with_more_data():
    rng = np.random.default_rng(3)
    short = rng.normal(0.0005, 0.01, 250)
    long = rng.normal(0.0005, 0.01, 2500)
    lo_s, hi_s = bootstrap_sharpe_ci(short, n_boot=1000, seed=0)
    lo_l, hi_l = bootstrap_sharpe_ci(long, n_boot=1000, seed=0)
    assert (hi_l - lo_l) < 0.6 * (hi_s - lo_s)


def test_bootstrap_ci_width_is_about_right():
    # For i.i.d. data, SE(annualised Sharpe) ~ sqrt(periods/n) when the true Sharpe is small.
    rng = np.random.default_rng(4)
    r = rng.normal(0.0, 0.01, 1000)
    lo, hi = bootstrap_sharpe_ci(r, n_boot=2000, alpha=0.05, seed=1)
    approx_width = 2 * 1.96 * np.sqrt(252 / 1000)
    assert 0.8 * approx_width < (hi - lo) < 1.2 * approx_width


def test_expected_max_normal_known_values():
    assert abs(expected_max_normal(1) - 0.0) < 1e-6
    assert abs(expected_max_normal(2) - 1 / np.sqrt(np.pi)) < 1e-6   # 0.56419
    assert abs(expected_max_normal(10) - 1.53875) < 1e-4
    assert abs(expected_max_normal(100) - 2.50759) < 1e-4


def test_expected_max_normal_is_increasing_and_grows_slowly():
    values = [expected_max_normal(n) for n in (1, 2, 10, 100, 1000)]
    assert all(a < b for a, b in zip(values, values[1:]))
    # Growth is about sqrt(2 ln n): far slower than n.
    assert values[-1] < 4.0


def test_data_snooping_one_strategy_has_no_edge():
    avg = max_sharpe_of_random_strategies(1, 252, n_reps=300, seed=0)
    assert abs(avg) < 0.3


def test_data_snooping_best_of_many_looks_great():
    avg100 = max_sharpe_of_random_strategies(100, 252, n_reps=200, seed=1)
    avg10 = max_sharpe_of_random_strategies(10, 252, n_reps=200, seed=1)
    assert avg10 < avg100
    # One year of daily data: Sharpe of a no-skill series is ~ N(0, 1), so the best of 100 ~ 2.5.
    assert abs(avg100 - expected_max_normal(100)) < 0.2
    assert avg100 > 2.0   # "a Sharpe above 2" found in pure noise


def test_bonferroni():
    assert abs(bonferroni_threshold(0.05, 10) - 0.005) < 1e-12
    assert abs(bonferroni_threshold(0.05, 1) - 0.05) < 1e-12
