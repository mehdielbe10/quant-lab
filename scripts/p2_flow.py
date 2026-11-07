from quantlab.flow import poisson_arrival_times, generate_order_flow
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson

rate = 2
temps_attente = np.diff(poisson_arrival_times(rate = rate, horizon = 5000, seed = 0))
print(f"mean: {temps_attente.mean()}")
plt.hist(temps_attente, bins=50, density=True, label = "Simulation")
t = np.linspace(0, temps_attente.max(), 200)
f =  rate * np.exp(t*(-rate))
plt.plot(t, f, label="Courbe théorique")
plt.xlabel("temps d'attente en seconde")
plt.ylabel("Densité")
plt.legend()
plt.savefig("figures/p2_waiting_times.png")


comptes = []
horizon = 5
for i in range(10_000):
    instants = poisson_arrival_times(rate, horizon = horizon, seed=i)
    nb_instants = len(instants)
    comptes.append(nb_instants)
comptes = np.array(comptes)
print(f"moyenne : {np.mean(comptes)}")
print(f"variance : {np.var(comptes)}")
plt.figure()
plt.hist(comptes, bins=np.arange(-0.5, comptes.max() + 1.5), density=True, label = "Simulation_P")
k = np.arange(0, comptes.max() + 1)
mu = rate * horizon
pmf = poisson.pmf(k, mu)
plt.plot(k, pmf, "o-", label="Poisson théorique")
plt.xlabel("Nombre de clients")
plt.ylabel("probabilité")
plt.legend()
plt.savefig("figures/p2_counts.png")


lam_buy = 3 
lam_sell = 1
flux = generate_order_flow(lam_buy, lam_sell, horizon=5000, seed=0)
p = lam_buy / (lam_buy + lam_sell)
n = len(flux)
fraction_event = sum(1 for _, cote in flux if cote == "buy")/n
standard_error = np.sqrt((p*(1-p)/n))
print(p)
print(f"fraction event :{fraction_event}")
print(f"standard_error : {standard_error}")