---
name: custom-module-migration
description: End-to-end modernization methodology for migrating Drupal 7 custom modules, procedural hooks, database schemas, configuration variables, entities, forms, AJAX interactions, frontend assets, Views/custom plugins, theme presentation layers, dynamic runtime dependencies, external system integrations, cache metadata, sessions, security, and runtime lifecycle into PSR-4 Drupal 10/11 modules.
version: 1.12.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files. It enforces:
1. **Mandatory Step 0 Zero-Search Exact Path Derivation (Rule 18)**: Construct `SOURCE_MODULE_PATH = os.path.join(source.path, source.custom_modules_path, MODULE)` and `TARGET_MODULE_PATH = os.path.join(target.path, target_custom_modules_path, MODULE)` strictly from `migration.config.yml`. Never run broad workspace searches (`glob`, `grep`, `find .`) across root or sibling directories.
2. **Strict Path Boundary Confinement (Rule 16)**: All source reads are strictly confined to `SOURCE_MODULE_PATH` and target operations to `TARGET_MODULE_PATH`. The agent is strictly prohibited from searching, reading, or referencing files in adjacent directories, sibling folders, parent directories, or backup repositories outside the configured paths.
3. **From-Scratch Scaffolding Protocol (`NEW_TARGET_MODULE`, Rule 17)**: When `<MODULE>` is absent in `<target.path>`, the agent scaffolds the modern D10 module from the ground up inside `TARGET_MODULE_PATH`, faithfully reproducing legacy business behavior, caching mechanisms (bubbleable cache tags, contexts, max-age), security controls (permissions, access checkers, CSRF, output sanitization), and inter-module interactions using 100% pure modern Drupal 10/11 standards (PSR-4, Constructor Dependency Injection, CMI YAML, Twig).
4. **Existing Target Reconciliation (`EXISTING_TARGET_MODULE`)**: When `<MODULE>` already exists in `TARGET_MODULE_PATH`, the agent reconciles gaps surgically without destroying working D10 implementations.

---

## Technical References & Associated Skills
- Associated Skills:
  - [`skills/d7-analysis`](../d7-analysis/SKILL.md)
  - [`skills/d7-to-d10-mapping`](../d7-to-d10-mapping/SKILL.md)
  - [`skills/configuration-migration`](../configuration-migration/SKILL.md)
  - [`skills/migration-api`](../migration-api/SKILL.md)
  - [`skills/d10-architecture`](../d10-architecture/SKILL.md)
  - [`skills/dependency-analysis`](../dependency-analysis/SKILL.md)
