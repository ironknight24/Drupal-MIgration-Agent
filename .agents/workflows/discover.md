# Antigravity Workflow: Discovery Audit

## Purpose
Executes a strictly read-only inspection of source Drupal 7 and target Drupal 10 environments, inventorying modules, themes, entities, fields, hooks, classes, database schemas, configuration, state, and external code without mutating any files.

## Trigger & Invocation
This workflow is triggered via either slash commands or natural language conversation:

- **Slash Command**: `/discover`
- **Conversational Triggers / Natural Intent**:
  - `discover`
  - `run discovery`
  - `run discovery scan`
  - `perform codebase discovery`
  - `inspect drupal 7 codebase`
  - `inventory legacy components`
- **Corresponding Claude Command**: `commands/discover.md`

## Operational Procedure
1. Check that `migration.config.yml` exists and Preflight validation passes.
2. Maintain strictly READ-ONLY access to `source.path` and `target.path`.
3. Activate the Discovery protocol using `skills/d7-analysis/SKILL.md`:
   - Inventory custom modules, contrib modules, and themes.
   - Extract procedural hooks (9 types), custom OOP PHP classes (22 types), constructors, and include hierarchies.
   - Inventory database schemas (`hook_schema`), entities, bundles, fields, revisions, and translations.
   - Scan for external Drupal-integrated PHP scripts outside standard directories (Section 102 multi-vector evidence).
4. Populate `state/migration-manifest.yml` with the static inventory.
5. Initialize component states in `state/migration-state.yml` to `DISCOVERED`.
6. Author `reports/discovery/DISCOVERY-AUDIT-<DATE>.md` using `templates/discovery-report.md`.
