---
description: Start or resume the recursive, evidence-driven Drupal 7 to Drupal 10/11 migration workflow for the full workspace or a targeted module.
---

# Drupal Migration: Orchestrate

Run the master orchestrator to manage the complete, dependency-aware, dynamically sequenced Drupal 7 to Drupal 10/11 migration lifecycle.

```text
/drupal-migration-agent:orchestrate [MODULE_NAME]
```
*Aliases:* `/orchestrate [MODULE_NAME]`, `/migrate-module <MODULE_NAME>`

---

## Execution Modes:

### Mode 1: Targeted Recursive Module Migration (`/orchestrate <MODULE_NAME>`)
When a specific module name is provided (e.g. `/orchestrate ariba_helper`):
1. **Target Validation**: Verify that `<MODULE_NAME>` exists in `state/migration-manifest.yml` as a `custom_module`.
2. **Recursive Dependency Discovery & Ordering**:
   - Inspect declared and implicit custom dependencies from `state/migration-manifest.yml` and `reports/dependencies/`.
   - Build the recursive ancestor graph ($\text{Ancestors}(M) \cup \{M\}$).
   - Perform cycle detection. If a cycle exists, halt with `BLOCKED-CYCLE-XXX.md`.
   - Recursively process and validate unmigrated upstream dependencies in topological order before initiating the parent module.
3. **Module Execution & Baseline Snapshot**:
   - Snapshot existing target module files and checksums (`EXISTING_TARGET_MODULE` vs `NEW_TARGET_MODULE`).
   - Dispatch `custom-module` agent with `component_id: <MODULE_NAME>` and `execution_scope: SINGLE_MODULE`.
   - Enforce strict write isolation: writes restricted exclusively to `<target_custom_modules_path>/<MODULE_NAME>/**/*`.
4. **Comparative Completeness Audit**:
   - Perform forensic D7 $\to$ D10 audit matching 100% of discovered hooks, classes, forms, routes, cache bins, queries, and integrations.
   - Classify every item into the 10 canonical statuses (`COMPLETE`, `PARTIAL`, `MISSING`, `BLOCKED`, `HUMAN_INTERVENTION_REQUIRED`, `RUNTIME_UNVERIFIED`, `SUPERSEDED`, `REPLACED`, `OBSOLETE`, `EXCLUDED`).
5. **Iterative Remediation Loop**:
   - **Branch A (Fixable from Evidence)**: For items marked `MISSING` or `PARTIAL` with empirical evidence, generate remediation tasks with stable IDs (e.g. `<MODULE>-SERVICE-001`), implement the fixes, and run targeted re-validation.
   - **Branch B (Requires Human Decision)**: For items marked `HUMAN_INTERVENTION_REQUIRED` (e.g. GDPR policy, ambiguous business rule), halt execution, log the decision options, and await user decision.
   - **Branch C (Runtime Unavailable)**: For items marked `RUNTIME_UNVERIFIED`, record the runtime verification boundary and proceed with static checks.
   - Repeat remediation loop until all material items are complete, a human decision is needed, or `max_remediation_iterations` (default 3) is reached.
6. **Evidence Suite & State Mutation**:
   - Generate standard evidence reports in `reports/migration/<MODULE_NAME>/` including the `## LLM REMEDIATION INPUT` section.
   - Authoritatively update `component_states.<MODULE_NAME>` in `state/migration-state.yml`.

---

### Mode 2: Global Workspace Orchestration (`/orchestrate`)
When invoked without arguments:
1. **Preflight Environment Validation**: Execute Preflight Gate (`commands/preflight.md`). Halt if any critical check fails.
2. **State & Progress Audit**: Read `state/migration-state.yml` to identify the current lifecycle phase and incomplete components.
3. **Dynamic Wave Scheduling**: Compute topological waves (`wave_0` ... `wave_N`) from dependency in-degrees.
4. **Wave Dispatching**: Dispatch specialist agents for all ready components in the active wave, serializing shared file writes.
5. **Iterative Wave Remediation**: Evaluate component results via Result Validation Gate, route failed components through remediation, and advance waves until 100% of workspace components reach terminal states.
6. **Final Audit**: Execute `final-audit` acceptance gates and generate `reports/final/FINAL-MIGRATION-SUMMARY.md`.

---

## Instructions for Claude:

1. Check if `migration.config.yml` exists in the workspace. If missing, prompt user to copy `migration.config.example.yml`.
2. Check if an argument was passed. If `<MODULE_NAME>` is supplied, execute **Mode 1 (Targeted Recursive Migration)**; otherwise execute **Mode 2 (Global Workspace Migration)**.
3. Always verify Preflight validation before modifying files.
4. Strictly enforce D7 source immutability (Rule 1 & Rule 2) and target path isolation.
5. Never invent business logic: if an unmapped requirement is encountered, transition component to `HUMAN_INTERVENTION_REQUIRED` and stop.
6. Persist all state transitions authoritatively in `state/migration-state.yml`.
