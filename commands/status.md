---
description: Display current migration lifecycle phase, component progress, and active blockers.
---

# Drupal Migration: Status

Display the real-time operational status of the migration from `state/migration-state.yml` and `state/migration-manifest.yml`.

## Instructions for Claude:

1. Read `state/migration-state.yml`:
   - Identify `current_phase` and overall status (`initialized`, `in_progress`, `blocked`, `completed`).
   - List any active items in `active_blockers`.
2. Read `state/migration-manifest.yml`:
   - Summarize component counts by status (`completed`, `in_progress`, `blocked`, `not_started`).
   - Group counts by category (custom modules, contrib modules, themes, config, data migrations).
3. Check `logs/file-change-log/` for the latest file modifications.
4. Output a concise status dashboard in tabular format.
