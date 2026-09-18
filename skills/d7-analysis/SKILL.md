---
name: d7-analysis
description: Procedural inspection heuristics for Drupal 7 modules, hooks, database schemas, and variables without mutating source files. Use when analyzing legacy Drupal 7 codebases.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Drupal 7 Codebase Analysis Skill

## Overview
This skill provides structured heuristics for non-destructively inspecting Drupal 7 code, modules, themes, and database schemas. It extracts business behavior, hook implementations, and couplings to prepare for modernization.

---

## Analysis Workflow

### 1. Module Identification & Packaging
- Inspect `.info` file to determine:
  - Is it custom or contributed? Check for `project = "..."` or `version = "7.x-..."` packaging metadata.
  - Declared dependencies: `dependencies[]`.
  - Registered files: `files[]`.
  - Config paths: `configure = ...`.

### 2. Hook Discovery & Cataloging
- Search `.module` and `.inc` files for function patterns:
  - `function {module}_{hook_name}(...)`
- Categorize discovered hooks:
  - **Routing/UI**: `hook_menu()`, `hook_menu_alter()`, `hook_theme()`, `hook_block_info()`, `hook_block_view()`.
  - **Forms**: `hook_form_alter()`, `hook_form_FORM_ID_alter()`.
  - **Entity Lifecycle**: `hook_node_load()`, `hook_node_insert()`, `hook_node_update()`, `hook_user_login()`.
  - **Database & Schema**: `hook_schema()`, `hook_install()`, `hook_update_N()`.
  - **Cron & Queues**: `hook_cron()`, `hook_cron_queue_info()`.

### 3. Business Logic & Global State Extraction
- Search for direct global references:
  - `$GLOBALS['user']` or `global $user;`
  - `$_GET`, `$_POST`, `$_REQUEST`, `$_SESSION`
  - Direct SQL queries: `db_query()`, `db_select()`
  - Legacy variables: `variable_get()`, `variable_set()`

### 4. Output Reporting Standard
Always ground findings in verifiable source line numbers (`[OBSERVED FACT]`).
