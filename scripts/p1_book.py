from quantlab.orderbook import OrderBook
import numpy as np
import time
import matplotlib.pyplot as plt


def niveaux(book, side):
    d = {}
    for order in book.dict_orders.values():
        if order[0] == side:
            d[order[1]] = d.get(order[1], 0) + order[2]
    return d

def afficher(book):
    asks = niveaux(book, "sell")
    bids = niveaux(book, "buy")
    price_ask = sorted(asks, reverse=True)
    price_bids = sorted(bids, reverse=True)
    morceaux_asks = []
    morceaux_bids = []
    for price_a in price_ask:
        texte_a = f"{price_a} x{asks[price_a]}"
        morceaux_asks.append(texte_a)
    print("Asks : " +  "|".join(morceaux_asks))
    for price_b in price_bids:
        text_b = f"{price_b} x{bids[price_b]}"
        morceaux_bids.append(text_b)
    print("Bids : " +  "|".join(morceaux_bids))


journee = [
    ("limit", "buy", 100, 5),     # id 1
    ("limit", "buy", 99, 3),      # id 2
    ("limit", "buy", 99, 2),      # id 3  (même prix que l'id 2)
    ("limit", "buy", 97, 4),      # id 4
    ("limit", "sell", 101, 2),    # id 5
    ("limit", "sell", 102, 3),    # id 6
    ("limit", "sell", 102, 4),    # id 7  (même prix que l'id 6)
    ("limit", "sell", 104, 5),    # id 8
    ("market", "buy", 8),         # mange 3 niveaux (101, 102, 102)
    ("market", "buy", 3),
    ("market", "sell", 4),
    ("cancel", 3),                # ordre vivant : True
    ("cancel", 5),                # ordre déjà exécuté : False
    ("cancel", 8),                # annule le seul ask : le carnet n'a plus d'ask
    ("limit", "sell", 103, 4),    # id 9
    ("limit", "sell", 105, 3),    # id 10
    ("limit", "buy", 104, 6),     # id 11 : exécute 4 à 103, puis pose 2 à 104
    ("limit", "sell", 98, 8),     # id 12 : exécute 6 (104, 100, 99), puis pose 2 à 98
    ("cancel", 10),               # annule le sell 105
    ("market", "buy", 5),         # plus gros que le carnet : 2 exécutés, le reste est jeté
]

b = OrderBook()
hist_bid = []
hist_ask = []
for i, action in enumerate(journee, 1):
    print(f"--- action {i} : {action} ---")
    if action[0] == "limit":
        resultat = b.add_limit_order(action[1], action[2], action[3])
    elif action[0] == "market":
        resultat = b.add_market_order(action[1], action[2])
    elif action[0] == "cancel":
        resultat = b.cancel(action[1])

    ask = b.best_ask()
    if ask == None:
        ask = np.nan
    hist_ask.append(ask)
    bid = b.best_bid()
    if bid == None:
        bid = np.nan
    hist_bid.append(bid)
    print(resultat)
    afficher(b)
x = list(range(1, len(journee) + 1))  
plt.step(x, hist_bid, where="post", label="best bid")
plt.step(x, hist_ask, where="post", label="best ask")
plt.legend()
plt.xlabel("Numéro de l'action")
plt.ylabel("Price")
plt.title("Meilleur bid et meilleur ask au fil de la journée")
plt.savefig("figures/p1_best_prices.png") 

def chrono():
    rng = np.random.default_rng(0)
    b = OrderBook()
    ids = []
    t0 = time.perf_counter()
    for i in range(100_000):
        r = rng.random()
        if r < 0.55:
            if rng.random() < 0.5:
                side = "sell"
            else:
                side = "buy"
            price = int(rng.integers(95,106))
            qty = int(rng.integers(1,6))
            oid, fills = b.add_limit_order(side, price, qty)
            ids.append(oid)
        elif 0.55 <= r < 0.80:
            if rng.random() < 0.5:
                side = "sell"
            else:
                side = "buy"
            qty = int(rng.integers(1,6))
            fills = b.add_market_order(side, qty)
        else:
            if ids:
                indice = int(rng.integers(len(ids)))
                id_a_annuler = ids.pop(indice)
                b.cancel(id_a_annuler)
    t1 = time.perf_counter()
    total_time = t1 - t0
    print(f" total time :{total_time:.3f} et mean time : {
        total_time/ 100_000 * 1e6:.2f}")
chrono()
