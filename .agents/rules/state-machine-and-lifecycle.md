# Rule: State Machine, Lifecycle & State Authority

## 1. Authoritative Dual-State Architecture
- **`state/migration-manifest.yml`** ("WHAT"): Static inventory of discovered components, files, hooks, classes, database tables, entities, fields, themes, integrations, and external code items.
- **`state/migration-state.yml`** ("WHERE"): The authoritative runtime state tracking `lifecycle_phase`, `current_wave`, `component_states`, `active_blockers`, and `execution_health`.
- **Single-Writer Authority**: Only the master Orchestrator workflow is authorized to mutate `state/migration-state.yml`. Individual specialist agents propose state transitions via structured results.

## 2. The 10 Canonical Item Migration Statuses
Every discovered hook, class, method, table, entity, form, route, and external behavior unit must be classified into exactly one of the 10 canonical statuses:
1. `COMPLETE`: Fully implemented with verified functional equivalence.
2. `PARTIAL`: Partially implemented; specific sub-methods or branches require remediation.
3. `MISSING`: Discovered in legacy D7 but absent in target D10/D11.
4. `BLOCKED`: Prevented from proceeding by an unmigrated upstream dependency or blocker ticket.
5. `HUMAN_INTERVENTION_REQUIRED`: Ambiguous business logic, policy choice, or conflicting architecture; requires human decision.
6. `RUNTIME_UNVERIFIED`: Statically compliant, but requires live Drupal runtime/CLI execution to verify behavior.
7. `SUPERSEDED`: Replaced by modern Drupal core or platform features.
8. `REPLACED`: Replaced by another module, service, or existing target implementation.
9. `OBSOLETE`: Dead code or retired legacy shim with verified zero active callers.
10. `EXCLUDED`: Intentionally excluded from scope with documented justification.

## 3. The 15 Component Lifecycle States
Components transition through canonical states:
`NOT_STARTED` -> `DISCOVERED` -> `ANALYZED` -> `PLANNED` -> `SCAFFOLDED` -> `IN_PROGRESS` -> `CODE_COMPLETE` -> `TESTING` -> `TESTS_PASSED` -> `VALIDATING` -> `VALIDATED` -> `COMPLETED`.
Exception branches: `BLOCKED`, `BLOCKED_UPSTREAM`, `SKIPPED`.

## 4. The 3-Path Remediation Decision Model
- **Path 1 (Fixable from Evidence)**: Auto-remediate `MISSING` or `PARTIAL` items with stable IDs (e.g. `<MODULE>-SERVICE-001`) up to `max_remediation_iterations` (default: 3).
- **Path 2 (Requires Human Decision)**: Halt immediately with `HUMAN_INTERVENTION_REQUIRED` on ambiguous requirements; never guess business logic.
- **Path 3 (Runtime Unavailable)**: Mark `RUNTIME_UNVERIFIED` and continue static verification without false completion claims.

## 5. Reference
- Detailed specifications: [MIGRATION_LIFECYCLE.md](../../MIGRATION_LIFECYCLE.md) and [REPORTING_STANDARD.md](../../REPORTING_STANDARD.md)
