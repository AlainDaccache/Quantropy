# Quantropy

**An applied quant curriculum backed by a focused, deep reference implementation.**

Quantropy teaches the quant body of knowledge *by running it*: an executable,
CI-tested curriculum (every lesson's code executes against this library on every
build — nothing rots), on top of a reference implementation that is genuinely deep
where real data allows:

- **Systematic trading** — research → signal → portfolio → backtest → evaluation →
  paper trading (IBKR), with a real, honestly-evaluated track record.
- **Fundamental equity valuation** — DCF / reverse-DCF / archetypes from SEC EDGAR
  filings, point-in-time clean.
- **The rigor stack** — no-look-ahead backtesting, deflated/probabilistic Sharpe,
  PBO, walk-forward & purged CV, robust covariance, a cumulative trials ledger.

Where a mature library already does it right, we **integrate instead of reinvent**
(QuantLib for derivatives, PyPortfolioOpt for optimization baselines, statsmodels/arch
for econometrics) — and teach through it. Every capability and lesson is honestly
labeled `[deep]`, `[integration]`, or `[survey]`.

## Getting started

```bash
pip install -e ".[dev,data]"       # library + tests + data providers
pytest                              # reference-value & invariant test suite
python examples/thin_thread.py     # signal -> sizing -> risk limits -> costed backtest
                                    #   (--live routes the same decision to IBKR paper)
pip install -e ".[book]"           # the executable curriculum
jupyter-book build curriculum
```

## The plan

| Document | What it is |
|---|---|
| [`MASTER_SPEC.md`](MASTER_SPEC.md) | Requirements, field map, milestones — the whole plan |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Domain model, bounded contexts, the **CI-enforced** dependency law |
| [`docs/CURRICULUM.md`](docs/CURRICULUM.md) | The full syllabus ("a CFA program for quants") |
| [`docs/REFERENCES.md`](docs/REFERENCES.md) | ~160 verified sources, mapped to every lesson |
| [`docs/BOUNDARIES.md`](docs/BOUNDARIES.md) / [`docs/SCRUTINY.md`](docs/SCRUTINY.md) | What's deliberately not covered; the hardest objections, pre-answered |

Earlier work is archived under [`legacy/`](legacy/) and ported piece-by-piece —
every ported formula gets a reference-value test first
([`docs/PROVENANCE.md`](docs/PROVENANCE.md)).

## License

MIT — see [LICENSE](LICENSE).
