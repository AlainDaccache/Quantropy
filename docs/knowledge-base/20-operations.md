# Operations, security and governance

Status: specification and research map; implementation not certified. Edition: 2026-10-05.

Live reliability is a product capability. Separate research from production credentials and execution rights. Use secret storage, least privilege, authentication, explicit account bindings, encrypted transport and reviewed dependency/update policies. Local-first reduces some complexity but does not remove malware, lost-device or credential risk. Web and desktop security controls have different requirements. [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/), [desktop guidance](https://owasp.org/projects/thick-client-application-security-verification-standard).

Observe data freshness, clock synchronization, broker sessions, order latency/rejections, risk headroom, reconciliation breaks, disk/database health and job failures. Alerts need actionable severity, deduplication and escalation, including a way to notice that the alert service itself failed. Define market/account-specific objectives for acceptable staleness, recovery time and loss of records; do not invent one universal latency SLA.

Persist checkpoints and event history; maintain backups and test restoration on a separate environment. Crash recovery should resume only after reconciling actual broker state. A Windows laptop may sleep, reboot, lose connectivity or shut down. For unattended strategies evaluate a dedicated host/VPS and supervised gateway; portability and recovery procedures matter more than a cloud label.

Use versioned model/config/data releases, migrations, rollback, change review and deployment records. Risk-limit changes and trading enablement are auditable. Research models cannot automatically promote themselves based on the best backtest. Maintain runbooks for stale data, unknown orders, margin calls, expiry, broker outage, corrupted state and compromised credentials.

Acceptance: recovery drills with simulated disconnects and crash boundaries; verified restore; redacted logs; no secret in git/report/notebook; production cannot load an unapproved artifact; alert delivery is tested. Tax/legal/data obligations depend on location, use and distribution. A personal app is not automatically exempt from every applicable obligation.

## Coverage checklist

- Secrets permissions and account separation
- Authentication encryption and redacted logs
- Dependency security and license inventory
- Monitoring alerts and heartbeat failure
- Clock data and broker health checks
- Backups restore and crash recovery
- Dedicated-host and laptop resilience
- Versioned deployments migrations rollback
- Model promotion and change governance
- Incident and emergency runbooks
- Privacy retention and data obligations

## Research sources

- [OWASP](sources.md#owasp)
- [OWASP-DESKTOP](sources.md#owasp-desktop)
- [IBKR-ERRORS](sources.md#ibkr-errors)

[Knowledge base index](README.md)
