---
description: Run a read-only discovery audit on the configured Drupal 7 and Drupal 10 environments.
---

# Drupal Migration: Discover

Execute the `discovery` agent to scan the source Drupal 7 and target Drupal 10 environments, inventorying modules, themes, entities, fields, and configuration without modifying any files.

## Instructions for Claude:

1. Check if `migration.config.yml` exists in the workspace.
   - If missing, prompt the user to copy `migration.config.example.yml` to `migration.config.yml`.
2. Ensure the Preflight Validation Gate (`commands/preflight.md`) passes before scanning:
   - Verify `source.path` and `target.path` exist, do not overlap, and contain valid Drupal core markers (Rules 1 & 2).
   - If Preflight fails, halt execution and display remediation steps from `reports/preflight/`.
3. **Strict Path Confinement & Zero-Search Boundary (Rule 16 & Rule 18)**:
   - Scan custom modules strictly under `<source.path>/<source.custom_modules_path>/` and themes under `<source.path>/<source.custom_themes_path>/`.
   - Broad recursive searching outside the configured `source.path` and `target.path` is strictly prohibited.
4. Treat both source and target environments as strictly READ-ONLY during discovery (Rule 1).
5. Activate the `discovery` agent (`agents/discovery/agent.md`) to inspect the systems.
6. Populate `state/migration-manifest.yml` with the discovered component inventory and initialize their runtime status in `state/migration-state.yml` as `DISCOVERED`.
7. Generate the comprehensive audit report in `reports/discovery/DISCOVERY-AUDIT-<DATE>.md` using `templates/discovery-report.md`.
8. Present an executive summary of findings to the user.

