---
name: d7-analysis
description: Procedural inspection heuristics for Drupal 7 modules, hooks, database schemas, legacy .inc files, and variables without mutating source files. Use when analyzing legacy Drupal 7 codebases.
version: 1.1.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Drupal 7 Codebase Analysis Skill

## Overview
This skill provides structured, non-destructive heuristics for inspecting Drupal 7 codebases, modules, themes, and database schemas. It explicitly discovers, dissects, and accounts for all source files—with exhaustive treatment of legacy `.inc` files—extracting business logic, callbacks, hook implementations, Drush commands, and dependencies to prepare for modern Drupal 10/11 re-engineering.

---

## Technical References
For deep technical catalogs, consult:
- [Drupal 7 Core APIs Reference](../../references/drupal-7/apis.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)

---

## Analysis Workflow & Heuristics

### 1. Recursive Source File Discovery & Inventory
For every custom module in scope, recursively discover all source files regardless of directory nesting:
- **Target File Extensions**: `*.module`, `*.inc`, `*.install`, `*.info`, `*.php`, `*.drush.inc`, `*.admin.inc`, `*.pages.inc`, `*.forms.inc`.
- **Zero Naming Assumptions**: Never assume `.inc` files follow fixed naming conventions. Discover files at the module root, in `includes/`, `admin/`, `forms/`, `pages/`, `plugins/`, `handlers/`, `commands/`, or arbitrary subdirectories (e.g., `module.inc`, `admin.inc`, `pages.inc`, `forms.inc`, `functions.inc`, `includes/foo.inc`, `includes/bar.inc`, `custom-command.inc`, `arbitrary-name.inc`).
- **Discovery Output**: Record relative path, file type, line count, and byte size in the module file manifest.

### 2. Include / Require & Relationship Graph Analysis
Trace how every discovered `.inc` and `.php` file is included, loaded, or referenced:
- **Include Mechanisms to Detect**:
  - Direct PHP includes: `include`, `include_once`, `require`, `require_once`.
  - Drupal module include helpers: `module_load_include('inc', '{module}', '{name}')`, `module_load_include('php', ...)`.
  - Form state includes: `form_load_include($form_state, 'inc', '{module}', '{name}')`.
  - CTools/Plugin include helpers: `ctools_include(...)`, `ctools_plugin_load_includes(...)`.
  - Menu routing declarations: `hook_menu()` items with `'file' => '...'` and optional `'file path' => '...'`.
  - Info file autoloading: `files[] = ...` in `{module}.info`.
- **Graph Construction**: Map direct and transitive inclusion chains (e.g., `module.module` $\rightarrow$ `includes/admin.inc` $\rightarrow$ `includes/helper.inc`).
- **Unverified Inclusions**: If an include target uses dynamic/computed string expressions that cannot be resolved statically, flag the link as `[UNVERIFIED RESULT]` with the source location.

### 3. Callable & Functional Dissection (Content Analysis)
Analyze the actual code contents inside each `.inc` and `.module` file. Dissect every item into discrete functional units:
- **Identified Constructs**:
  - Procedural functions, OOP classes, interfaces, traits, and constants (`define()`, `const`).
  - Menu / Router callbacks (`page callback`, `access callback`, `delivery callback`).
  - Form builders, validation handlers (`_validate`), and submission handlers (`_submit`).
  - AJAX callbacks (`'#ajax' => ['callback' => '...']`).
  - Batch operation callbacks and finished handlers (`'operations' => [...]`, `'finished' => '...'`).
  - Queue worker worker callbacks (`hook_cron_queue_info()`).
  - Cron workers and scheduled tasks.
  - Drush commands (`hook_drush_command()`, `drush_{command}()`).
  - Entity/Field CRUD hooks and callbacks.
  - Theme preprocess, process, and theme engine functions (`template_preprocess_...`, `theme_...`).
  - Database access routines (`db_query`, `db_select`, `db_insert`, `db_update`, `db_delete`).
  - Configuration/Variable operations (`variable_get`, `variable_set`, `variable_del`).
  - External HTTP/API clients (`drupal_http_request`, cURL, Guzzle wrappers).
  - Business logic, validation rules, and permission checks.
  - Procedural helper / utility algorithms.

