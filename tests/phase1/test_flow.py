"""P2 tests: Poisson client flow and merging event streams."""
import numpy as np

from quantlab.flow import poisson_arrival_times, merge_event_streams, generate_order_flow


def test_arrivals_are_sorted_inside_the_horizon_and_reproducible():
    t = poisson_arrival_times(10.0, 5.0, seed=1)
    assert np.all(np.diff(t) > 0) and t.min() > 0 and t.max() <= 5.0
    np.testing.assert_array_equal(t, poisson_arrival_times(10.0, 5.0, seed=1))
    assert not np.array_equal(t, poisson_arrival_times(10.0, 5.0, seed=2))


def test_zero_rate_gives_no_arrivals():
    assert len(poisson_arrival_times(0.0, 10.0, seed=0)) == 0


def test_count_is_poisson_mean_equals_variance_equals_rate_times_horizon():
    lam, T = 4.0, 5.0
    counts = np.array([len(poisson_arrival_times(lam, T, seed=s)) for s in range(1500)])
    se_mean = np.sqrt(lam * T / len(counts))
    assert abs(counts.mean() - lam * T) < 4 * se_mean
    assert abs(counts.var() / (lam * T) - 1) < 0.15           # Poisson: variance = mean


def test_waiting_times_are_exponential_and_memoryless():
    lam = 3.0
    t = poisson_arrival_times(lam, 20_000.0, seed=3)
    w = np.diff(t)
    n = len(w)
    assert abs(w.mean() - 1 / lam) < 4 * (1 / lam) / np.sqrt(n)
    assert abs(w.std() / (1 / lam) - 1) < 0.02                 # exponential: std = mean
    # memorylessness: P(W > s + u | W > s) = P(W > u)
    s, u = 0.4, 0.3
    cond = np.mean(w[w > s] > s + u)
    assert abs(cond - np.exp(-lam * u)) < 4 * np.sqrt(0.25 / (w > s).sum())
    assert abs(np.mean(w > u) - np.exp(-lam * u)) < 4 * np.sqrt(0.25 / n)


def test_merge_event_streams_hand_example_with_ties():
    out = merge_event_streams({"a": np.array([1.0, 3.0, 5.0]), "b": np.array([2.0, 3.0]), "c": np.array([])})
    assert out == [(1.0, "a"), (2.0, "b"), (3.0, "a"), (3.0, "b"), (5.0, "a")]


def test_merge_event_streams_is_chronological_and_complete():
    rng = np.random.default_rng(0)
    streams = {k: np.sort(rng.random(n)) for k, n in (("x", 500), ("y", 300), ("z", 200))}
    out = merge_event_streams(streams)
    times = [t for t, _ in out]
    assert times == sorted(times) and len(out) == 1000
    for k in streams:
        np.testing.assert_allclose([t for t, lab in out if lab == k], streams[k])


def test_order_flow_basic_properties():
    flow = generate_order_flow(5.0, 3.0, 10.0, seed=4)
    times = [t for t, _ in flow]
    assert times == sorted(times) and 0 < times[0] and times[-1] <= 10.0
    assert {s for _, s in flow} == {"buy", "sell"}
    assert flow == generate_order_flow(5.0, 3.0, 10.0, seed=4)


def test_order_flow_next_event_is_a_buy_with_probability_lb_over_lb_plus_ls():
    # The result you derived on paper: P(next event is a buy) = lam_b / (lam_b + lam_s).
    lb, ls = 30.0, 10.0
    flow = generate_order_flow(lb, ls, 300.0, seed=5)
    n = len(flow)
    frac = np.mean([s == "buy" for _, s in flow])
    assert abs(n - (lb + ls) * 300.0) < 4 * np.sqrt((lb + ls) * 300.0)
    assert abs(frac - lb / (lb + ls)) < 4 * np.sqrt(0.75 * 0.25 / n)


def test_order_flow_with_a_zero_rate_side():
    flow = generate_order_flow(8.0, 0.0, 5.0, seed=6)
    assert len(flow) > 0 and all(s == "buy" for _, s in flow)
