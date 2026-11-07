"""P3: the market maker's inventory as a Markov chain (first-step analysis, absorbing chains)."""
from __future__ import annotations

import numpy as np


def birth_death_transition_matrix(p: float, L: int) -> np.ndarray:
    """Transition matrix of the inventory random walk with absorbing barriers at -L and +L.

    States are the inventories -L, -L+1, ..., L (index 0 is -L, index 2L is +L), so the matrix has shape
    (2L+1, 2L+1). From an interior state the inventory goes up by 1 with probability p and down by 1 with
    probability 1 - p. The two end states are absorbing (they stay where they are with probability 1).
    """
    n = 2 * L + 1
    m = np.zeros((n,n))
    for i in range(1, 2*L):
        m[i, i+1] = p
        m[i, i-1] = 1 - p 
    m[0, 0] = 1
    m[2*L , 2*L] = 1
    return m 


def absorption_analysis(P, absorbing) -> tuple[np.ndarray, np.ndarray]:
    """First-step analysis of an absorbing Markov chain.

    P: transition matrix (n, n). absorbing: list of the indices of the absorbing states.
    Write P = [[Q, R], [0, I]] after listing the transient states (in increasing index order) first.
    Return (B, t):
      B[i, j] = probability that, starting from the i-th transient state, the chain is absorbed in absorbing[j];
      t[i]    = expected number of steps before absorption, starting from the i-th transient state.
    Hint: solve linear systems with (I - Q); do not simulate.
    """
    transitoires = []
    for a in range(len(P)):
        if a not in absorbing:
            transitoires.append(a)
    Q = P[np.ix_(transitoires, transitoires)]
    R = P[np.ix_(transitoires, absorbing)]
    I = np.eye(len(transitoires))
    Vecteur_1 = np.ones(len(transitoires))
    B = np.linalg.solve((I-Q), R)
    t = np.linalg.solve((I-Q), Vecteur_1)
    return (B, t)


def simulate_inventory_exit(p: float, L: int, n_sims: int, seed: int | None = None) -> tuple[float, float]:
    """Monte Carlo check of the same chain, started at inventory 0.

    Simulate n_sims walks (up with probability p, down otherwise) until |inventory| = L.
    Return (fraction of walks that exit at +L, average number of steps before exit).
    """
    
    sorties_haut = 0
    somme_pas = 0
    rng = np.random.default_rng(seed)
    for i in range(n_sims):
        stock = 0
        pas = 0
        while (stock != L) and (stock != -L):
            nombre = rng.random()
            if nombre < p:
                stock += 1
            else:
                stock -= 1
            pas += 1
        somme_pas += pas
        if stock == L:
            sorties_haut += 1 
    fractions_de_marche_L = sorties_haut / n_sims 
    moyenne_de_pas =  somme_pas / n_sims
    return (fractions_de_marche_L, moyenne_de_pas)

