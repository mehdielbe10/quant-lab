"""P2: client order flow as Poisson processes."""
from __future__ import annotations

import numpy as np
import heapq


def poisson_arrival_times(rate: float, horizon: float, seed: int | None = None) -> np.ndarray:
    """Arrival times of a Poisson process of intensity `rate` on [0, horizon], sorted increasingly.

    Build it from the fact you derived on paper: the waiting times between arrivals are i.i.d. Exponential(rate).
    (Another valid method: draw N ~ Poisson(rate * horizon), then N sorted uniforms on [0, horizon].)
    If rate <= 0, return an empty array. Use np.random.default_rng(seed).
    """
    t = 0
    instants = []
    if rate <= 0:
        return np.array([])
    rng = np.random.default_rng(seed)
    while t <= horizon:
        durée = rng.exponential(1/rate)
        t += durée
        if t > horizon:
            break
        instants.append(t)
    return np.array(instants)


def merge_event_streams(streams: dict[str, "np.ndarray"]) -> list[tuple[float, str]]:
    """Merge several sorted arrays of event times into ONE chronological list of (time, label).

    streams maps a label to a sorted array of times. Ties are broken by the order of the labels in the dict.
    Do it with a heap (heapq), like "merge k sorted lists": O(N log k), not by concatenating and sorting.
    Beware of Python's late-binding closures if you build generators in a loop.
    """
    tas = []
    for rang, (etiquette, tableau) in enumerate(streams.items()):
        if len(tableau) == 0:
            continue
        evenement = (tableau[0], rang, 0, etiquette)
        heapq.heappush(tas, evenement)
    sortie = []
    while tas:
        instant, rang, indice, etiquette = heapq.heappop(tas)
        sortie.append((instant, etiquette))
        indice += 1
        if indice < len(streams[etiquette]):
            evenement_suivant = (streams[etiquette][indice], rang, indice, etiquette)
            heapq.heappush(tas, evenement_suivant)
    return sortie

   

    


def generate_order_flow(lam_buy: float, lam_sell: float, horizon: float,
                        seed: int | None = None) -> list[tuple[float, str]]:
    """Client market orders on [0, horizon]: buys arrive at rate lam_buy, sells at rate lam_sell, independently.

    Returns a chronological list of (time, side) with side in {"buy", "sell"}.
    (A client "buy" is a market buy order: it lifts the market maker's ask.)
    Same seed -> same result. Use independent random streams for buys and sells.
    """
    raise NotImplementedError
