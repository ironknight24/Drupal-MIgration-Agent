# Antigravity Workflow: Master Orchestrator

## Purpose
Runs the master orchestrator to manage the complete, dependency-aware, dynamically sequenced Drupal 7 to Drupal 10/11 migration lifecycle for the full workspace or a targeted module.

## Trigger & Invocation
This workflow is triggered via either slash commands or natural language conversation:

- **Mode A: Global Workspace Migration**:
  - Slash Command: `/orchestrate`
  - Conversational Triggers / Natural Intent:
    - `orchestrate`
    - `run orchestration`
    - `run full migration`
    - `start global migration`
    - `migrate entire site`
- **Mode B: Targeted Single-Module Migration**:
  - Slash Commands: `/orchestrate <MODULE_NAME>` or `/migrate-module <MODULE_NAME>`
  - Conversational Triggers / Natural Intent:
    - `orchestrate <MODULE_NAME>`
    - `migrate module <MODULE_NAME>`
    - `migrate-module <MODULE_NAME>`
    - `run migration for <MODULE_NAME>`
- **Corresponding Claude Commands**: `commands/orchestrate.md` and `commands/migrate-module.md`

## Operational Procedure

### Execution Architecture (Subagents & Inline Fallback)
The Orchestrator dispatches specialist tasks using native subagents when available. If subagent dispatch is unavailable, the Orchestrator executes specialist procedures inline by adopting the respective specialist role and skill protocol without failing.

### Mode 1: Targeted Recursive Module Migration (`orchestrate <MODULE_NAME>`)
1. Validate `<MODULE_NAME>` exists in `state/migration-manifest.yml`.
2. Construct ancestor sub-DAG ($\text{Ancestors}(M) \cup \{M\}$) including any coupled external code.
3. Perform cycle detection. If a cycle is found, emit `BLOCKED-CYCLE-XXX.md` and halt.
4. Recursively migrate unmigrated upstream dependencies in bottom-up topological order.
5. Snapshot target module directory (`EXISTING_TARGET_MODULE` vs `NEW_TARGET_MODULE`).
6. Execute migration for `<MODULE_NAME>` with strict write isolation to its directory.
7. Run comparative completeness audit across 12 dimensions and 10 canonical statuses.
8. Execute 3-path remediation loop (Evidence fix, Human decision gate, Runtime unverified).
9. Update `state/migration-state.yml` authoritatively and generate reports in `reports/migration/<MODULE_NAME>/`.

### Mode 2: Global Workspace Orchestration (`orchestrate`)
1. Verify Preflight validation (`reports/preflight/`).
2. Read `state/migration-state.yml` for active lifecycle phase and component statuses.
3. Calculate dynamic waves (`wave_0` ... `wave_N`) from dependency in-degrees.
4. Dispatch specialist tasks for active wave components (or execute inline), serializing shared file writes.
5. Advance waves as components reach terminal states until 100% complete.
6. Dispatch final audit and generate `reports/final/FINAL-MIGRATION-SUMMARY.md`.
