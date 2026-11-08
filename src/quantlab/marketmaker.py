"""P3: a first market maker, wired to the order book, the client flow and the fair price."""
from __future__ import annotations
from quantlab.flow import generate_order_flow
from quantlab.simulation import simulate_gbm_at_times
from quantlab.orderbook import OrderBook
import numpy as np



def run_market_making(lam_buy: float, lam_sell: float, horizon: float, half_spread: int, sigma: float,
                      inventory_limit: int, s0: float = 100.0, tick: float = 0.01,
                      seed: int | None = None) -> dict:
    """Simulate a market maker facing UNINFORMED clients (clients do not know where the price is going).

    Ingredients (all yours from P0, P1, P2):
      - client market orders of size 1: generate_order_flow(lam_buy, lam_sell, horizon);
      - the fair price at each order time: simulate_gbm_at_times(s0, 0.0, sigma, times) (drift 0);
      - an OrderBook that holds the market maker's quotes.
    Prices in the book are integer ticks: price_in_ticks = round(price / tick). Time unit: 1 day;
    sigma is the daily volatility of the GBM (relative).

    Algorithm, for each client order k = 0, 1, 2, ... (V_{-1} = s0, V_k = fair price at the time of order k):
      1. cancel the market maker's old quotes (if still resting);
      2. center = round(V_{k-1} / tick). Post a bid of size 1 at center - half_spread, UNLESS inventory >= inventory_limit;
         post an ask of size 1 at center + half_spread, UNLESS inventory <= -inventory_limit
         (half_spread is an integer number of ticks);
      3. send the client's market order (size 1) to the book. A client "buy" hits the ask (the market maker SELLS:
         inventory -1, cash + price * tick); a client "sell" hits the bid (the market maker BUYS: inventory +1,
         cash - price * tick). If the needed quote is not there, the order is missed (nothing happens);
      4. record inventory and cash, then move on: the fair price becomes V_k.
    Inventory starts at 0 and cash at 0.

    Return a dict with keys:
      "times"     (n,) array of client order times
      "sides"     list of "buy"/"sell"
      "filled"    (n,) bool array: was the order executed?
      "inventory" (n,) int array: inventory AFTER each order
      "cash"      (n,) float array: cash AFTER each order
      "fair"      (n,) float array: V_k
      "pnl"       cash[-1] + inventory[-1] * fair[-1]   (0.0 if there are no orders)
      "n_orders", "n_fills", "n_missed"  (ints, n_orders = n_fills + n_missed)
    Same seed -> same result (derive separate seeds for the flow and the price from np.random.default_rng(seed)).
    """

    n_fills = 0
    n_missed = 0
    rng = np.random.default_rng(seed)
    graine_flux, graine_price = rng.integers(0, 2**31, size=2)
    flux = generate_order_flow(lam_buy, lam_sell, horizon, graine_flux)
    times = np.array([instants for instants, _ in flux])
    sides = [cotés for _, cotés in flux]
    n_orders = len(times)
    if n_orders == 0: 
      return {"times": np.array([]) , "sides": [],
               "filled": np.array([], dtype= bool),
                 "inventory": np.array([], dtype=int), "cash": np.array([]),
                   "fair": np.array([]), "pnl": 0.0, "n_orders": 0,
                     "n_fills": 0, "n_missed": 0}
    tableau = simulate_gbm_at_times(s0, 0.0, sigma, times, seed=graine_price)
    fair = tableau[0]

    carnet = OrderBook()
    stock = 0
    cash = 0.0
    prix_precedent = s0
    l_execute = []
    l_stock = []
    l_cash = []
    id_achat = None
    id_vente = None
    for k in range(n_orders):
      carnet.cancel(id_achat)
      carnet.cancel(id_vente)
      id_achat = None
      id_vente = None
      centre = round(prix_precedent / tick)
      if stock < inventory_limit:
         offre_achat = carnet.add_limit_order(side="buy", price= centre - half_spread, qty=1)
         id_achat, _ = offre_achat
      if stock > -inventory_limit:
         offre_vente = carnet.add_limit_order(side="sell", price= centre + half_spread, qty=1)
         id_vente, _ = offre_vente
      l = carnet.add_market_order(sides[k], 1)
      if l:
        price_ticks = l[0][0]
        price_e = price_ticks * tick
        if sides[k] == "buy":
          stock -= 1
          cash += price_e
        else: 
          stock += 1
          cash -= price_e
        n_fills += 1
        execute = True
      else:
        n_missed += 1
        execute = False
      l_execute.append(execute)
      l_stock.append(stock)
      l_cash.append(cash)
      prix_precedent = fair[k]
    filled = np.array(l_execute, dtype=bool)
    inventory = np.array(l_stock, dtype=int)
    cash_array = np.array(l_cash)
    pnl = float(cash_array[-1] + inventory[-1] * fair[-1])
    return {"times": times , "sides": sides,
                   "filled": filled,
                     "inventory": inventory, "cash": cash_array,
                       "fair": fair, "pnl": pnl, "n_orders": n_orders,
                         "n_fills": n_fills, "n_missed": n_missed}


         
         
  
         

      
         
