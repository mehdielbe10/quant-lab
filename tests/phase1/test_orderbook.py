"""P1 tests: the limit order book (price-time priority, cancel, no crossed book)."""
import time

import numpy as np
import pytest

from quantlab.orderbook import OrderBook


def test_empty_book():
    b = OrderBook()
    assert b.best_bid() is None and b.best_ask() is None
    assert b.mid_price() is None and b.spread() is None


def test_resting_orders_best_prices_mid_and_spread():
    b = OrderBook()
    id1, f1 = b.add_limit_order("buy", 99, 5)
    id2, f2 = b.add_limit_order("buy", 100, 3)
    id3, f3 = b.add_limit_order("sell", 103, 4)
    id4, f4 = b.add_limit_order("sell", 102, 2)
    assert (id1, id2, id3, id4) == (1, 2, 3, 4)
    assert f1 == f2 == f3 == f4 == []
    assert b.best_bid() == 100 and b.best_ask() == 102
    assert b.mid_price() == 101.0 and b.spread() == 2


def test_market_order_trades_at_the_resting_price():
    b = OrderBook()
    oid, _ = b.add_limit_order("sell", 101, 5)
    fills = b.add_market_order("buy", 2)
    assert fills == [(101, 2, oid)]
    assert b.order_remaining(oid) == 3
    assert b.quantity_at("sell", 101) == 3


def test_price_priority_best_price_first():
    b = OrderBook()
    a102, _ = b.add_limit_order("sell", 102, 1)
    a101, _ = b.add_limit_order("sell", 101, 1)
    fills = b.add_market_order("buy", 2)
    assert fills == [(101, 1, a101), (102, 1, a102)]
    b = OrderBook()
    l99, _ = b.add_limit_order("buy", 99, 1)
    l100, _ = b.add_limit_order("buy", 100, 1)
    assert b.add_market_order("sell", 2) == [(100, 1, l100), (99, 1, l99)]


def test_time_priority_same_price_first_come_first_served():
    b = OrderBook()
    first, _ = b.add_limit_order("sell", 101, 1)
    second, _ = b.add_limit_order("sell", 101, 1)
    assert b.add_market_order("buy", 1) == [(101, 1, first)]
    assert b.add_market_order("buy", 1) == [(101, 1, second)]


def test_partially_filled_order_keeps_its_place_in_the_queue():
    b = OrderBook()
    first, _ = b.add_limit_order("sell", 101, 3)
    second, _ = b.add_limit_order("sell", 101, 3)
    assert b.add_market_order("buy", 1) == [(101, 1, first)]
    assert b.add_market_order("buy", 3) == [(101, 2, first), (101, 1, second)]
    assert b.order_remaining(first) == 0 and b.order_remaining(second) == 2


def test_market_order_larger_than_the_book_discards_the_rest():
    b = OrderBook()
    b.add_limit_order("sell", 101, 2)
    b.add_limit_order("sell", 102, 1)
    fills = b.add_market_order("buy", 10)
    assert sum(q for _, q, _ in fills) == 3
    assert b.best_ask() is None
    assert b.best_bid() is None                 # the unfilled remainder did NOT rest


def test_marketable_limit_order_trades_then_rests():
    b = OrderBook()
    a101, _ = b.add_limit_order("sell", 101, 1)
    b.add_limit_order("sell", 103, 5)
    oid, fills = b.add_limit_order("buy", 102, 3)
    assert fills == [(101, 1, a101)]            # trades at the RESTING price, not at 102
    assert b.best_bid() == 102                  # remainder rests
    assert b.order_remaining(oid) == 2
    assert b.best_ask() == 103


def test_non_marketable_limit_order_just_rests():
    b = OrderBook()
    b.add_limit_order("sell", 101, 1)
    oid, fills = b.add_limit_order("buy", 100, 2)
    assert fills == [] and b.best_bid() == 100 and b.order_remaining(oid) == 2


def test_fully_filled_limit_order_gets_an_id_but_does_not_rest():
    b = OrderBook()
    b.add_limit_order("sell", 101, 5)
    oid, fills = b.add_limit_order("buy", 101, 2)
    assert oid == 2 and fills == [(101, 2, 1)]
    assert b.best_bid() is None and b.order_remaining(oid) == 0


