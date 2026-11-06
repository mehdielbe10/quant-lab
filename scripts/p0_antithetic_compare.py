from quantlab.simulation import mc_call_price

for anti in (False, True):
    prix, se = mc_call_price(100, 100, 0.05, 0.2, 1.0, 100_000, seed=0, antithetic=anti)
    print("antithetic =", anti, "| prix =", prix, "| SE =", se)