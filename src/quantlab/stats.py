"""S2 / S6: Sharpe ratio statistics (S2) and data-snooping (S6)."""
from __future__ import annotations

import numpy as np


def sharpe_ratio(returns, periods_per_year: int = 252) -> float:
    """Annualised Sharpe ratio (risk-free rate = 0): mean / std * sqrt(periods_per_year).

    Use the sample standard deviation (ddof=1).
    """
    raise NotImplementedError


def bootstrap_sharpe_ci(returns, n_boot: int = 2000, alpha: float = 0.05,
                        periods_per_year: int = 252, seed: int | None = None) -> tuple[float, float]:
    """Percentile bootstrap confidence interval (1 - alpha) for the annualised Sharpe ratio.

    Resample the returns with replacement (i.i.d. bootstrap), n_boot times.
    Returns (lower, upper).
    """
    raise NotImplementedError


def expected_max_normal(n: int) -> float:
    """E[max of n i.i.d. standard normals], by numerical integration.

    Density of the max: n * phi(x) * Phi(x)**(n-1). Integrate x times that density
    (scipy.integrate.quad over a wide interval is enough).
    """
    raise NotImplementedError


def max_sharpe_of_random_strategies(n_strategies: int, n_obs: int, n_reps: int = 200,
                                    seed: int | None = None, periods_per_year: int = 252) -> float:
    """Data-snooping experiment.

    One repetition: draw n_strategies independent return series of n_obs i.i.d. N(0, 1)
    values (no skill at all), compute the annualised Sharpe of each, keep the best one.
    Return the average of that best Sharpe over n_reps repetitions.
    """
    raise NotImplementedError


def bonferroni_threshold(alpha: float, n_tests: int) -> float:
    """Per-test significance level that keeps the family-wise error rate at alpha."""
    raise NotImplementedError
