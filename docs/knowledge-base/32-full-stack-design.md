# Proposed full-stack architecture and engineering sequence

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Architecture proposal, not a frozen technology commitment. Favor a Python domain library for financial models and research; a typed HTTP service exposes those same functions to an accessible browser UI. A TypeScript/React UI and FastAPI service are plausible candidates. Evaluate small prototypes and operational fit before committing versions. The API must not contain a separate implementation of financial math.

Use a transactional database for accounts, ledger, orders, workflow state, model/experiment registry and provenance links. Columnar files plus an analytical engine serve research snapshots. Keep immutable source objects and artifact hashes; large datasets stay outside git with manifests. Start with one deployment and a durable worker/job queue for ingestion, calibration and experiments. Add distributed computation only when measured workloads demand it.

Separate trust boundaries: browser/API; offline worker; credentials and execution process; broker; data vendors. Execution should have narrowly scoped permissions and consume approved artifacts/intents. Analytics must remain usable without broker credentials. Persistent order state and reconciliation do not depend on a web request staying alive. Local development can use a simpler database while obeying the same contracts; production migrations and concurrency need explicit tests.

Proposed package boundaries: domain (identities/units/conventions/contracts); data (adapters/vintages/quality); ledger; models (fundamental/pricing/statistics); research (experiments/validation); portfolio/risk; simulation; execution (broker adapters); services/API; UI; operations. Dependency direction points toward stable domain interfaces, with vendor details at the edge.

Sequence: contract fixtures and ledger first; read-only API/report; first analysis and research slices; portfolio/simulation; broker read-only/paper/recovery; controlled live; advanced domains. Integration prototypes must compare QuantLib/LEAN/OpenBB against independent fixtures and real deployment needs. Performance and availability objectives derive from each workflow. A global microservices platform or ultra-low-latency engine is unnecessary until a chosen strategy justifies it.

Acceptance: deterministic replay, transactional durable state, versioned jobs/artifacts, measured representative throughput, isolation of secrets, restore drills and a full trace from input to result to ledger. Runtime implementation remains future work after these proposals are reviewed against actual data and constraints.

## Coverage checklist

- Python domain library and shared financial math
- Typed HTTP API and browser UI
- Transactional state and analytical storage
- Durable jobs workers and artifact lineage
- Execution credential trust boundary
- Local development and production migrations
- Independent integration prototypes
- Dependency direction and stable contracts
- Measured workload performance objectives
- End-to-end replay and recovery evidence

## Research sources

- [QUANTLIB](sources.md#quantlib)
- [LEAN](sources.md#lean)
- [OPENBB](sources.md#openbb)
- [OWASP](sources.md#owasp)

[Knowledge base index](README.md)
