# quant-lab: a market-making simulator

A Python simulation of a market maker: a trader who continuously posts a buy price (the bid)
and a sell price (the ask), earns the bid-ask spread from client orders, and has to manage the
inventory risk that this creates (holding too much stock, or being short too much).

The project asks four questions, step by step:
1. How should a market maker quote?
2. What does it cost to trade against clients who know more than you (adverse selection)?
3. How risky is the inventory?
4. How do you tell a strategy that works from one that was just lucky?

This is a simulation to understand mechanisms. It is not a profitable trading strategy on a real market.

## Status

- Phase 1: the trading engine (prices, order book, client flow, first market maker). Done.
- Phase 2: adverse selection, optimal quoting, statistical evaluation. Planned (next).
- Phase 3: portfolio risk, estimation, backtesting. Planned.


## Phase 1: the trading engine (done)

### P0. Fair price: geometric Brownian motion, Black-Scholes, Monte Carlo
- Simulates asset prices with the exact geometric Brownian motion scheme
  `S(t+dt) = S(t) * exp((r - sigma^2/2) dt + sigma sqrt(dt) Z)` (no Euler approximation), including
  at irregular time steps.
- Prices European call options by Monte Carlo with standard error and 95% confidence interval,
  and checks the result against the closed-form Black-Scholes price.
- Uses antithetic variates (Z and -Z) as a variance-reduction technique: the standard error
  goes from 0.0465 to 0.0331 (-29%) for the same number of draws.
- Key idea: the `-sigma^2/2` term comes from the convexity of the exponential, `E[exp(sigma sqrt(t) Z)] = exp(sigma^2 t / 2)`.
  Without it the average price would drift upward.

### P1. Limit order book
- A matching engine with price-time priority: best price first, then oldest order first.
- Data structures: two heaps (bids stored with negative prices to get a max-heap, asks as a min-heap)
  plus a dictionary of live orders.
- Lazy deletion: cancelling an order only removes it from the dictionary, in O(1). The dead entry
  is discarded when it reaches the top of the heap, so the cost is amortized O(log n) per order.
- Supports limit orders, market orders, cancellations, and "marketable" limit orders
  (an order that crosses the book first trades as a taker, then rests as a maker).
- Two invariants are checked after each of 3,000 randomized operations: the book is never crossed
  (best bid < best ask) and quantities are conserved (received = executed + resting + cancelled).
- Performance on a laptop: 100,000 limit orders in about 0.21 s, and 100,000 mixed operations
  (55% limit, 25% market, 20% cancel) in about 0.19 s (roughly 2 microseconds per operation).

### P2. Client order flow: Poisson processes
- Buy and sell orders arrive as independent Poisson processes with rates `lambda_b` and `lambda_s`.
  Waiting times between arrivals are exponential with memorylessness.
- The two flows are merged in time order with a k-way heap merge (O(N log k)), instead of
  concatenating and sorting everything (O(N log N)).
- Validated statistically with three experiments:
  - waiting times follow the exponential distribution with mean and standard deviation `1/lambda`;
  - arrival counts in a window have mean = variance = lambda t (checked on simulated counts);
  - the fraction of buy orders is `lambda_b / (lambda_b + lambda_s)`: 0.7508 simulated vs 0.75
    theoretical (standard error 0.003).

### P3. First market maker and inventory risk
- A market-making engine that combines the order book, the client flow and the fair price: it quotes
  a bid and an ask around the centre price (a half-spread, in ticks), is hit by client orders,
  and tracks cash, inventory and P&L over time.
- Against uninformed clients, the P&L of one trade is the spread captured; the gain or loss from
  the inventory (`q * dV`) has expected value zero, because the client order direction `q` is independent
  of the next price move `dV`, but it adds variance (`q^2 Var(dV)`).
- The inventory is modelled as an absorbing Markov chain (the absorbing states are the inventory
  limits `-L` and `+L`). With first-step analysis, the expected time before hitting a limit is
  `E = (I - Q)^(-1) 1` (the fundamental matrix), and the probability of exiting on each side is
  `B = (I - Q)^(-1) R`. In the symmetric case the expected exit time from zero is exactly `L^2` steps.
- The exact result is confirmed by Monte Carlo simulation of the random walk and by an end-to-end test
  of the full engine.
- Known limitation of this model: clients are uninformed and accept any price, so the market maker
  never suffers adverse selection: it earns the spread on every trade, and only the inventory adds risk.
  This is the "too nice" assumption that Phase 2 removes.


## Phase 2: adverse selection and optimal quoting (planned)

### P4. Informed clients
- Add a fraction of clients who know the next price move and trade accordingly.
- Model the market maker's learning with Bayes' rule: after seeing a buy or a sell, how likely is it that
  the client is informed? This is the Glosten-Milgrom model, where the spread exists to compensate
  for trading against informed traders.
- Measure the market maker's losses (adverse selection) in simulation, and use OLS regression
  to estimate how much the spread must widen to break even as the share of informed traders grows.

### P5. Optimal quoting under inventory risk
- Estimate how client order intensity depends on the distance of the quote from the fair price,
  with a log-linear regression of `A * exp(-k * delta)`; the optimal distance without inventory risk is `delta* = 1/k`.
- Add an inventory penalty: shift the bid and the ask against the current inventory
  (quote lower prices when long, higher when short) to push the position back toward zero.
- Compare this with symmetric quotes on both the P&L and its variance.

### Statistical evaluation
- Use the bootstrap to build confidence intervals on a strategy's profit, and to compare two
  strategies: is the difference a real edge or noise?

## Phase 3: portfolio risk and backtesting (planned)

- Several correlated assets, simulated with a Cholesky decomposition of the covariance matrix.
- Estimation of expected returns and covariance from data, and how estimation error affects decisions.
- Hedging the inventory across assets.
- Mean-variance optimization (Markowitz).
- Performance measurement: Sharpe ratio, with bootstrap confidence intervals; data-snooping
  bias (testing many strategies and keeping the best one makes the result look better than it is).
- Backtesting on historical data, and a bonus on delta-hedging an option under Black-Scholes.
- Possible final step: calibrate the simulation on real market data and run paper trading (no real money).

## Limitations

- A simulation: independent Poisson order flow, constant parameters, a single asset, no latency, no fees.
- In Phase 1 the clients are uninformed and accept any price, so the market maker cannot lose to
  adverse selection. This is what Phase 2 changes.
- The timings come from my own laptop and depend on the machine.

## Run the tests

```
pip install -r requirements.txt
pytest tests/phase1 -q
```

Tests are small programs that check automatically that each module gives the expected result
(for example: "the order book is never crossed", "the exact Markov-chain answer matches the simulation").
If all of them pass, the code does what it claims. Each phase has its own test folder.

## Repository

- `src/quantlab/`: the code (`simulation`, `orderbook`, `flow`, `markov`, `marketmaker`).
- `tests/phase1/`: the tests of Phase 1.
- `scripts/`: the experiments that produce the numbers above.
- `figures/`: plots from the experiments.
- `JOURNAL.md`: a log of what was built, what blocked me and what I understood.

## Note

This is a learning project, built step by step with guidance, which provided the plan, the test suite and hints along the way. I wrote the code of every module marked "done" and can explain each of them. The parts marked "planned" are not built yet.