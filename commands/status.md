---
description: Display current migration lifecycle phase, component progress, and active blockers.
---

# Drupal Migration: Status

Display the real-time operational status of the migration from `state/migration-state.yml` and `state/migration-manifest.yml`.

## Instructions for Claude:

1. Read `state/migration-state.yml`:
   - Identify `lifecycle_phase`, `current_wave`, and overall execution status (`NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`, `COMPLETE_WITH_GAPS`).
   - List active dynamic wave components, wave in-progress counts, and wave completed counts.
   - List any active items in `active_blockers` with their classification and remediation stages.
2. Read `state/migration-manifest.yml`:
   - Summarize component counts across the 15 canonical states (`NOT_STARTED`, `DISCOVERED`, `ANALYZED`, `PLANNED`, `SCAFFOLDED`, `IN_PROGRESS`, `CODE_COMPLETE`, `TESTING`, `TESTS_PASSED`, `VALIDATING`, `VALIDATED`, `COMPLETED`, `BLOCKED`, `BLOCKED_UPSTREAM`, `SKIPPED`).
   - Group counts by category (custom modules, contrib modules, themes, configuration, data migrations).
3. Check `logs/file-change-log/` for the latest file modifications.
4. Output a concise status dashboard in tabular format.

