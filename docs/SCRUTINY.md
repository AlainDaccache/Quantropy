# Scrutiny — the hardest questions this project should face, pre-answered

> An evaluation guide written from the attacker's side. Each objection below is one
> we consider legitimate; each answer points to the artifact — not the prose — that
> carries the response. If you can land an objection this page doesn't handle,
> that's a defect: raise it.

**"Your backtest is overfit."**
Assume so until shown otherwise — that's the project's own default. The response is
structural: deflated Sharpe with a *cumulative* trials ledger (every hypothesis ever
tried counts, not just this study's), purged/embargoed walk-forward, a single-touch
holdout, and acceptance gates (Curriculum VI.6–.7). No performance number ships
without its trials count.

**"Paper trading isn't real trading."**
Correct, and we say so: every claim is tagged `[backtest]` or `[paper]`, never
"returns." Costs, financing, and injected divergences (partial fills, rejects,
latency) are modelled; the same code path runs both. Paper is the honest maximum a
retail candidate can show — the dishonest alternatives are backtest-only claims or
pretending.

**"Why should I trust your data?"**
Don't trust — check. Point-in-time storage (as-reported, restatements preserved),
survivorship-aware universes, immutable snapshots (a rerun months later reads
identical bytes), and lessons that reproduce filing figures to the dollar
(Curriculum I.4–.6; the verification ledger).

**"What's your edge? Why would these strategies make money?"**
No proprietary edge is claimed — that's deliberate. The premia harvested are the
*documented* ones (Curriculum III.6) with their economic rationales and post-cost
caveats; the deliverable is the platform, the rigor, and the honestly-measured
record. Claiming secret alpha in a public portfolio would be the actual red flag.

**"Isn't this just AI-generated documentation?"**
The documents were drafted with AI assistance under adversarial human direction —
the commit history shows the iterations. The defense is the part AI cannot supply:
every `[deep]` lesson executes in CI against code with reference-value tests, the
verification ledger names each reproduced number, and the owner's obligation
(MASTER_SPEC §6.3) is to re-derive and defend any element live. Test that in the
interview — it's the point.

**"Why Python and not C++?"**
Python is where quant *research* lives; the numerics that matter are
reference-tested. But the boundary was recalibrated after a 2026 job-market audit:
research-grade C++ is demanded well beyond HFT, so a small C++ pricing kernel with
pybind11 interop is a **planned optional artifact** (BOUNDARIES §3). Only
low-latency *systems* engineering stays out.

**"Why so much fundamental analysis for a quant curriculum? Jane Street won't test
any of it."**
Deliberate, and labeled. Pure prop-trading seats test probability and speed — the
role map says exactly that and routes those candidates to the practice track. The
FSA/valuation depth serves the *quantamental and equity-researcher* seats (Point72,
Millennium fundamental pods, quality-factor construction) where it is the
differentiator, and it feeds the quality/distress signals in Part VI. Breadth across
seats is the design, with per-seat weighting stated honestly in the role map.

**"Why no crypto? No exotics? No swaps calibration?"**
Priced exclusions, each with reason and entry point — see `docs/BOUNDARIES.md`. The
map of what's *not* covered is maintained with the same care as what is.

**"DeMiguel says 1/N beats your optimizers."**
Taught, not dodged (Curriculum VII.3): naive MVO's error-maximization is
*demonstrated* in code, 1/N is the benchmark robust methods must beat, and the
construction stack (shrinkage, BL, ERC, HRP) exists precisely because of that
literature.

**"The factor zoo — why believe any of your factors?"**
Because they're replications, not discoveries: premia reproduced to published
numbers (Ken French data), with the replication-crisis literature (Harvey-Liu-Zhu,
Hou-Xue-Zhang, Jensen-Kelly-Pedersen — both sides) taught in III.5–.6, and any *new*
claim subject to the same multiple-testing deflation as VI.6 demands.

**"Rates without swap calibration is toy fixed income."**
Sovereign curves from the Fed's own GSW data, bootstrapping, NSS fitting,
duration/key-rate/PCA risk — externally verifiable and `[deep]` (Curriculum
IV.6–.7). Swaps/vol-cube calibration is data-gated and priced as a boundary, with
QuantLib integration as the teaching path.

**"What would make you kill a strategy?"**
Pre-committed: decay monitoring against the backtest distribution, acceptance gates,
and the kill criteria in the track-record protocol (MASTER_SPEC §6.1–.2) — decided
before results exist, so the answer can't bend to them.

**"What are this project's actual weaknesses?"**
(1) The artifact set is young — the engine and live record are the next milestones,
and until months accrue on the record, performance evidence is thin. (2) One person
maintains it — bus factor of one, mitigated by tests and CI, not eliminated. (3)
Free data has real limits (no institutional-grade universes; survivorship-free
equity history is imperfect) — flagged wherever it binds. A project that couldn't
name its weaknesses would be the one to distrust.
