---
description: Migrate exactly one selected Drupal 7 custom module into Drupal 10/11 with recursive dependency resolution, 3-path remediation, write isolation, and forensic verification.
---

# Drupal Migration: Migrate Single Module

Execute an isolated, recursive, dependency-aware, forensics-backed migration for exactly **ONE** selected Drupal 7 custom module.

```text
/drupal-migration-agent:migrate-module <MODULE_NAME>
```
*Alias:* `/migrate-module <MODULE_NAME>`, `/orchestrate <MODULE_NAME>`

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
   - Do **NOT** interpret a missing argument as "migrate everything". Do **NOT** fall back to global `/orchestrate`.
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

### 3. Recursive Dependency Resolution & Ordering
1. Read dependency metadata for `<MODULE_NAME>` from `state/migration-manifest.yml` and `reports/dependencies/`:
   - Categorize dependencies into:
     - **A. Core / Contrib dependencies**: Verify compatibility with target Drupal version.
     - **B. D7 Custom Module dependencies**: Identify all custom modules upon which `<MODULE_NAME>` depends.
2. Build the targeted module ancestor sub-DAG ($\text{Ancestors}(M) \cup \{M\}$):
   - Execute cycle detection. If a cycle is detected, emit `reports/blocked/BLOCKED-<MODULE_NAME>-001-CYCLE.md` and halt.
   - For every custom module dependency $D$:
     - Check the runtime state of $D$ in `state/migration-state.yml`.
     - If $D$ is in `COMPLETE` or `VALIDATED` state, skip.
     - If $D$ is unmigrated, recursively execute targeted migration on $D$ in bottom-up topological order before migrating $<MODULE_NAME>$.
     - If $D$ is `BLOCKED` or `HUMAN_INTERVENTION_REQUIRED`, mark $<MODULE_NAME>$ as `BLOCKED_UPSTREAM` in `state/migration-state.yml`, generate `reports/blocked/BLOCKED-<MODULE_NAME>-001-UPSTREAM.md`, and halt.

---

### 4. Target Module Snapshot, Path Confinement & Scaffolding Mode
1. **Strict Path Resolution & Boundary Lockdown**:
   - Resolve target module directory strictly as: `<target.path>/<target_custom_modules_path>/<MODULE_NAME>/`.
   - Resolve source module directory strictly within `<source.path>/.../<MODULE_NAME>/`.
   - **Adjacent Directory Prohibition**: The agent is strictly **FORBIDDEN** from inspecting, grepping, or referencing files in sibling folders, parent directories, or backup repositories outside the configured `source.path` and `target.path`.
2. Check existing state in `state/migration-state.yml`:
   - If `<MODULE_NAME>` is already `COMPLETE`:
     - If user did not pass `--force` or explicit re-run intent, notify user that module is already migrated and offer re-validation.
3. **Scaffolding Mode Selection**:
   - **Mode A: Existing Target Module (`EXISTING_TARGET_MODULE`)**:
     - If `<target.path>/<target_custom_modules_path>/<MODULE_NAME>/` already exists on disk:
       - Snapshot existing files, calculate file list and checksums.
       - Reconcile legacy D7 functionality against existing D10 implementation rather than blindly overwriting.
       - Surgically add missing services, routes, or classes without destroying existing working D10 code.
   - **Mode B: From-Scratch Module Generation (`NEW_TARGET_MODULE`)**:
     - If `<MODULE_NAME>` does **NOT** exist in `<target.path>`:
       - Scaffold the modern Drupal 10 module from scratch inside `<target.path>/<target_custom_modules_path>/<MODULE_NAME>/`.
       - Re-engineer 100% of the D7 module's business rules, calculations, and workflows.
       - Modernize caching to bubbleable cache metadata (`#cache['tags']`, `#cache['contexts']`, `#cache['max-age']`).
       - Modernize security (custom permissions, access checkers, CSRF tokens, output sanitization, Rule 10 secret isolation).
       - Modernize inter-module hooks and interactions into Symfony Event Subscribers and modern D10 hooks.
       - Implement strictly using modern Drupal 10 standards: PSR-4 autoloading, Constructor Dependency Injection, CMI YAML (`config/install/`), and Twig templates (`templates/`).

---

### 5. D7 Source Baseline & Forensics
1. Conduct exhaustive read-only inspection of D7 source strictly within `<source.path>/.../<MODULE_NAME>/`:
   - Scan all `.module`, `.install`, `.inc`, `.php`, `.info`, `.js`, `.css`, template, and asset files belonging to this module.
   - Never drift into adjacent modules or directories.
   - Catalog all functions, procedural hooks, custom OOP classes, constructors, methods, forms, routes, permissions, database queries (`hook_schema`), entity definitions, cache bins/tags, and external integrations.
