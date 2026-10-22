"""P1: a limit order book with price-time priority.

Prices are INTEGERS (ticks) and quantities are positive INTEGERS. Sides are the strings "buy" and "sell".
A "buy" order trades against the asks (sell orders), a "sell" order against the bids.

Rules to implement
  * Price priority: the best price is matched first (highest bid, lowest ask).
  * Time priority: at the same price, the order that arrived first is matched first.
  * A trade happens at the price of the RESTING order (the "maker"), not at the incoming order's limit.
  * add_limit_order: first match what is marketable (a buy limit order is marketable against asks priced
    <= its limit; a sell limit order against bids priced >= its limit), then whatever is left rests in the book.
  * add_market_order: match against the book as far as possible; any unfilled remainder is discarded.
  * cancel: removes a resting order. Cancelling an order that is not resting (unknown id, already filled,
    already cancelled) returns False.
  * The book is never crossed: after any operation, best_bid < best_ask (when both exist).

Complexity target: O(log n) per resting order and O(1) amortised cancel (hint: a heap per side, a dict of
live orders, and "lazy deletion": do not remove a cancelled order from the heap, skip it when it reaches the top).
"""
from __future__ import annotations


class OrderBook:
    def __init__(self) -> None:
        """Create an empty book. The first order id is 1, then 2, 3, ... (shared by buy and sell orders)."""
        raise NotImplementedError

    def add_limit_order(self, side: str, price: int, qty: int) -> tuple[int, list[tuple[int, int, int]]]:
        """Submit a limit order. Returns (order_id, fills).

        fills is a list of (price, quantity, maker_order_id) in execution order.
        The order gets an id even if it is filled immediately and never rests.
        Raise ValueError if side is not "buy"/"sell" or qty is not a positive integer.
        """
        raise NotImplementedError

    def add_market_order(self, side: str, qty: int) -> list[tuple[int, int, int]]:
        """Submit a market order. Returns fills (same format). The unfilled remainder is dropped.
        Raise ValueError for an invalid side or qty."""
        raise NotImplementedError

    def cancel(self, order_id: int) -> bool:
        """Cancel a resting order. True if it was resting, False otherwise."""
        raise NotImplementedError

    def best_bid(self) -> int | None:
        """Highest resting buy price, or None."""
        raise NotImplementedError

    def best_ask(self) -> int | None:
        """Lowest resting sell price, or None."""
        raise NotImplementedError

    def mid_price(self) -> float | None:
        """(best_bid + best_ask) / 2, or None if one side is empty."""
        raise NotImplementedError

    def spread(self) -> int | None:
        """best_ask - best_bid, or None if one side is empty."""
        raise NotImplementedError

    def resting_quantity(self, side: str) -> int:
        """Total quantity currently resting on that side (any complexity is fine, used for checks)."""
        raise NotImplementedError

    def quantity_at(self, side: str, price: int) -> int:
        """Total quantity resting at that side and price (any complexity is fine)."""
        raise NotImplementedError

    def order_remaining(self, order_id: int) -> int:
        """Remaining quantity of a resting order, 0 if it is not resting."""
        raise NotImplementedError
