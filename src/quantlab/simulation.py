"""P0 / phase 3: the fair price process (GBM), its validation against Black-Scholes, and a correlated market."""
from __future__ import annotations

import numpy as np


def simulate_gbm(s0: float, mu: float, sigma: float, T: float,
                 n_steps: int, n_paths: int, seed: int | None = None) -> np.ndarray:
    """Simulate GBM paths with the EXACT discretisation (not Euler).

    Returns an array of shape (n_paths, n_steps + 1).
    Column 0 is s0, column j is the value at time j * T / n_steps.
    Use np.random.default_rng(seed) so results are reproducible.
    """
    raise NotImplementedError


def simulate_gbm_at_times(s0: float, mu: float, sigma: float, times, n_paths: int = 1,
                          seed: int | None = None) -> np.ndarray:
    """GBM observed at irregular times (the event times of the client order flow).

    times: strictly increasing positive times t_1 < t_2 < ... (time 0 has price s0).
    Returns an array of shape (n_paths, len(times)): the price at each time in `times`.
    The step between two observations is dt = t_k - t_{k-1} (t_0 = 0), and the EXACT scheme is
    used with that dt, so the law of the price does not depend on how often you look.
    Raise ValueError if times is not strictly increasing or its first value is <= 0.
    """
    raise NotImplementedError


def bs_call(s0: float, k: float, r: float, sigma: float, T: float) -> float:
    """Black-Scholes price of a European call (no dividends)."""
    raise NotImplementedError


def bs_delta(s0: float, k: float, r: float, sigma: float, T: float) -> float:
    """Black-Scholes delta of a European call: d(price)/d(s0)."""
    raise NotImplementedError


def mc_call_price(s0: float, k: float, r: float, sigma: float, T: float,
                  n_paths: int, seed: int | None = None,
                  antithetic: bool = False) -> tuple[float, float]:
    """Monte Carlo price of a European call and its standard error.

    - Simulate the terminal value S_T directly (one step) under the RISK-NEUTRAL drift r.
    - Return (price, standard_error). Both are discounted to today.
    - If antithetic=True: n_paths must be even (raise ValueError otherwise).
      Draw n_paths/2 normals Z and use their mirrors -Z, average the payoff of each pair,
      and compute the standard error from those n_paths/2 pair averages.
    """
    raise NotImplementedError


def simulate_market(mu, cov, n_days: int, seed: int | None = None, s0: float = 100.0,
                    ar1: float = 0.0, periods_per_year: int = 252, names=None):
    """Simulate ONE history of a market of p correlated assets. This is the laboratory (stage S1).

    mu, cov: TRUE annual expected returns (shape (p,)) and annual covariance matrix (p, p).
    Returns a pandas DataFrame of prices with n_days + 1 rows (row 0 = s0 for every asset),
    a business-day DatetimeIndex (use pd.bdate_range("2015-01-05", periods=n_days + 1)),
    and one column per asset (names if given, else "A1", "A2", ...).

    Method (dt = 1 / periods_per_year, L = np.linalg.cholesky(cov)):
      - draw independent standard normals z_t (shape (n_days, p)) and form the correlated
        shocks e_t = sqrt(dt) * L @ z_t, whose covariance is cov * dt;
      - log-return of day t = (mu - diag(cov) / 2) * dt + e_t         (exact GBM, Ito correction);
      - if ar1 != 0, the shocks are autocorrelated: e_t = ar1 * e_{t-1} + sqrt(1 - ar1**2) * (sqrt(dt) * L @ z_t),
        starting from e_{-1} = sqrt(dt) * L @ (another standard normal draw).
        The variance of e_t is unchanged, only its autocorrelation (= ar1, per asset) changes.
        This gives the market a small, known predictability: a signal can really work in it.
      - prices = s0 * exp(cumulative sum of log-returns).
    Use np.random.default_rng(seed) so a history is reproducible.
    """
    raise NotImplementedError
