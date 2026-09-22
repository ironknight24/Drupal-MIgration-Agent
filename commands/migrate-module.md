---
description: Migrate exactly one selected Drupal 7 custom module into Drupal 10/11 with dependency gating, write isolation, and forensic verification.
---

# Drupal Migration: Migrate Single Module

Execute an isolated, dependency-aware, forensics-backed migration for exactly **ONE** selected Drupal 7 custom module without migrating the rest of the workspace.

```text
/drupal-migration-agent:migrate-module <MODULE_NAME>
```
*Alias:* `/migrate-module <MODULE_NAME>`

---

## Instructions for Claude:

### 1. Argument Validation & Explicit Selection
1. Parse the command argument for `<MODULE_NAME>`:
   - If no module name is provided, **HALT** immediately with an error:
     ```text
     [ERROR] Missing required argument: <MODULE_NAME>
     Usage: /drupal-migration-agent:migrate-module <MODULE_NAME>
     Example: /drupal-migration-agent:migrate-module ariba_helper
     ```
   - Do **NOT** interpret a missing argument as "migrate everything". Do **NOT** fall back to `/orchestrate`.
2. Check if `migration.config.yml` exists. If missing, prompt user to copy `migration.config.example.yml`.
3. Check `state/migration-manifest.yml`. Verify that `<MODULE_NAME>`:
   - Exists in the inventory.
   - Is categorized as a `custom_module` (not a core, contrib, or theme component).
   - Is within the configured migration scope.
   - If not found in manifest, prompt user to run `/discover` first.

---

### 2. Preflight Validation Gate
1. Execute Preflight verification (`commands/preflight.md`):
   - Confirm `source.path` and `target.path` exist and do not collide (Checks `PRE-01` through `PRE-06`, `PRE-08`, `PRE-09`).
   - If Preflight fails, **HALT** immediately and display remediation steps from `reports/preflight/`.

---

### 3. Upstream Dependency Analysis & Gating
1. Read dependency metadata for `<MODULE_NAME>` from `state/migration-manifest.yml` and `reports/dependencies/`:
   - Categorize dependencies into:
     - **A. Core / Contrib dependencies**: Verify compatibility with target Drupal version.
     - **B. D7 Custom Module dependencies**: Identify all custom modules upon which `<MODULE_NAME>` depends.
2. For every custom module dependency $D$:
   - Check the runtime state of $D$ in `state/migration-state.yml`.
   - If any custom dependency $D$ is **NOT** in `COMPLETED` or `VALIDATED` state:
     - Do **NOT** silently migrate $D$.
     - Mark `<MODULE_NAME>` as `BLOCKED_UPSTREAM` in `state/migration-state.yml`.
     - Generate a blocker ticket in `reports/blocked/BLOCKED-<MODULE_NAME>-001-UPSTREAM.md`.
     - Report to user:
       ```text
       [BLOCKED_UPSTREAM] Module '<MODULE_NAME>' cannot be migrated because upstream custom module dependency '$D' has not been migrated yet.
       Please migrate '$D' first using: /drupal-migration-agent:migrate-module $D
       ```
     - **HALT** execution.

---

### 4. Target Module Snapshot & Idempotency Check
1. Resolve target module directory: `<target_custom_modules_path>/<MODULE_NAME>/`.
2. Check existing state in `state/migration-state.yml`:
   - If `<MODULE_NAME>` is already `COMPLETED`:
     - If user did not pass `--force` or explicit re-run intent, notify user that module is already migrated and offer re-validation.
3. If target module directory `<target_custom_modules_path>/<MODULE_NAME>/` already exists on disk:
   - Snapshot existing files, calculate file list and checksums.
   - Tag status as `EXISTING_TARGET_MODULE` (vs `NEW_TARGET_MODULE`).
   - Reconcile legacy D7 functionality against existing D10 implementation rather than blindly overwriting.

---

### 5. D7 Source Baseline & Forensics
1. Conduct exhaustive read-only inspection of D7 source at `<source_custom_modules_path>/<MODULE_NAME>/`:
   - Scan all `.module`, `.install`, `.inc`, `.php`, `.info`, `.js`, `.css`, template, and asset files.
   - Catalog all functions, procedural hooks, custom OOP classes, constructors, methods, forms, routes, permissions, database queries (`hook_schema`), entity definitions, cache bins/tags, and external integrations.
