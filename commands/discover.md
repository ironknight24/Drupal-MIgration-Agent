---
description: Run a read-only discovery audit on the configured Drupal 7 and Drupal 10 environments.
---

# Drupal Migration: Discover

Execute the `discovery` agent to scan the source Drupal 7 and target Drupal 10 environments, inventorying modules, themes, entities, fields, and configuration without modifying any files.

## Instructions for Claude:

1. Read `migration.config.yml` to identify `source.path` and `target.path`.
2. Validate that `source.path` exists and does not overlap with `target.path` (Rule 1 & Rule 2).
3. Treat both environments as strictly READ-ONLY (Rule 1).
4. Activate the `discovery` agent (`agents/discovery/agent.md`) to inspect the systems.
5. Populate `state/migration-manifest.yml` with the discovered component inventory and initialize their runtime status in `state/migration-state.yml` as `DISCOVERED`.
6. Generate the comprehensive audit report in `reports/discovery/DISCOVERY-AUDIT-<DATE>.md` using `templates/discovery-report.md`.
7. Present an executive summary of findings to the user.

