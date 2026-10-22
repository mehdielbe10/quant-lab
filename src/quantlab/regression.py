"""S3: linear regression from scratch (no statsmodels, no sklearn)."""
from __future__ import annotations

import numpy as np


def ols(X, y, add_intercept: bool = True) -> dict:
    """Ordinary least squares with classical standard errors.

    X: array of shape (n,) or (n, k). y: array of shape (n,).
    If add_intercept, a column of ones is added FIRST, so beta[0] is the intercept.

    Return a dict with keys:
      "beta":  estimated coefficients, shape (p,)
      "se":    standard errors, shape (p,)         (sigma2_hat * (X'X)^-1, sigma2_hat = SSE / (n - p))
      "t":     t statistics beta / se, shape (p,)
      "r2":    R squared (1 - SSE / SST)
      "resid": residuals, shape (n,)
      "df":    degrees of freedom n - p
    """
    raise NotImplementedError


def vif(X) -> np.ndarray:
    """Variance inflation factors, one per column of X (X has NO intercept column).

    VIF_j = 1 / (1 - R2_j), where R2_j is the R squared of regressing column j
    on all the other columns (with an intercept).
    """
    raise NotImplementedError
