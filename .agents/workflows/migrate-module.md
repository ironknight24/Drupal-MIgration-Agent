# Antigravity Workflow: Migrate Single Module

## Purpose
Executes an isolated, recursive, dependency-aware, forensics-backed migration for exactly ONE selected Drupal 7 custom module.

## Trigger & Invocation
This workflow is triggered via either slash commands or natural language conversation:

- **Slash Commands**:
  - `/migrate-module <MODULE_NAME>`
  - `/orchestrate <MODULE_NAME>`
- **Conversational Triggers / Natural Intent**:
  - `migrate-module <MODULE_NAME>`
  - `migrate module <MODULE_NAME>`
  - `orchestrate <MODULE_NAME>`
  - `migrate custom module <MODULE_NAME>`
  - `modernize module <MODULE_NAME>`
- **Corresponding Claude Command**: `commands/migrate-module.md`

## Operational Procedure
1. Require explicit `<MODULE_NAME>` argument; never fall back to global migration if argument is omitted.
2. Verify preflight checks pass and `<MODULE_NAME>` is registered as a custom module in `state/migration-manifest.yml`.
3. Resolve upstream custom module dependencies recursively in topological order before migrating `<MODULE_NAME>`.
4. Enforce strict write boundary: mutations allowed ONLY under `<target_custom_modules_path>/<MODULE_NAME>/**/*` and `reports/migration/<MODULE_NAME>/*`.
5. Conduct forensic D7 source baseline audit (`reports/migration/<MODULE_NAME>/<MODULE_NAME>_D7_BASELINE.md`).
6. Author migration plan (`reports/migration/<MODULE_NAME>/<MODULE_NAME>_MIGRATION_PLAN.md`).
7. Execute modernization (or inline fallback): PSR-4 classes, constructor DI, route definitions, CMI configuration, Twig templates.
8. Audit behavioral parity across 12 dimensions; execute 3-path remediation loop; update `state/migration-state.yml`.
