"""The laboratory: a small market whose TRUE parameters you know.

This file is given to you (not an exercise). Every stage of the project uses the same lab,
so results from different stages can be compared.
"""
import numpy as np

LAB_NAMES = ["US_equity", "EU_equity", "EM_equity", "Bonds", "Gold", "Commodities"]
LAB_MU = np.array([0.07, 0.07, 0.08, 0.025, 0.03, 0.04])        # true annual expected returns
LAB_VOL = np.array([0.16, 0.18, 0.22, 0.06, 0.15, 0.20])        # true annual volatilities
LAB_CORR = np.array([
    [1.00, 0.80, 0.70, -0.20, 0.00, 0.40],
    [0.80, 1.00, 0.75, -0.15, 0.05, 0.40],
    [0.70, 0.75, 1.00, -0.10, 0.10, 0.45],
    [-0.20, -0.15, -0.10, 1.00, 0.20, -0.05],
    [0.00, 0.05, 0.10, 0.20, 1.00, 0.20],
    [0.40, 0.40, 0.45, -0.05, 0.20, 1.00],
])
LAB_COV = np.outer(LAB_VOL, LAB_VOL) * LAB_CORR                  # true annual covariance matrix


def lab_parameters():
    """Return (mu, cov, names): the true parameters of the lab market (annual units)."""
    return LAB_MU.copy(), LAB_COV.copy(), list(LAB_NAMES)
