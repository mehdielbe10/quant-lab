# quant-lab: a market maker, from the order book to risk

> **Template. Replace every <placeholder>. Write only results you actually obtained.**

A simulated exchange written from scratch in Python (NumPy, SciPy, pandas), with unit tests. A market-making bot quotes a bid and an ask around a fair price, clients arrive at random (some of them informed), and the project answers: *how should a market maker quote, what do informed clients cost, how risky is the inventory, and how do we know the strategy beats luck?* Every result is checked against theory.

## What is in it

| Stage | Module | Question | Result |
|---|---|---|---|
| P0 Fair price | `simulation` | How do I simulate the true price exactly, at irregular times? | Exact GBM (Ito-corrected); Monte Carlo call price matches Black–Scholes (<error>), standard error ∝ 1/√N |
| P1 Order book | `orderbook` | How do buyers and sellers get matched, fast? | Price-time priority, heap + lazy deletion, O(log n) per order; <n> orders in <t> s |
| P2 Client flow | `flow` | When do clients arrive? | Poisson arrivals; P(next is a buy) = λ_b/(λ_b+λ_s) confirmed (<values>) |
| P3 First market maker | `markov`, `marketmaker` | How risky is the inventory? | Expected time to hit the inventory limit: exact <a>, simulated <b>, full engine <c> |
| P4 Informed clients | `regression` | What do informed clients cost? | <Bayes break-even spread; t-stat of order flow on price moves> |
| P5 Optimal quotes | | Where should I quote? | <optimal half-spread δ* = 1/k, with inventory penalty> |

Figures: `figures/<...>.png`.

## How to run (under 5 minutes)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python scripts/p3_market_maker.py
```

## Limitations

- A simulation: i.i.d. Poisson flow, constant parameters, a single asset, no latency, no fees.
- <your own limitation>

## References

- Hull, *Options, Futures and Other Derivatives*; Shreve, *Stochastic Calculus for Finance II*.
- <Glosten & Milgrom (1985), Avellaneda & Stoikov (2008): add only after reading and checking them.>
