"""S2: what can (and cannot) be estimated from a finite history."""
from __future__ import annotations

import numpy as np


def annualised_mean_cov(returns, periods_per_year: int = 252):
    """Annualised sample mean vector and covariance matrix of periodic returns.

    returns: array or DataFrame of shape (n, p). Returns (mu_hat, cov_hat) with
    mu_hat = mean * periods_per_year and cov_hat = sample covariance (ddof=1) * periods_per_year.
    """
    raise NotImplementedError


def mean_standard_error(returns, periods_per_year: int = 252) -> np.ndarray:
    """Standard error of the ANNUALISED mean, for each asset (shape (p,)).

    The mean of n i.i.d. periodic returns has standard error std / sqrt(n); annualise it by
    multiplying by periods_per_year. (Equivalently: sigma_annual / sqrt(number of years).)
    """
    raise NotImplementedError
