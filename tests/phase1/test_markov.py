"""P3 tests: inventory as a Markov chain (absorbing chains, first-step analysis)."""
import numpy as np

from quantlab.markov import birth_death_transition_matrix, absorption_analysis, simulate_inventory_exit


def test_transition_matrix_structure():
    P = birth_death_transition_matrix(0.6, 2)
    assert P.shape == (5, 5)
    np.testing.assert_allclose(P.sum(axis=1), 1.0)
    np.testing.assert_allclose(P[0], [1, 0, 0, 0, 0])
    np.testing.assert_allclose(P[4], [0, 0, 0, 0, 1])
    np.testing.assert_allclose(P[2], [0, 0.4, 0, 0.6, 0])


def test_absorption_analysis_hand_example():
    # Chain on {0, 1, 2}: 0 and 2 absorbing, from 1 go to either with probability 1/2.
    P = np.array([[1, 0, 0], [0.5, 0, 0.5], [0, 0, 1]])
    B, t = absorption_analysis(P, [0, 2])
    np.testing.assert_allclose(B, [[0.5, 0.5]])
    np.testing.assert_allclose(t, [1.0])


def test_symmetric_gambler_ruin_probabilities_and_times():
    # inventories -2..2, start at x: P(exit at +L) = (x + L) / (2 L), E[steps] = L^2 - x^2.
    P = birth_death_transition_matrix(0.5, 2)
    B, t = absorption_analysis(P, [0, 4])
    # transient states are inventories -1, 0, 1
    np.testing.assert_allclose(B[:, 1], [0.25, 0.5, 0.75])
    np.testing.assert_allclose(t, [3.0, 4.0, 3.0])


def test_asymmetric_gambler_ruin_matches_the_closed_form():
    p, L = 0.6, 3
    P = birth_death_transition_matrix(p, L)
    B, t = absorption_analysis(P, [0, 2 * L])
    r = (1 - p) / p
    N = 2 * L
    for idx, i in enumerate(range(1, N)):                      # i = inventory + L
        up = (1 - r**i) / (1 - r**N)
        steps = i / ((1 - p) - p) - (N / ((1 - p) - p)) * up
        assert abs(B[idx, 1] - up) < 1e-10
        assert abs(B[idx, 0] - (1 - up)) < 1e-10
        assert abs(t[idx] - steps) < 1e-9


def test_monte_carlo_agrees_with_the_exact_analysis():
    for p, L in ((0.5, 3), (0.6, 2)):
        P = birth_death_transition_matrix(p, L)
        B, t = absorption_analysis(P, [0, 2 * L])
        exact_up, exact_t = B[L - 1, 1], t[L - 1]               # start at inventory 0
        n = 40_000
        up, mean_steps = simulate_inventory_exit(p, L, n, seed=1)
        assert abs(up - exact_up) < 4 * np.sqrt(exact_up * (1 - exact_up) / n)
        assert abs(mean_steps / exact_t - 1) < 0.03
