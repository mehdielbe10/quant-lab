import numpy as np
import matplotlib.pyplot as plt
from quantlab.simulation import simulate_gbm, bs_call, mc_call_price

prix, erreur = mc_call_price(100, 100, 0.05, 0.2, 1, n_paths=200_000, seed=0)
print("Monte Carlo :", prix, "+-", erreur)
print("Black-Scholes :", bs_call(100, 100, 0.05, 0.2, 1))

paths = simulate_gbm(100, 0.05, 0.2, 1, 252, 20)

t = np.linspace(0, 1, 253)
plt.plot(t, paths.T)
plt.xlabel("Temps (années)")
plt.ylabel("Prix")
plt.savefig("figures/p0_trajectories.png")