2. Create baseline report in `reports/migration/<MODULE_NAME>/<MODULE_NAME>_D7_BASELINE.md`.

---

### 6. Module-Scoped Migration Plan
1. Generate detailed migration plan in:
   - `reports/custom-modules/PLAN-<MODULE_NAME>.md`
   - `reports/migration/<MODULE_NAME>/<MODULE_NAME>_MIGRATION_PLAN.md`
2. Include:
   - Files to create, modify, or retire.
   - D7 API $\to$ D10/D11 PSR-4 architecture mapping.
   - Service container definitions (`.services.yml`) and constructor Dependency Injection.
   - Form classes (`FormBase`, `ConfigFormBase`), routes (`.routing.yml`), permissions (`.permissions.yml`).
   - Cache modernization (cache bins $\to$ `@cache.default` / cache tags / cache contexts).
   - Any required external changes outside the module recorded as `REQUIRES_EXTERNAL_CHANGE` (do not modify external files).
3. If `agents.require_plan_before_modification` is `true`, present plan to user for approval before writing code.

---

### 7. Scoped Migration Execution
1. Dispatch `custom-module` agent (`agents/custom-module/agent.md`) with:
   - `component_id`: `<MODULE_NAME>`
   - `execution_scope`: `SINGLE_MODULE`
   - `target_dir`: `<target_custom_modules_path>/<MODULE_NAME>/`
2. **Strict Write Boundary Enforcement**:
   - Authorized write target: **ONLY** `<target_custom_modules_path>/<MODULE_NAME>/**/*` and `reports/migration/<MODULE_NAME>/*`.
   - **FORBIDDEN WRITES**: D7 source (strictly READ-ONLY), other custom modules, contrib modules, Drupal core, vendor, themes, global config.
   - Log all created/updated files in `logs/file-change-log/`.

---

### 8. Post-Migration Forensic Audit & Validation
1. Execute module-scoped static checks on `<target_custom_modules_path>/<MODULE_NAME>/`:
   - Validate PHP syntax on all generated `.php` and `.module` files.
   - Validate YAML syntax on `.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `.libraries.yml`.
   - Check PSR-4 namespace compliance (`Drupal\<MODULE_NAME>\...`).
2. Perform D7 $\to$ D10 Functional Completeness Audit:
   - Match 100% of discovered D7 functions, hooks, classes, forms, and database interactions to D10 implementations.
   - Assign each item an evidence-based outcome: `MIGRATED`, `PARTIALLY_MIGRATED`, `NOT_MIGRATED`, `SUPERSEDED`, `INTENTIONALLY_REMOVED`, `BLOCKED`, or `UNVERIFIED`.
   - Check cache preservation: ensure D7 cache bins and cache operations have modern D10 cache tag/invalidation equivalents.
3. Generate evidence artifacts in `reports/migration/<MODULE_NAME>/`:
   - `<MODULE_NAME>_FUNCTION_MAP.md`
   - `<MODULE_NAME>_FUNCTION_MAP.yml`
   - `<MODULE_NAME>_DEPENDENCY_ANALYSIS.md`
   - `<MODULE_NAME>_POST_MIGRATION_AUDIT.md`
   - `<MODULE_NAME>_GAP_ANALYSIS.md`
   - `<MODULE_NAME>_FINAL_VERDICT.md`

---

### 9. State Mutation & Safety Sign-Off
1. Verify with filesystem / git inspection that:
   - **Zero** D7 files were modified.
   - **Zero** custom modules other than `<MODULE_NAME>` were touched.
   - **Zero** themes or global configs were touched.
   - If any unexpected file was modified $\to$ mark `SAFETY_VIOLATION` and halt.
2. The Orchestrator authoritatively updates `component_states.<MODULE_NAME>` in `state/migration-state.yml`:
   - Set status to `COMPLETED` (or `COMPLETED_WITH_GAPS` if non-material gaps documented).
   - Record timestamp, files changed count, and evidence links.
   - Leave all other component states completely untouched.
3. Present executive summary and final verdict to user.
