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
import heapq

class OrderBook:
    def __init__(self) -> None:
        """Create an empty book. The first order id is 1, then 2, 3, ... (shared by buy and sell orders)."""
        self.bids = []
        self.asks = []
        self.dict_orders = {}
        self.count = 0

    def _apparier(self, side, qty, limite):
        fills = []
        reste = qty
        if side == "sell":
            tas = self.bids
            methode = self.best_bid
            signe = -1
        else:
            tas = self.asks
            methode = self.best_ask
            signe = +1

        while reste > 0 and methode() is not None:
            id_order = tas[0][1]
            qty_order = self.dict_orders[id_order][2]
            price_order = signe * tas[0][0]
            if (side == "buy" and price_order > limite
                ) or (side == "sell" and price_order < limite):
                break
            echange = min(reste, qty_order)
            fills.append((price_order, echange, id_order))
            reste = reste - echange
            if echange == qty_order:
                del(self.dict_orders[id_order])
            else: 
                self.dict_orders[id_order][2] -= echange
        return fills     
            
        
        


    def add_limit_order(self, side: str, price: int, qty: int) -> tuple[int, list[tuple[int, int, int]]]:
        """Submit a limit order. Returns (order_id, fills).

        fills is a list of (price, quantity, maker_order_id) in execution order.
        The order gets an id even if it is filled immediately and never rests.
        Raise ValueError if side is not "buy"/"sell" or qty is not a positive integer.
        """
        if not (side == "buy" or side == "sell"):
            raise ValueError
        elif not isinstance(qty, int) or qty <= 0:
            raise ValueError

        self.count += 1
        fills = self._apparier(side, qty, price)
        reste = qty - sum(q for _, q, _ in fills)
        if reste > 0:
            self.dict_orders[self.count] = [side, price, reste]
            if side == "sell":
                heapq.heappush(self.asks, (price, self.count))
            
            else:
                heapq.heappush(self.bids, (-price, self.count))
        return (self.count, fills)


    def add_market_order(self, side: str, qty: int) -> list[tuple[int, int, int]]:
        """Submit a market order. Returns fills (same format). The unfilled remainder is dropped.
        Raise ValueError for an invalid side or qty."""
        if not (side == "buy" or side == "sell"):
            raise ValueError
        elif not isinstance(qty, int) or qty <= 0:
            raise ValueError
        if side == "buy":
            limite = float("inf")
        else:
            limite = - float("inf")
        return self._apparier(side, qty, limite)
    

    def cancel(self, order_id: int) -> bool:
        """Cancel a resting order. True if it was resting, False otherwise."""
        if order_id in self.dict_orders:
            del self.dict_orders[order_id]
            return True
        return False


    def best_bid(self) -> int | None:
        """Highest resting buy price, or None."""
        while self.bids and self.bids[0][1] not in self.dict_orders:        
            heapq.heappop(self.bids) 
        if not self.bids:
            return None
        return -self.bids[0][0]

    def best_ask(self) -> int | None:
        """Lowest resting sell price, or None."""
        while self.asks and self.asks[0][1] not in self.dict_orders:        
            heapq.heappop(self.asks) 
        if not self.asks:
            return None
        return self.asks[0][0]
        

    def mid_price(self) -> float | None:
        """(best_bid + best_ask) / 2, or None if one side is empty."""
        if self.best_bid() == None or self.best_ask() == None:
            return None
        return (self.best_ask() + self.best_bid())/2
        

    def spread(self) -> int | None:
        """best_ask - best_bid, or None if one side is empty."""
        if self.best_bid() == None or self.best_ask() == None:
            return None
        return self.best_ask() - self.best_bid()
        

    def resting_quantity(self, side: str) -> int:
        """Total quantity currently resting on that side (any complexity is fine, used for checks)."""
        total = 0
        for ordre in self.dict_orders.values():
            if ordre[0] == side:
                total += ordre[2]
        return total
        

    def quantity_at(self, side: str, price: int) -> int:
        """Total quantity resting at that side and price (any complexity is fine)."""
        total = 0
        for ordre in self.dict_orders.values():
            if ordre[0] == side and ordre[1] == price:
                total += ordre[2]
        return total

    def order_remaining(self, order_id: int) -> int:
        """Remaining quantity of a resting order, 0 if it is not resting."""
        if order_id in self.dict_orders:
            return self.dict_orders[order_id][2]
        return 0
        