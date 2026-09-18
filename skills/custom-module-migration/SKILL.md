---
name: custom-module-migration
description: Comprehensive 12-step engineering playbook for migrating custom Drupal 7 modules into modern Drupal 10/11 modules, with recursive .inc file handling and Drush modernization.
version: 1.1.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files. It enforces exhaustive discovery and re-engineering of legacy `.inc` files, inclusion trees, and Drush commands into modern OOP architectures.

---

## Technical References & Associated Skills
- Associated Skills:
  - [`skills/d7-analysis`](../d7-analysis/SKILL.md)
  - [`skills/d7-to-d10-mapping`](../d7-to-d10-mapping/SKILL.md)
  - [`skills/d10-architecture`](../d10-architecture/SKILL.md)
- Canonical References:
  - [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
  - [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)
  - [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)

---

## Target-Version Resolution
Determine target version from project configuration (`target.core_version`):
- For **Drupal 10.x**: Target PHP >= 8.1; use DocBlock annotations or PHP Attributes where supported.
- For **Drupal 11.x**: Target PHP >= 8.3; prefer PHP 8 Attributes for all supported plugins; ensure strict return types.

---

## The 12-Step Modernization Playbook

1. **Step 1: Recursive Inventory & Source Asset Discovery**
   - Recursively catalog all source files (`.info`, `.module`, `.inc`, `.install`, `.php`, `.drush.inc`, `.js`, `.css`) across root and subdirectories (`includes/`, `admin/`, `commands/`, etc.).
   - Dissect every `.inc` file into discrete callable units and record include/require relationships.

2. **Step 2: Dependency & Caller Graph Mapping**
   - Identify core module, contrib module, and custom module dependencies using `skills/dependency-analysis`.
   - Map inter-file and inter-module calls to `.inc` functions.

3. **Step 3: Business Behavior & Functional Dissection**
   - Extract discrete functional units from `.module` and `.inc` files.
   - Classify every unit into the 18-class taxonomy (Controllers, Forms, Services, Plugins, Access Checkers, Drush Commands, Queue/Batch Workers, etc.).

4. **Step 4: Legacy API Audit**
   - Audit legacy Drupal 7 procedural APIs (`db_query`, `variable_get`, globals, `drupal_set_message`, `drupal_goto`) against `references/drupal-7/hooks.md` and `references/drupal-7/apis.md`.

5. **Step 5: Modern Architecture Design (Non-1:1 Mapping)**
   - Re-engineer functionality into modern Symfony/Drupal OOP architectures rather than 1:1 file renaming:
     - D7 page callback $\rightarrow$ D10 Controller
     - D7 form callback $\rightarrow$ D10 Form API class
     - D7 business logic in `.inc` $\rightarrow$ D10 Service class
     - D7 Drush command in `.inc` $\rightarrow$ modern Drush Command class / service
     - D7 access callback $\rightarrow$ D10 Custom Access Check service
     - D7 batch/queue callback $\rightarrow$ D10 Batch API / QueueWorker plugin
   - Consolidate or decompose files as architecturally appropriate (one `.inc` may produce multiple D10 classes; multiple `.inc` files may merge into one cohesive service).

6. **Step 6: Target-Ready Design Review**
   - Enforce constructor Dependency Injection, typehints, strict return types, and interface contracts; eliminate static `\Drupal::*` calls.

7. **Step 7: Migration Plan Formulation & File-to-Function Matrix**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
   - Maintain an explicit File-to-Function Accounting Table showing the exact target class for every legacy `.inc` function.

8. **Step 8: Controlled Implementation & Modernization**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `drush.services.yml`).
   - Implement services, controllers, forms, plugins, and Drush classes strictly inside `target.path/web/modules/custom/<MODULE>/`.
   - Delegate scoped complex service authoring to `api-modernization` where required.
   - Log all file creations and modifications in `logs/file-change-log/`.

9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting modernized services and controllers using `skills/testing`.

10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
    - Verify that every discovered `.inc` function has an explicit modern equivalent or valid reason.

11. **Step 11: Gap Analysis & Outcome Accounting**
    - Verify that every `.inc` file and function ends in an approved outcome state:
      `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`.
    - Reject any `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, or `SILENTLY_OMITTED` items.

12. **Step 12: Sign-Off & Manifest Update**
    - Generate `reports/custom-modules/REPORT-<MODULE>.md`.
    - Propose updating component status to `CODE_COMPLETE` via `agent_result`.
