---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Module 8/9 — Where Backtests Lie, and the Statistics That Catch Them `[deep]`

**Learning objectives.** After this lesson you can: (1) demonstrate — in code — the
no-look-ahead property a trustworthy engine must have; (2) show why costs and a
latching kill switch are non-negotiable; (3) run the *honesty statistics*: fool the
probabilistic Sharpe with a best-of-many selection, then catch it with the deflated
Sharpe.

## 1. Intuition

A backtest can lie in two places: the **engine** (peeking, free fills, ignored
costs) and the **inference** (trying 200 things and reporting the winner). This
lesson attacks both, using the real `quantropy` engine and evaluation stack on
synthetic data — synthetic *on purpose*: when you control the truth, you can prove
the machinery honest.

## 2. The engine cannot peek — prove it

The engine's contract: a decision on bar *t* sees history only through *t* and
fills at *t+1*. If that holds, **changing the future cannot change the past**:

```{code-cell} ipython3
import numpy as np
import pandas as pd

from quantropy.backtest import RiskLimits, SimulatedVenue, run_backtest
from quantropy.data.model import AssetClass, Instrument
from quantropy.research import MovingAverageCross


def series(values):
    return pd.Series(values, index=pd.bdate_range("2024-01-01", periods=len(values)), dtype=float)


class PassThrough:
    def scale(self, raw, history):
        return raw


SPY = Instrument("SPY", AssetClass.ETF)


def run(prices):
    return run_backtest(
        prices, MovingAverageCross(3, 8), PassThrough(), SPY,
        limits=RiskLimits(max_leverage=2.0, max_drawdown=0.99),
        venue=SimulatedVenue(slippage_bps=0, cost_bps=0),
    )


base = series(100 + np.cumsum(np.sin(np.arange(40))))
wild = base.copy()
wild.iloc[30:] = [1000, 1, 500, 2, 800, 3, 900, 4, 700, 5]   # absurd future

(run(base).frame.iloc[:30] == run(wild).frame.iloc[:30]).all().all()
```

`True`: thirty bars of history are byte-identical even though the future was
replaced with nonsense. This **prefix invariance** is the single most important
property of any backtest engine — and it's a CI-enforced test in this repo, not a
promise.

## 3. Costs only ever hurt — and the kill switch latches

```{code-cell} ipython3
rng = np.random.default_rng(7)
prices = series(100 * np.cumprod(1 + rng.normal(0, 0.01, 120)))

finals = {}
for bps in (0, 10, 50):
    venue = SimulatedVenue(slippage_bps=0, cost_bps=bps)
    res = run_backtest(prices, MovingAverageCross(5, 20), PassThrough(), SPY,
                       limits=RiskLimits(max_leverage=2.0, max_drawdown=0.99),
                       venue=venue)
    finals[f"{bps}bps"] = round(float(res.equity.iloc[-1]))
finals
```

Monotonically worse with costs — a frictionless backtest is an upper bound
pretending to be an estimate. And when a long position rides into a crash, the
drawdown switch must **latch** (no automatic re-entry — that's how drawdowns
compound):

```{code-cell} ipython3
crash = series([100, 100, 100, 70, 65, 64, 63, 62])


class AlwaysLong:
    def target(self, history):
        return 1.0


res = run_backtest(crash, AlwaysLong(), PassThrough(), SPY,
                   limits=RiskLimits(max_leverage=2.0, max_drawdown=0.20))
res.killed, res.frame["position_units"].iloc[-1]
```

## 4. The inference lie: fool PSR, get caught by DSR

Now the subtler lie. Generate **200 strategies with zero true alpha**, keep the
best-looking one, and evaluate it naively:

```{code-cell} ipython3
from quantropy.evaluation import deflated_sharpe, probabilistic_sharpe

rng = np.random.default_rng(11)
trials = [pd.Series(rng.normal(0, 0.01, 750)) for _ in range(200)]
srs = [t.mean() / t.std(ddof=1) for t in trials]
best = trials[int(np.argmax(srs))]

psr = probabilistic_sharpe(best)          # "is the Sharpe real?" — fooled
dsr = deflated_sharpe(best, n_trials=200, # same question, counting the trials
                      var_trial_sr=float(np.var(srs, ddof=1)))
round(psr, 3), round(dsr, 3)
```

The probabilistic Sharpe is highly confident — the strategy *looks* real. The
deflated Sharpe, told that 200 things were tried, is not. **The only difference
between the two numbers is a disclosed trials count** — which is why this project
keeps a cumulative trials ledger (`quantropy.research.TrialsLedger`) and why any
Sharpe reported without one is, per the references, pseudo-mathematics.

## 5. Pitfalls

- Prefix invariance protects against *engine* look-ahead only — feature-level
  leakage (full-sample standardization, restated fundamentals) needs Module 2's
  PIT discipline and the causal feature contract.
- DSR needs the variance of trial Sharpes, honestly measured; logging only your
  favorite trials understates it and under-deflates. Every variation you *looked
  at* is a trial.
- The kill switch is a risk policy, not a return enhancer — expect it to cost
  return in most samples and to save the firm in the one that matters.

## 6. Exercises

1. Break the engine on purpose: modify `run` to hand the signal `prices` (the full
   series) instead of `history`, and show prefix invariance failing.
2. With the trials above, how many trials does it take before DSR < 0.5 for the
   best strategy? Plot DSR vs N.
3. Log the 200 trials into a `TrialsLedger` (tmp file) and recompute DSR from
   `ledger.n_trials()` and `ledger.trial_sharpe_variance()`.

## Further reading

`docs/REFERENCES.md` §1: Bailey & López de Prado (2012, 2014); the
Arnott-Harvey-Markowitz protocol; López de Prado (2018) ch. 7 (purged CV).