2. Create baseline report in `reports/migration/<MODULE_NAME>/<MODULE_NAME_D7_BASELINE.md`.

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
   - `source_dir`: `<source.path>/.../<MODULE_NAME>/`
   - `target_dir`: `<target.path>/<target_custom_modules_path>/<MODULE_NAME>/`
2. **Strict Write Boundary Enforcement**:
   - Authorized write target: **ONLY** `<target.path>/<target_custom_modules_path>/<MODULE_NAME>/**/*` and `reports/migration/<MODULE_NAME>/*`.
   - **FORBIDDEN WRITES & READS**: Sibling directories, adjacent workspaces, D7 source (strictly READ-ONLY), other custom modules, contrib modules, Drupal core, vendor, themes, global config.
   - Log all created/updated files in `logs/file-change-log/`.

---

### 8. Forensic Completeness Audit & 3-Path Remediation Engine
1. Execute module-scoped static checks on `<target_custom_modules_path>/<MODULE_NAME>/`:
   - Validate PHP syntax on all generated `.php` and `.module` files.
   - Validate YAML syntax on `.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `.libraries.yml`.
   - Check PSR-4 namespace compliance (`Drupal\<MODULE_NAME>\...`).
2. Perform D7 $\to$ D10 Functional Completeness Audit:
   - Match 100% of discovered D7 functions, hooks, classes, forms, and database interactions to D10 implementations.
   - Assign each item one of the 10 canonical statuses: `COMPLETE`, `PARTIAL`, `MISSING`, `BLOCKED`, `HUMAN_INTERVENTION_REQUIRED`, `RUNTIME_UNVERIFIED`, `SUPERSEDED`, `REPLACED`, `OBSOLETE`, `EXCLUDED`.
3. Evaluate Findings via the **3-Path Remediation Engine**:
   - **Path 1: FIXABLE FROM EVIDENCE**:
     - Generate structured remediation tasks with stable IDs (e.g. `<MODULE>-ROUTE-001`, `<MODULE>-SERVICE-002`).
     - Re-enter execution loop to implement targeted fixes.
     - Re-validate and re-audit after each fix.
     - Enforce loop limits: `max_remediation_iterations` (default 3), `max_retries_per_component` (default 2).
   - **Path 2: REQUIRES HUMAN DECISION**:
     - For ambiguous business logic, GDPR policy, or architecture trade-offs, transition to `HUMAN_INTERVENTION_REQUIRED`.
     - Halt execution, document options in `reports/human_decisions/`, and await user decision. Never invent business logic.
   - **Path 3: RUNTIME UNAVAILABLE**:
     - If runtime/DDEV is unavailable, mark dynamic items as `RUNTIME_UNVERIFIED`.
     - Proceed with static completion and log verification boundary.
4. Generate evidence artifacts in `reports/migration/<MODULE_NAME>/`:
   - `<MODULE_NAME>_FUNCTION_MAP.md`
   - `<MODULE_NAME>_FUNCTION_MAP.yml`
   - `<MODULE_NAME>_DEPENDENCY_ANALYSIS.md`
   - `<MODULE_NAME>_POST_MIGRATION_AUDIT.md`
   - `<MODULE_NAME>_GAP_ANALYSIS.md`
   - `<MODULE_NAME>_FINAL_VERDICT.md` (including standard `## LLM REMEDIATION INPUT` section)

---

### 9. State Mutation & Safety Sign-Off
1. Verify with filesystem / git inspection that:
   - **Zero** D7 files were modified.
   - **Zero** custom modules other than `<MODULE_NAME>` were touched.
   - **Zero** themes or global configs were touched.
   - If any unexpected file was modified $\to$ mark `SAFETY_VIOLATION` and halt.
2. The Orchestrator authoritatively updates `component_states.<MODULE_NAME>` in `state/migration-state.yml`:
   - Set status to `COMPLETE` (only when all items are `COMPLETE`, `SUPERSEDED`, `REPLACED`, `OBSOLETE`, `EXCLUDED`, or documented `RUNTIME_UNVERIFIED`).
   - If unfixable or blocked gaps exist, set status to `PARTIAL`, `BLOCKED`, or `HUMAN_INTERVENTION_REQUIRED`.
   - Record timestamp, files changed count, and evidence links.
   - Leave all other component states completely untouched.
3. Present executive summary and final verdict to user.
