from quantlab.orderbook import OrderBook

b = OrderBook()
print(b.add_limit_order("sell", 102, 3))   # attendu : (1, [])
print(b.add_limit_order("buy", 100, 5))    # attendu : (2, [])
print(b.asks, b.bids)                      # attendu : [(102, 1)] [(-100, 2)]
print(b.dict_orders)                       # attendu : {1: ['sell', 102, 3], 2: ['buy', 100, 5]}

print(b.best_ask())    # attendu : 102
print(b.best_bid())    # attendu : 100

b2 = OrderBook()
b2.add_limit_order("sell", 102, 3)
print(b2.mid_price())   # attendu : None
print(b2.spread())      # attendu : None
print(b.mid_price())    # attendu : 101.0
print(b.spread())       # attendu : 2