---
description: Start or resume the end-to-end Drupal 7 to Drupal 10/11 migration workflow.
---

# Drupal Migration: Orchestrate

Run the master orchestrator to manage the complete, dependency-aware, dynamically sequenced Drupal 7 to Drupal 10/11 migration lifecycle.

## Instructions for Claude:

1. Check if `migration.config.yml` exists in the workspace.
   - If not found, instruct the user to copy `migration.config.example.yml` to `migration.config.yml` and provide source and target paths.
2. Execute the Preflight Validation Gate (`commands/preflight.md`):
   - Verify that all critical preflight checks (`PRE-01` through `PRE-06`, `PRE-08`, `PRE-09`) pass.
   - If Preflight fails (status `BLOCKED`), halt immediately and display required remediations from `reports/preflight/`.
3. Inspect `state/migration-state.yml` to determine current progress:
   - If `execution_health.status` is `BLOCKED`, inspect `active_blockers` and target remediation stages in `reports/blocked/`.
   - If resuming an existing migration, determine the lowest incomplete lifecycle phase and identify components in non-terminal states (`NOT_STARTED`, `READY`, `PLANNED`, `SCAFFOLDED`, `IN_PROGRESS`, `CODE_COMPLETE`, `TESTING`, `VALIDATING`).
4. Compute or resume dynamic DAG waves (`current_wave`) from `state/migration-manifest.yml` dependencies.
5. Activate the `orchestrator` agent (`agents/orchestrator/agent.md`) to dispatch tasks wave-by-wave, enforcing single-writer state serialization.
6. Strictly follow all rules in `SAFETY_RULES.md`, `AGENT_PROTOCOL.md`, and `MIGRATION_LIFECYCLE.md`.
7. Report progress to the user at each phase and dynamic wave boundary.