- Canonical References:
  - [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
  - [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)
  - [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)
  - [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)

---

## Target-Version Resolution
Determine target version from project configuration (`target.core_version`):
- For **Drupal 10.x**: Target PHP >= 8.1; use DocBlock annotations or PHP Attributes where supported.
- For **Drupal 11.x**: Target PHP >= 8.3; prefer PHP 8 Attributes for all supported plugins; ensure strict return types.

---

## The 13-Step Modernization Playbook

1. **Step 1: Exact Path Derivation, Recursive Inventory & Source Discovery**
   - Read `migration.config.yml` and compute `SOURCE_MODULE_PATH = os.path.join(source.path, source.custom_modules_path, MODULE)`.
   - Confine file scanning strictly to `SOURCE_MODULE_PATH` without broad searches across adjacent folders.
   - Recursively catalog all source files (`.info`, `.module`, `.inc`, `.install`, `*.php`, `*.profile`, `.drush.inc`, `.js`, `.css`, `*.views_default.inc`, `*.views.inc`) across root and subdirectories (`includes/`, `lib/`, `classes/`, `src/`, `admin/`, `commands/`, `views/`, etc.).
   - Dissect every custom PHP file, class, interface, trait, constructor, procedural hook implementation, custom entity type, field definition, revision mechanism, translation setting, form builder, form alter, AJAX callback, configuration/state access, frontend behavior, Views definition / custom handler plugin, external system integration, and runtime behavior.
   - Catalog discovered artifacts into the respective taxonomies (9-type hook taxonomy, 20-type configuration taxonomy, 26-target entity taxonomy, 19-target form/AJAX taxonomy, 21-target frontend taxonomy, 30-target Views taxonomy, 35-target dynamic taxonomy, 35-target integration taxonomy, 40-target runtime taxonomy).

2. **Step 2: Dependency, Target Environment Introspection, Hook Invocation & Config Lifecycle Mapping**
   - **Target `composer.json` & Contrib Introspection**: Parse `<target.path>/composer.json`, `<target.path>/composer.lock`, and `<target.path>/web/modules/contrib/` to discover all installed Drupal core subsystems, contrib packages, and third-party libraries available in the target site.
   - **Continuous Auto-Resolution Protocol**:
     - Check if D7 dependency was absorbed into D10 core (e.g. `entityreference`, `date`, `views`, `ctools` plugin types, `block_class`) $\to$ auto-map to modern Core API.
     - Check if D7 dependency replacement is in target `composer.json` (e.g. `drupal/group`, `drupal/paragraphs`, `drupal/token`, `drupal/key`) $\to$ inspect installed `.services.yml` and classes to auto-map calls without raising blockers.
     - Only escalate to `HUMAN_INTERVENTION_REQUIRED` if a dependency is completely absent from both D10 core and target `composer.json` and cannot be resolved from available project information.
   - Map inter-file and inter-module calls to custom classes (`new ClassName()`, static calls), procedural functions, custom hook subscribers/callers, entity reference topologies, form callers, AJAX endpoints, Views handlers, configuration reads/writes/deletes, and external system egress/ingress.
   - Analyze hook execution order, module weights (`{system}.weight`), alter sequencing (`hook_module_implements_alter`), entity reference hierarchy, variable lifecycle (`CREATE -> READ -> MODIFY -> DELETE`), external integration DAG edges, and runtime lifecycle edges.

3. **Step 3: Business Behavior, Hook Dissection, Form & Entity/Configuration Decomposition**
   - Extract discrete functional units from custom PHP classes, `.inc` files, procedural hooks, custom entities, field definitions, form builders, configuration forms, default Views, external integration handlers, and runtime callbacks.
   - Decompose `hook_menu()` implementations into discrete routes, controllers, form classes (`src/Form/`), access checkers, menu links, local tasks, local actions, contextual links, REST resource endpoints, and webhook callback receivers.
   - Decompose `system_settings_form()` into `ConfigFormBase` classes, typed schemas (`config/schema/*.schema.yml`), default configuration (`config/install/*.yml`), and menu routes.
   - Decompose `confirm_form()` into `ConfirmFormBase` classes.
   - Decompose custom D7 entities into Content Entity classes (`src/Entity/`), interfaces, access control handlers, view builders, and field definitions.
   - Decompose default Views and `hook_views_default_views()` into CMI configuration files (`config/install/views.view.*.yml`).

4. **Step 4: Legacy API Audit, Constructor Inspection, Form API, Entity & State Analysis**
   - Audit constructors (`__construct()` and legacy `ClassName()`): extract parameters, global references (`$user`, `$conf`), and procedural calls (`variable_get()`, `db_query()`, `entity_load()`, `drupal_get_form()`, `views_get_view()`, `drupal_http_request()`).
   - Audit legacy Drupal 7 procedural APIs (`variable_get()`, `variable_set()`, `variable_del()`, `entity_load()`, `entity_save()`, `field_info_field()`, `EntityFieldQuery`, `drupal_get_form()`, `ajax_render()`, `ajax_command_*()`, `views_get_view()`, `views_embed_view()`, `drupal_http_request()`, `curl_exec()`, `xmlrpc()`, `cache_get()`, `cache_set()`, `lock_acquire()`).
   - Distinguish Content Entities vs Config Entities vs Configuration (CMI) vs State (State API) vs Forms vs Views vs Cache vs External Integrations vs Runtime.
   - Inspect custom database schemas in `hook_schema()`: column definitions, primary keys, indexes, foreign keys, revision tables, data tables, and entity reference columns (`uid`, `nid`, `tid`, `fid`, `entity_id`).
   - Audit all procedural database queries (`db_query()`, `db_select()`, `db_insert()`, `db_update()`, `db_delete()`, `db_merge()`, `db_transaction()`, `EntityFieldQuery`, `hook_views_query_alter()`) for dynamic SQL, external database queries, and parameter safety.

5. **Step 5: Modern Architecture Design (Non-1:1 Mapping, Data Models, Entities, Forms, AJAX, CMI, Views & PSR-4)**
   - Re-engineer functionality into modern Symfony/Drupal OOP architectures rather than 1:1 file renaming, fully supporting non-1:1 mappings (one-to-many transformations where a single legacy hook/table decomposes into multiple routes, services, or forms; and many-to-one transformations where multiple procedural hooks or tables consolidate into a unified service or entity repository):
     - D7 custom entity with tables $\rightarrow$ D10 Content Entity in `src/Entity/` (`@ContentEntityType`) with base field definitions, revision support, translation support, and access handler
     - D7 bundle / type configuration $\rightarrow$ D10 Config Entity (`@ConfigEntityType`) in `src/Entity/`
     - D7 fields $\rightarrow$ D10 Base Fields (`baseFieldDefinitions`) or Config Fields (`field.storage.*.yml`, `field.field.*.yml`)
     - D7 standard form builder $\rightarrow$ D10 `FormBase` class in `src/Form/`
     - D7 admin settings form / `system_settings_form()` $\rightarrow$ D10 `ConfigFormBase` in `src/Form/` + `config/install/*.yml` + `config/schema/*.schema.yml`
     - D7 confirmation form / `confirm_form()` $\rightarrow$ D10 `ConfirmFormBase` in `src/Form/`
     - D7 entity edit/add form $\rightarrow$ D10 `ContentEntityForm` in `src/Form/` or registered entity form handler
     - D7 AJAX callback / commands $\rightarrow$ D10 `AjaxResponse` method returning `CommandInterface` objects
     - D7 client-side JavaScript / `Drupal.behaviors` $\rightarrow$ D10 `once()` behavior in `js/` registered in `<module>.libraries.yml` with `core/drupal`, `core/drupalSettings`, `core/once`
     - D7 `Drupal.settings` / `drupal_add_js(..., 'setting')` $\rightarrow$ D10 `#attached['drupalSettings']` + client `drupalSettings`
     - D7 CSS stylesheets / `.info` stylesheets $\rightarrow$ D10 SMACSS structured `<module>.libraries.yml` definitions in `css/`
     - D7 Views definition / `hook_views_default_views()` $\rightarrow$ D10 CMI View in `config/install/views.view.<view_id>.yml`
     - D7 custom Views handler / plugin (`views_handler_*`, `views_plugin_*`) $\rightarrow$ D10 annotated plugin class in `src/Plugin/views/` (`@ViewsField`, `@ViewsFilter`, `@ViewsArgument`, `@ViewsSort`, `@ViewsRelationship`, `@ViewsArea`, `@ViewsPager`, `@ViewsAccess`, `@ViewsQuery`, `@ViewsStyle`, `@ViewsRow`, `@ViewsDisplay`)
     - D7 Views data definition (`hook_views_data`) $\rightarrow$ D10 `hook_views_data()` in `<module>.views.inc`
     - D7 Views query alteration (`hook_views_query_alter`) $\rightarrow$ D10 `hook_views_query_alter()` operating on `Sql` query plugin
     - D7 form alter (`hook_form_alter`) $\rightarrow$ D10 `hook_form_alter()` or Event Subscriber
     - D7 business logic class / function / procedural hook $\rightarrow$ D10 Service class in `src/Service/` registered in `.services.yml`
     - D7 page callback from `hook_menu()` $\rightarrow$ D10 Controller in `src/Controller/`
     - D7 runtime state / flag / timestamp $\rightarrow$ D10 State API (`StateInterface` / `\Drupal::state()`)
     - D7 secrets / credentials / environment values $\rightarrow$ `settings.php` overrides / `getenv()` / Key module (Rule 10: zero secrets in CMI)
     - D7 custom hook invocation (`module_invoke_all`) $\rightarrow$ Symfony EventDispatcher event dispatching with custom `Event` class and `EventSubscriberInterface`
     - D7 external HTTP / API calls (`drupal_http_request()`, cURL) $\rightarrow$ Guzzle Client (`\GuzzleHttp\ClientInterface`) inside dedicated Gateway Services (`src/Service/`)
     - D7 webhook receivers / IPN callbacks $\rightarrow$ Symfony Webhook Controller (`src/Controller/WebhookController.php`) with HMAC signature verification
     - D7 external file transfers / remote storage $\rightarrow$ Flysystem stream wrappers (`@FlysystemStreamWrapper`)
     - D7 external CLI binaries (`exec()`, `shell_exec()`) $\rightarrow$ Symfony `Process` component (`Symfony\Component\Process\Process`)
     - D7 procedural cache operations $\rightarrow$ Injected CacheBackend services with bubbleable cache tags/contexts/max-age
     - D7 routing access callbacks $\rightarrow$ Custom Access Checker services implementing `AccessInterface`

6. **Step 6: Dynamic, Runtime & Data-Driven Dependency Alignment (Step 21)**
   - Account for all dynamic callables, variable functions, dynamic class instantiations, dynamic hooks, dynamic entity/field types, and serialized payloads.
   - Re-engineer dynamic function dispatches to Plugin Managers (`DefaultPluginManager`) or tagged service collections.
   - Specify deterministic, safe runtime probes for runtime-dependent artifacts and mark unverified probes with explicit boundary markers.

7. **Step 7: External Integrations, APIs, Webhooks & Third-Party System Alignment (Step 22)**
   - Account for all outbound HTTP/API calls, inbound REST/JSON endpoints, webhook receivers, authentication mechanisms, and external SDKs.
   - Enforce Rule 10 secret isolation: replace hardcoded credentials or `variable_get()` keys with Drupal Key module references or environment variables.
   - Re-engineer procedural HTTP and remote storage into Guzzle Gateway Services, Symfony Webhook Controllers, and Flysystem stream wrappers.
   - Preserve timeout settings, retry logic (exponential backoff), idempotency headers, and error handling behaviors.

8. **Step 8: Cache, Session, Security, Access Checkers & Runtime Lifecycle Alignment (Step 23)**
   - Account for all caching operations, cache invalidation hooks, static caches, session usages, cookie handlers, temporary stores, routing access checks, permission checks, entity/field access hooks, CSRF tokens, output sanitization, locking APIs, database transactions, and bootstrap/shutdown lifecycle hooks.
   - Modernize caching to bubbleable cache metadata (`#cache['tags']`, `#cache['contexts']`, `#cache['max-age']`).
   - Modernize sessions to Symfony `SessionInterface` / `tempstore.private`.
   - Modernize access callbacks to `AccessCheckInterface` services.
   - Modernize lifecycle hooks (`hook_boot()`, `hook_init()`) to Symfony `KernelEvents` event subscribers.

9. **Step 9: Migration Plan Formulation & Complete Accounting Matrix**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
   - Maintain an explicit File/Class/Hook/Database/Configuration/Entity/Form/Frontend/Views/Dynamic/Integration/Runtime Accounting Table showing the exact target class, service, entity, field config, form class, AJAX handler, library definition, JavaScript behavior, View configuration, custom Views plugin, dynamic plugin manager, config object, state key, event subscriber, plugin, webhook controller, gateway service, access checker, cache metadata, or routing artifact for every legacy item.

10. **Step 10: Controlled Implementation & Modernization**
    - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `.links.menu.yml`, `.links.task.yml`, `drush.services.yml`, `.libraries.yml`, `.views.inc`).
    - Generate default configuration (`config/install/<module>.settings.yml`), schema (`config/schema/<module>.schema.yml`), field definitions (`config/install/field.storage.*`, `field.field.*`), and Views definitions (`config/install/views.view.*.yml`).
    - Implement entity classes (`src/Entity/`), access handlers, storage handlers, services, controllers, form classes (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`), AJAX handlers, JavaScript `once()` behaviors (`js/`), SMACSS stylesheets (`css/`), `.libraries.yml` definitions, custom Views plugins (`src/Plugin/views/`), dynamic plugin managers (`src/Plugin/`), gateway services (`src/Service/`), webhook controllers (`src/Controller/`), access checkers (`src/Access/`), event subscribers, plugins, repository classes, and Drush classes strictly inside `target.path/web/modules/custom/<MODULE>/`.
    - Delegate scoped complex service authoring, DI modernization, and database query modernization to `api-modernization` where required.
    - Log all file creations and modifications in `logs/file-change-log/`.

11. **Step 11: Automated Testing**
    - Author PHPUnit Unit and Kernel tests targeting modernized entities (CRUD, revisions, translations), field storage, services, controllers, form submissions (`submitForm()`), form validation (`validateForm()`), AJAX response commands, JavaScript/CSS library registrations, Views configuration schemas, custom Views plugin executions, query alterations, configuration schemas, state persistence, event subscribers, dynamic plugin managers, runtime probes, gateway services (with Guzzle MockHandler), webhook signature verification, access checkers, cache tag invalidation, session handling, repositories, and entities using `skills/testing`.

12. **Step 12: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
    - Verify that every discovered custom PHP file, class, method, function, procedural hook, custom database table, configuration/state variable, entity type, field, form builder, form alter, AJAX callback, JavaScript behavior, CSS asset, View definition, custom Views plugin, dynamic dependency, external integration, and runtime behavior has an explicit modern equivalent or valid reason.

13. **Step 13: Gap Analysis, Outcome Accounting & 3-Path Remediation**
    - Verify that every custom PHP file, class, function, procedural hook implementation, custom database table, configuration/state artifact, entity type, field, form, AJAX callback, frontend asset, View definition, Views plugin, dynamic dependency, external integration, and runtime behavior item is classified under one of the 10 canonical item statuses:
      `COMPLETE`, `PARTIAL`, `MISSING`, `BLOCKED`, `HUMAN_INTERVENTION_REQUIRED`, `RUNTIME_UNVERIFIED`, `SUPERSEDED`, `REPLACED`, `OBSOLETE`, or `EXCLUDED`.
    - Reject any `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, or `SILENTLY_OMITTED` items.
    - Evaluate gaps via the **3-Path Remediation Engine**:
      - **Path 1 (FIXABLE FROM EVIDENCE)**: Generate structured remediation tasks with stable IDs, implement code fixes within the module write boundary, and re-audit (up to `max_remediation_iterations: 3`).
      - **Path 2 (REQUIRES HUMAN DECISION)**: Transition to `HUMAN_INTERVENTION_REQUIRED` for ambiguous business logic, GDPR policy, or architecture trade-offs. Never invent business requirements.
      - **Path 3 (RUNTIME UNAVAILABLE)**: Mark dynamic behaviors as `RUNTIME_UNVERIFIED` and continue static verification.
    - Generate `reports/custom-modules/REPORT-<MODULE>.md` and `reports/migration/<MODULE>/<MODULE>_FINAL_VERDICT.md` containing the structured `## LLM REMEDIATION INPUT` section.
    - Propose updating component status to `COMPLETE` (or `PARTIAL`/`BLOCKED`/`HUMAN_INTERVENTION_REQUIRED`) via `agent_result`.

---

## 14. Targeted Single-Module Migration Protocol (`/orchestrate <MODULE>` or `/migrate-module <MODULE>`)

When invoked in targeted single-module mode:

1. **Target Module Identification & Manifest Validation**:
   - The agent strictly validates that `<MODULE>` exists in `state/migration-manifest.yml` as a `custom_module`.
2. **Recursive Upstream Custom Dependency Resolution**:
   - Inspect all declared and implicit custom module dependencies for `<MODULE>` and construct the ancestor sub-DAG.
   - Execute cycle detection. If a cycle is detected, halt with `BLOCKED-<MODULE>-001-CYCLE.md`.
   - Process unmigrated upstream dependencies in bottom-up topological order.
   - If an upstream dependency is `BLOCKED` or requires human input, mark `<MODULE>` as `BLOCKED_UPSTREAM` and halt.
3. **Pre-Migration Target Snapshot**:
   - If `<target_module_dir>/<MODULE>/` already exists, capture file inventory, line counts, and checksums, tagging the run as `EXISTING_TARGET_MODULE` (vs `NEW_TARGET_MODULE`).
4. **Strict Write Scope & Boundary Enforcement**:
   - Authorized write target is strictly `<target_module_dir>/<MODULE>/**/*` and `reports/migration/<MODULE>/*`.
   - Zero writes to D7 source (strictly read-only). Zero writes to other custom modules, contrib modules, themes, core, or global config.
   - If a supporting change outside the module is required, record it as `REQUIRES_EXTERNAL_CHANGE` in the plan and gap analysis without modifying external files.
5. **Standard Evidence Artifacts & LLM Remediation Input**:
   - In single-module mode, generate the comprehensive evidence suite under `reports/migration/<MODULE>/`:
     - `<MODULE>_D7_BASELINE.md`
     - `<MODULE>_MIGRATION_PLAN.md`
     - `<MODULE>_FUNCTION_MAP.md`
     - `<MODULE>_FUNCTION_MAP.yml`
     - `<MODULE>_DEPENDENCY_ANALYSIS.md`
     - `<MODULE>_POST_MIGRATION_AUDIT.md`
     - `<MODULE>_GAP_ANALYSIS.md`
     - `<MODULE>_FINAL_VERDICT.md` (including standard `## LLM REMEDIATION INPUT` with stable task IDs)
6. **State Mutation**:
   - The Orchestrator updates only `component_states.<MODULE>` in `state/migration-state.yml`, leaving all unrelated components unchanged.