### 4. Caller & Reference Analysis
For every function and class identified in an `.inc` file:
- Trace references from the owning `.module` file.
- Trace references from other `.inc` files in the same module.
- Trace references from other custom modules across the codebase.
- Trace references from contributed/core modules where applicable.
- Determine if the function is a callback, a public API consumed by other modules, or an internal private helper.

### 5. Standardized 18-Class Functional Taxonomy
Classify every piece of `.inc` functionality into exactly one of the standardized functional categories:
1. `CONTROLLER_PAGE`: Page routing, rendering callbacks, REST/JSON output endpoints.
2. `FORM_HANDLER`: Form definition, validation, submission, and AJAX handling.
3. `SERVICE_BUSINESS_LOGIC`: Reusable business logic, calculations, domain workflows.
4. `PLUGIN_CANDIDATE`: Block, field formatter, field widget, views handler, or CTools plugin behavior.
5. `EVENT_SUBSCRIBER`: Lifecycle hooks, state change reactions, event-driven triggers.
6. `ACCESS_CHECKER`: Custom permission checks, route access callbacks, entity access logic.
7. `ENTITY_FIELD_LOGIC`: Entity operations, bundle definitions, custom field storage/formatting.
8. `QUEUE_WORKER`: Asynchronous job processors, queue processing logic.
9. `BATCH_PROCESSOR`: Step-by-step batch operations and completion callbacks.
10. `CRON_HANDLER`: Scheduled recurring tasks, periodic maintenance jobs.
11. `DRUSH_COMMAND`: CLI commands, Drush generators, maintenance scripts.
12. `CONFIGURATION_HANDLER`: Settings forms, configuration read/write schemas.
13. `THEME_RENDERER`: Twig/theme preprocessors, render array builders, template logic.
14. `UTILITY_HELPER`: Generic string, array, date, or math manipulation helpers.
15. `DATABASE_DATA_ACCESS`: Direct SQL queries, custom schema definitions, complex joins.
16. `INTEGRATION_CLIENT`: External web services, REST/SOAP/GraphQL clients, webhook receivers.
17. `TEST_SUPPORT`: SimpleTest cases, mock fixtures, test helpers.
18. `LEGACY_OBSOLETE`: Dead code, deprecated D6-era wrappers, obsolete workarounds.

### 6. Legacy D7 API Pattern Detection
Detect legacy patterns requiring architectural modernization:
- **Global State**: `$GLOBALS['user']`, `global $user, $conf;`, `$_GET`, `$_POST`, `$_SESSION`.
- **Variables**: `variable_get()`, `variable_set()`, `variable_del()`.
- **Database**: Direct SQL `db_query()`, deprecated procedural helpers.
- **Messages & Output**: `drupal_set_message()`, `drupal_goto()`, `drupal_add_js()`, `drupal_add_css()`.
- **File System**: `file_load()`, `file_save()`, `file_unmanaged_copy()`, `drupal_realpath()`.

### 7. Drush Command Recognition & Cataloging
Explicitly inspect all files (`*.drush.inc`, `includes/*.inc`, etc.) for CLI commands:
- Extract command name, description, arguments, options, aliases, and examples.
- Map business logic invoked by the command.
- Classify survival requirement: `REQUIRED`, `REPLACED` (core Drush provides equivalent), `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.

---

## Output Reporting Standard
All discovery outputs must:
1. Provide verifiable file paths and line number ranges (`[OBSERVED FACT]`).
2. Maintain explicit file-to-functionality accounting tables in discovery artifacts.
3. Flag any dynamic or unresolvable include / callback as `[UNVERIFIED RESULT]`.
