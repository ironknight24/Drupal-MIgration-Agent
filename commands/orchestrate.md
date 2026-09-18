---
description: Start or resume the end-to-end Drupal 7 to Drupal 10/11 migration workflow.
---

# Drupal Migration: Orchestrate

Run the master orchestrator to manage the complete, dependency-aware Drupal 7 to Drupal 10/11 migration lifecycle.

## Instructions for Claude:

1. Check if `migration.config.yml` exists in the workspace.
   - If not found, prompt the user to provide the paths to the Drupal 7 source directory and Drupal 10 target directory, and create `migration.config.yml`.
2. Inspect `state/migration-state.yml` to determine current progress:
   - If `global_block` is `true`, halt and display the blocker from `reports/blocked/BLOCKED-000-GLOBAL.md`.
   - If resuming an existing migration, identify incomplete phases and components in `state/migration-manifest.yml`.
3. Activate the `orchestrator` agent (`agents/orchestrator.md` / `agents/orchestrator/agent.md`) to sequence tasks.
4. Strictly follow all rules in `SAFETY_RULES.md` and `AGENT_PROTOCOL.md`.
5. Report progress to the user at each phase boundary.
