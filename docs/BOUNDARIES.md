# Boundaries — what this project deliberately does not cover, and why

> Knowing the negative space precisely is part of the knowledge claim. Every topic
> below is *excluded or held at survey depth on purpose*, with the reason, the seat
> it matters to, and the canonical entry point for going deeper. If a topic in
> quantitative finance appears in neither the curriculum (`docs/CURRICULUM.md`) nor
> this register, that is a defect — report it and one of the two documents gets
> amended.

Exclusion reasons: **[infra]** requires institutional infrastructure/licensing ·
**[data]** requires data that is not freely/verifiably available · **[adjacent]** a
neighboring profession's core, not a quant-generalist requirement · **[frontier]**
active research without settled practice.

## 1. Sell-side derivatives at production depth

| Topic | Why out | Seat | Entry point |
|---|---|---|---|
| Exotic pricing at desk grade (autocallables, barriers in prod) | [infra][data] — no market-quote calibration surface | Desk quant | Hull; Joshi, *Concepts & Practice of Mathematical Finance* |
| LMM/BGM & SABR calibration to live vol cubes | [data] — swaption/cap vol surfaces are licensed | Rates quant | Brigo & Mercurio, *Interest Rate Models* ¹ |
| XVA desk practice (CVA/FVA/MVA at scale) | [infra] — needs netting sets, CSAs, counterparty data | XVA quant | Gregory, *The xVA Challenge* ¹ |
| Structured products & convertibles | [data][adjacent] | Structuring | Fabozzi Handbook (§12 refs) |
| *Held instead at:* BSM/trees/Greeks `[deep]`, surface via QuantLib `[integration]`, the rest mapped in Curriculum Part V. | | | |

## 2. Credit & securitization depth

| Topic | Why out | Seat | Entry point |
|---|---|---|---|
| Loan-level credit models, CDO/copula machinery | [data] — loan tapes & CDS curves licensed | Credit quant | Duffie & Singleton, *Credit Risk* ¹ |
| MBS prepayment modeling & OAS | [data] — pool-level data licensed | MBS quant | Fabozzi Handbook (§12 refs) |
| Regulatory credit capital (IRB, CECL/IFRS9 modeling) | [infra][adjacent] | Bank risk | BCBS d424 (§14 refs) |
| *Held instead at:* structural/hazard concepts + CDS mechanics `[survey]` (Curriculum V.5, IX.3). | | | |

## 3. High-frequency & production trading infrastructure

| Topic | Why out | Seat | Entry point |
|---|---|---|---|
| Co-location, tick-to-trade latency, hardware | [infra] | HFT engineer | — (industry practice; no canonical text) |
| Live market-making at scale | [infra] — retail cannot quote | MM quant | Cartea-Jaimungal-Penalva (§13 refs) |
| kdb+/q, FIX engineering, exchange connectivity | [infra][adjacent] | Quant dev | vendor docs; Harris (§13 refs) for context |
| C++/low-latency systems | [adjacent] — demonstrable only with a targeted artifact | Quant dev | — |
| *Held instead at:* microstructure economics + Almgren-Chriss + Avellaneda-Stoikov in simulation `[survey/integration]` (Curriculum VIII.1–.2). | | | |

## 4. Asset classes & venues

| Topic | Why out | Seat | Entry point |
|---|---|---|---|
| Crypto/DeFi (perps, funding, AMMs, MEV) | deliberate scope; calendar layer admits it later | Crypto quant | — (fast-moving; no stable canon) |
| Physical commodities & power markets (storage, transport, nodal pricing) | [data][adjacent] — a whole discipline (energy quant) | Energy quant | Eydeland & Wolyniec, *Energy and Power Risk Management* ¹ |
| Municipal bonds, EM local debt | [data] | FI specialist | Fabozzi Handbook (§12 refs) |

## 5. Adjacent professions

| Topic | Why out | Seat | Entry point |
|---|---|---|---|
| Actuarial/insurance (reserving, longevity, Solvency II) | [adjacent] | Actuary | SOA syllabus |
| Regulatory submission mechanics (FRTB-IMA, CCAR filings) | [infra][adjacent] — literacy kept at IX.3/IX.6 `[survey]` | Bank risk | BCBS (§14 refs) |
| Tax optimization at scale, estate/wealth planning | [adjacent] | Wealth mgmt | CFA L3 pathways |
| Corporate finance execution (M&A, capital raising) | [adjacent] — valuation overlap covered in Part IV | Banker | Koller et al. (§6 refs) |

## 6. Frontier / research-grade topics

| Topic | Why out | Seat | Entry point |
|---|---|---|---|
| Deep-RL execution/allocation at production scale | [frontier] — RL concepts appear in VI.4 | ML quant | Gu-Kelly-Xiu lineage (§11 refs) |
| DSGE/structural macro estimation | [adjacent][frontier] — nowcasting surveyed in III.1 | Macro economist | Hamilton (§5 refs) |
| Rough volatility, signature methods | [frontier] | Vol researcher | Gatheral (§5 refs) as gateway |
| Quantum/alternative computing in finance | [frontier] | — | — |

---

¹ *Named as the standard entry text; publication details not independently verified
in `docs/REFERENCES.md`'s verification pass — confirm the edition before citing.*

**Reading this register correctly:** none of these exclusions is ignorance — each is
a priced decision under the four criteria of `MASTER_SPEC.md` §4 (verifiability,
teachability, distinguishing power, solo-reachable correctness). The curriculum
teaches where each boundary *is* and what lies beyond it; crossing one later is an
extension, not a redesign.
