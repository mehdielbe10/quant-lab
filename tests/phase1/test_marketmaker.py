"""P3 tests: a market maker facing uninformed clients, built from the order book + flow + fair price."""
import numpy as np

from quantlab.marketmaker import run_market_making
from quantlab.markov import birth_death_transition_matrix, absorption_analysis


def test_result_structure_and_reproducibility():
    r = run_market_making(20.0, 20.0, 2.0, half_spread=2, sigma=0.01, inventory_limit=10, seed=1)
    n = r["n_orders"]
    assert n > 0 and r["n_orders"] == r["n_fills"] + r["n_missed"]
    for key in ("times", "filled", "inventory", "cash", "fair"):
        assert len(r[key]) == n
    assert len(r["sides"]) == n
    r2 = run_market_making(20.0, 20.0, 2.0, half_spread=2, sigma=0.01, inventory_limit=10, seed=1)
    np.testing.assert_array_equal(r["inventory"], r2["inventory"])
    assert r["pnl"] == r2["pnl"]
    r3 = run_market_making(20.0, 20.0, 2.0, half_spread=2, sigma=0.01, inventory_limit=10, seed=2)
    assert not np.array_equal(r["times"], r3["times"])


def test_no_orders_gives_zero_pnl():
    r = run_market_making(0.0, 0.0, 5.0, half_spread=2, sigma=0.01, inventory_limit=5, seed=0)
    assert r["n_orders"] == 0 and r["pnl"] == 0.0


def test_inventory_moves_by_one_and_respects_the_limit():
    r = run_market_making(40.0, 40.0, 3.0, half_spread=1, sigma=0.01, inventory_limit=4, seed=2)
    inv = np.concatenate([[0], r["inventory"]])
    steps = np.diff(inv)
    assert np.all(np.abs(inv) <= 4)
    for k, side in enumerate(r["sides"]):
        expected = (-1 if side == "buy" else 1) if r["filled"][k] else 0
        assert steps[k] == expected


def test_with_no_volatility_every_fill_earns_exactly_the_half_spread():
    r = run_market_making(30.0, 30.0, 3.0, half_spread=3, sigma=0.0, inventory_limit=1000, tick=0.01, seed=3)
    assert r["n_missed"] == 0
    assert abs(r["pnl"] - r["n_fills"] * 3 * 0.01) < 1e-9
    steps = np.diff(np.concatenate([[0.0], r["cash"]]))
    for k, side in enumerate(r["sides"]):
        expected = 100.0 + 0.03 if side == "buy" else -(100.0 - 0.03)
        assert abs(steps[k] - expected) < 1e-9


def test_one_sided_flow_hits_the_inventory_limit():
    # only buyers: the market maker keeps selling until inventory = -L, then misses every order.
    r = run_market_making(50.0, 0.0, 10.0, half_spread=2, sigma=0.0, inventory_limit=5, seed=4)
    assert r["n_orders"] > 100
    assert r["n_fills"] == 5 and r["inventory"][-1] == -5
    assert r["n_missed"] == r["n_orders"] - 5


def test_against_uninformed_clients_the_expected_pnl_is_the_spread_earned():
    # The fair price is a martingale and the clients are blind to it: inventory carries risk but no expected loss.
    diffs = []
    for seed in range(300):
        r = run_market_making(20.0, 20.0, 1.0, half_spread=2, sigma=0.002, inventory_limit=30, seed=seed)
        diffs.append(r["pnl"] - r["n_fills"] * 2 * 0.01)
    diffs = np.array(diffs)
    assert abs(diffs.mean()) < 4 * diffs.std() / np.sqrt(len(diffs))
    assert diffs.std() > 0                                       # inventory risk is real


def test_the_full_engine_exits_inventory_bands_as_the_markov_chain_predicts():
    # Symmetric flow, no inventory limit in play: the number of orders before |inventory| = 3 has mean L^2 = 9.
    L = 3
    P = birth_death_transition_matrix(0.5, L)
    _, t = absorption_analysis(P, [0, 2 * L])
    exact = t[L - 1]
    exits = []
    for seed in range(300):
        r = run_market_making(60.0, 60.0, 1.0, half_spread=1, sigma=0.0, inventory_limit=1000, seed=seed)
        hit = np.where(np.abs(r["inventory"]) >= L)[0]
        assert len(hit) > 0
        exits.append(hit[0] + 1)
    exits = np.array(exits)
    assert abs(exits.mean() - exact) < 4 * exits.std() / np.sqrt(len(exits))
