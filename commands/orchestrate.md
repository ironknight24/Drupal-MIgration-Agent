---
description: Start or resume the end-to-end Drupal 7 to Drupal 10/11 migration workflow.
---

# Drupal Migration: Orchestrate

Run the master orchestrator to manage the complete, dependency-aware, dynamically sequenced Drupal 7 to Drupal 10/11 migration lifecycle.

## Instructions for Claude:

1. Check if `migration.config.yml` exists in the workspace.
   - If not found, prompt the user to provide the paths to the Drupal 7 source directory and Drupal 10 target directory, and create `migration.config.yml`.
2. Inspect `state/migration-state.yml` to determine current progress:
   - If `execution_health.status` is `BLOCKED`, inspect `active_blockers` and target remediation stages in `reports/blocked/`.
   - If resuming an existing migration, determine the lowest incomplete lifecycle phase and identify components in non-terminal states (`NOT_STARTED`, `READY`, `PLANNED`, `SCAFFOLDED`, `IN_PROGRESS`, `CODE_COMPLETE`, `TESTING`, `VALIDATING`).
3. Compute or resume dynamic DAG waves (`current_wave`) from `state/migration-manifest.yml` dependencies.
4. Activate the `orchestrator` agent (`agents/orchestrator/agent.md`) to dispatch tasks wave-by-wave, enforcing single-writer state serialization.
5. Strictly follow all rules in `SAFETY_RULES.md`, `AGENT_PROTOCOL.md`, and `MIGRATION_LIFECYCLE.md`.
6. Report progress to the user at each phase and dynamic wave boundary.

