# Backtesting methodology at method level

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Chan and Lopez de Prado provide useful research maps, but no author's procedure should become a universal default. Chan's public teaching outline covers backtesting and practical strategy issues; the author's full books need edition/chapter review. Lopez de Prado's bibliography links research on portfolio construction, machine learning and research validation. [Chan outline](https://epchan.com/EP%20Chan%20Course%20Offerings.pdf), [original bibliography](https://www.quantresearch.org/Publications.htm).

Separate four kinds of validation. Economic premise: why a mechanism might persist and who bears its risk. Data validity: historical availability, identifiers, vintages, survivorship and prices. Engine validity: causal decisions, executable order assumptions and correct financial accounting. Statistical evidence: unseen validation, dependence, uncertainty and selection across all searched configurations.

Explicit procedures include chronological holdouts, expanding/rolling walk-forward, purged and embargoed splits for overlapping information intervals, combinatorial purged evaluation where justified, dependence-aware bootstrap, randomized/placebo tests, parameter/subsample robustness and replication against published construction. CSCV/PBO, probabilistic/deflated Sharpe approaches and minimum-track-record analysis are candidates requiring exact source/formula verification. They are not interchangeable and must not become a collection of flattering pass rates.

ML feature/label methods also need separate specifications: event/time/volume sampling, volatility-scaled events, triple-barrier labels, meta-labeling, sample overlap/uniqueness weighting, fractional differencing and feature-importance procedures. None is automatically necessary for a daily trend strategy. Labels, scaling, feature selection and hyperparameters stay within causal training partitions.

Simulation procedure must declare signal availability, venue session, decision/order/fill timing, partial fills, spread/impact/latency, borrow/funding, corporate actions, futures rolls/settlement and option lifecycle. OHLC ambiguity, stop gaps, terminal liquidation and timeout costs need independent cases. Report trade/event histories and gross/net benchmark comparisons with selection history.

Acceptance: reproduce exact research construction before claiming improvement; record changes from published universes/costs; preserve prefix causality; validate independent cash/position identities; evaluate adverse regimes and operational failure. Full-paper/book review and procedure-specific implementation cards remain required before these named methods are enabled.

## Coverage checklist

- Chan and Prado edition paper procedure mapping
- Economic data engine statistical validation separation
- Chronological rolling expanding and purged evaluation
- CSCV PBO PSR DSR track-record research candidates
- Dependence-aware bootstrap placebos and robustness
- Events triple barriers meta labels uniqueness weighting
- Fractional differencing and feature importance candidates
- Execution lifecycle cost and terminal-state fixtures
- Published replication versus modified strategy evidence
- All-trial and holdout-use governance

## Research sources

- [CHAN](sources.md#chan)
- [CHAN-BOOK](sources.md#chan-book)
- [PRADO-PUBLICATIONS](sources.md#prado-publications)
- [OVERFIT](sources.md#overfit)
- [SKLEARN](sources.md#sklearn)
- [LEAN-FILLS](sources.md#lean-fills)

[Knowledge base index](README.md)
