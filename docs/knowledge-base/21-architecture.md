# Architecture and domain contracts

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Start as a modular monolith in one Quantropy repository with clear interfaces. Premature microservices increase operational overhead before the financial semantics are stable. Separate bounded modules: instruments/calendars, raw/normalized data, accounting, pricing/analytics, research, strategy/portfolio, simulation, risk, execution/adapters, reporting and UI.

Use domain contracts rather than passing arbitrary dataframes everywhere. Instrument records declare units and conventions. Observation records declare event/availability times and provenance. A portfolio snapshot declares positions, cash, marks and as-of time. A model result declares estimate, uncertainty, assumptions and evidence. A trade intent declares desired economic action; broker orders and executions are separate records. Decimal/exact arithmetic may be appropriate for booked money/quantities, with controlled numeric arrays for analytical models.

Store datasets/snapshots in columnar files with an analytical query engine where fit is demonstrated; use a transactional database for orders, ledger, registries and workflow state. DuckDB/Parquet, SQLite/PostgreSQL and Python are candidates, not commitments made without a benchmark. Durable state must not rely on a notebook session, CSV append order or in-memory cache. A single-user build can have simpler deployment while retaining correct transactions and migration paths.

The same strategy decision interface runs against replay, simulation, paper and live observation/portfolio services. Different event/fill/broker adapters handle execution semantics. Strategy code cannot access future observations by bypassing the as-of interface. Modeling modules may run offline without any trading credentials.

Acceptance: modules can be tested independently against contracts; package dependency direction prevents broker code entering analytics; one trace follows data to decision to order to ledger; deterministic replay reproduces decisions under pinned inputs. Choose language/runtime and UI after proving two vertical workflows, not because existing repos happen to use them.

## Coverage checklist

- Modular monolith and bounded domains
- Typed observations units and availability
- Portfolio intent order execution contracts
- Pricing result assumptions and uncertainty
- Transactional order ledger registry storage
- Columnar research snapshots and query
- Shared decision interfaces across modes
- Broker and vendor adapter isolation
- Reproducible builds and dependency locking
- API UI notebook domain-service parity

## Research sources

- [LEAN](sources.md#lean)
- [QUANTLIB](sources.md#quantlib)
- [OPENBB](sources.md#openbb)

[Knowledge base index](README.md)
