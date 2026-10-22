"""S4: mean-variance portfolio optimisation."""
from __future__ import annotations

import numpy as np


def min_variance_weights(cov) -> np.ndarray:
    """Minimum-variance weights with sum(w) = 1 and shorting allowed (closed form, Lagrange)."""
    raise NotImplementedError


def max_sharpe_weights(mu, cov, rf: float = 0.0) -> np.ndarray:
    """Maximum-Sharpe (tangency) weights, normalised so that sum(w) = 1, shorting allowed.

    Assume sum(inv(cov) @ (mu - rf)) > 0.
    """
    raise NotImplementedError


def long_only_min_variance(cov, max_weight: float = 1.0) -> np.ndarray:
    """Minimum-variance weights with sum(w) = 1 and 0 <= w_i <= max_weight (numerical, e.g. scipy.optimize.minimize)."""
    raise NotImplementedError


def shrink_covariance(sample_cov, delta: float) -> np.ndarray:
    """Shrink a covariance matrix toward a scaled identity.

    result = (1 - delta) * S + delta * (trace(S) / p) * I, where p is the number of assets.
    """
    raise NotImplementedError