def test_cancel():
    b = OrderBook()
    o1, _ = b.add_limit_order("buy", 100, 1)
    o2, _ = b.add_limit_order("buy", 99, 1)
    assert b.cancel(o1) is True
    assert b.best_bid() == 99                   # the cancelled order must not be reported as the best bid
    assert b.cancel(o1) is False                # already cancelled
    assert b.cancel(12345) is False             # unknown
    assert b.order_remaining(o1) == 0 and b.order_remaining(o2) == 1


def test_cancelled_order_is_never_filled():
    b = OrderBook()
    first, _ = b.add_limit_order("sell", 101, 1)
    second, _ = b.add_limit_order("sell", 101, 1)
    b.cancel(first)
    assert b.add_market_order("buy", 1) == [(101, 1, second)]


def test_cannot_cancel_an_order_that_was_filled():
    b = OrderBook()
    oid, _ = b.add_limit_order("sell", 101, 1)
    b.add_market_order("buy", 1)
    assert b.cancel(oid) is False


def test_quantities():
    b = OrderBook()
    b.add_limit_order("buy", 100, 2)
    b.add_limit_order("buy", 100, 3)
    b.add_limit_order("buy", 99, 4)
    b.add_limit_order("sell", 105, 7)
    assert b.quantity_at("buy", 100) == 5
    assert b.resting_quantity("buy") == 9 and b.resting_quantity("sell") == 7
    assert b.quantity_at("sell", 100) == 0


def test_invalid_orders_raise():
    b = OrderBook()
    with pytest.raises(ValueError):
        b.add_limit_order("hold", 100, 1)
    with pytest.raises(ValueError):
        b.add_limit_order("buy", 100, 0)
    with pytest.raises(ValueError):
        b.add_market_order("sell", -3)


def test_random_stress_invariants():
    rng = np.random.default_rng(0)
    b = OrderBook()
    live = []
    rested = cancelled = maker_filled = 0
    for _ in range(3000):
        r = rng.random()
        if r < 0.55:
            side = "buy" if rng.random() < 0.5 else "sell"
            price = int(rng.integers(95, 106))
            qty = int(rng.integers(1, 6))
            oid, fills = b.add_limit_order(side, price, qty)
            taken = sum(q for _, q, _ in fills)
            for p, q, _ in fills:               # limit respected, executed at maker price
                assert (p <= price) if side == "buy" else (p >= price)
            prices = [p for p, _, _ in fills]
            assert prices == sorted(prices) if side == "buy" else prices == sorted(prices, reverse=True)
            maker_filled += taken
            rested += qty - taken
            if qty - taken:
                live.append(oid)
        elif r < 0.80:
            side = "buy" if rng.random() < 0.5 else "sell"
            fills = b.add_market_order(side, int(rng.integers(1, 6)))
            maker_filled += sum(q for _, q, _ in fills)
        elif live:
            oid = live.pop(int(rng.integers(len(live))))
            rem = b.order_remaining(oid)
            if b.cancel(oid):
                cancelled += rem
        bb, ba = b.best_bid(), b.best_ask()
        if bb is not None and ba is not None:
            assert bb < ba                      # the book is never crossed
        total = b.resting_quantity("buy") + b.resting_quantity("sell")
        assert total == rested - cancelled - maker_filled      # quantity is conserved


def test_it_is_fast_enough_for_a_big_flow():
    # O(n) scans per operation would take minutes here; heaps + a dict take well under a second.
    rng = np.random.default_rng(1)
    b = OrderBook()
    ids = []
    t0 = time.time()
    for i in range(30_000):
        side = "buy" if i % 2 else "sell"
        price = 1000 - 5 - int(rng.integers(0, 50)) if side == "buy" else 1000 + 5 + int(rng.integers(0, 50))
        oid, _ = b.add_limit_order(side, price, 1)
        ids.append(oid)
    for oid in ids[::2]:
        b.cancel(oid)
    for _ in range(5_000):
        b.add_market_order("buy", 1)
        b.add_market_order("sell", 1)
        b.best_bid(); b.best_ask()
    assert time.time() - t0 < 8.0
