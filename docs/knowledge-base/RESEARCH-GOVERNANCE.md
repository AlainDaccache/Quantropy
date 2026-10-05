# Research governance

The canonical editing location is this knowledge-base directory in the Quantropy branch. Output bundles are copies, not a second source of truth. The older build scripts in a local working directory generated the original specifications; running them over this edition would discard the reference revision and must not be used as an update workflow.

Every new detailed topic needs a stable ID, one owner, prerequisite links, aliases, date/jurisdiction when relevant, and the completion contract in [the audit](FINANCE-AUDIT.md). Do not duplicate definitions in product pages. Curriculum/book mappings are views of the concept catalog; title identification is not chapter-level review. Existing 306 method entries need migration before an all-method DRY claim is appropriate.

Source review records should identify edition, inspected section, exact claim supported and limitations. Distinguish original research, standards, official documentation, educational synthesis and author interpretation. Full derivations need primary-source review and independent mathematical checking. Conflicting conventions should be named and linked rather than flattened into one apparently universal formula.

Changes to a material definition must update dependent examples and mark affected implementations for revalidation. Formula verification, empirical validation and editorial review are separate evidence fields. Laws, broker behavior, product availability, accounting rules and data permissions need dated rechecks. Never represent a method as profitable because it appears in a textbook or passes a backtest.

To validate this edition: run `python tools/verify_knowledge_base.py` from the repository root. This checks navigation, coverage ownership, example evidence and manifest integrity. It does not run financial-engine tests. After an intentional edit, regenerate manifest file hashes, inspect the diff, then rerun verification; do not silently repair hashes to conceal unexpected changes.

[Index](README.md)

Use the [knowledge contract](templates/knowledge-contract.md). The initial [claim evidence register](claim-evidence.csv) documents seven scoped claims; it is not exhaustive claim attribution.

Verify detailed drafts with `python tools/verify_finance_contracts.py`. This checks catalog membership, prerequisite acyclicity and separately calculated examples. Use `--write-evidence` only after reviewing an intentional change to the examples; then refresh the manifest and rerun both verifiers.
