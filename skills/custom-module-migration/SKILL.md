---
name: custom-module-migration
description: Comprehensive 12-step engineering playbook for migrating custom Drupal 7 modules into modern Drupal 10/11 modules, with recursive custom PHP file/class re-engineering, constructor DI modernization, and Drush modernization.
version: 1.2.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files. It enforces exhaustive discovery and re-engineering of legacy custom PHP source files, OOP classes, constructors, interfaces, traits, `.inc` files, inclusion trees, and Drush commands into modern PSR-4 architectures.

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
   - Recursively catalog all source files (`.info`, `.module`, `.inc`, `.install`, `*.php`, `*.profile`, `.drush.inc`, `.js`, `.css`) across root and subdirectories (`includes/`, `lib/`, `classes/`, `src/`, `admin/`, `commands/`, etc.).
   - Dissect every custom PHP file, class, interface, trait, and constructor into discrete units and record autoload/include relationships.

2. **Step 2: Dependency & Caller Graph Mapping**
   - Identify core module, contrib module, and custom module dependencies using `skills/dependency-analysis`.
   - Map inter-file and inter-module calls to custom classes (`new ClassName()`, static calls) and procedural functions.

3. **Step 3: Business Behavior & Functional Dissection**
   - Extract discrete functional units from custom PHP classes and `.inc` files.
   - Classify every unit into the 22-class taxonomy (`SERVICE_BUSINESS_LOGIC`, `CONTROLLER`, `FORM`, `PLUGIN`, `EVENT_SUBSCRIBER`, `ACCESS_CHECKER`, `ENTITY_LOGIC`, `FIELD_LOGIC`, `QUEUE_WORKER`, `BATCH_PROCESSOR`, `CRON_HANDLER`, `DRUSH_COMMAND`, `CONFIGURATION_HANDLER`, `INTEGRATION_CLIENT`, `DATA_ACCESS`, `VALUE_OBJECT`, `DOMAIN_OBJECT`, `UTILITY_HELPER`, `TEST_SUPPORT`, `LIBRARY_EXTERNAL_DEPENDENCY`, `LEGACY_OBSOLETE`, `HUMAN_DECISION_REQUIRED` / `UNVERIFIED`).

4. **Step 4: Legacy API Audit & Constructor Inspection**
   - Audit constructors (`__construct()` and legacy `ClassName()`): extract parameters, global references (`$user`, `$conf`), and procedural calls (`variable_get()`, `db_query()`).
   - Audit legacy Drupal 7 procedural APIs against `references/drupal-7/hooks.md` and `references/drupal-7/apis.md`.

5. **Step 5: Modern Architecture Design (Non-1:1 Mapping & PSR-4)**
   - Re-engineer functionality into modern Symfony/Drupal OOP architectures rather than 1:1 file renaming:
     - D7 business logic class / function $\rightarrow$ D10 Service class in `src/Service/` registered in `.services.yml`
     - D7 page callback $\rightarrow$ D10 Controller in `src/Controller/`
     - D7 form callback/class $\rightarrow$ D10 Form API class in `src/Form/`
     - D7 Drush command $\rightarrow$ modern Drush Command class in `src/Drush/Commands/`
     - D7 access callback $\rightarrow$ D10 Custom Access Check service in `src/Access/`
     - D7 batch/queue callback $\rightarrow$ D10 Batch API / QueueWorker plugin in `src/Plugin/QueueWorker/`
     - D7 value / domain object $\rightarrow$ PSR-4 typed class in `src/Model/` or `src/ValueObject/`
   - Consolidate or decompose files as architecturally appropriate (one legacy PHP file may produce multiple D10 classes; multiple files may merge into one cohesive service).

6. **Step 6: Target-Ready Design Review & Constructor DI**
   - Enforce constructor Dependency Injection, typehints, strict return types, and interface contracts; eliminate static `\Drupal::*` calls.
   - Refactor constructors to modern `public function __construct(...)` injecting only genuinely utilized dependencies.

7. **Step 7: Migration Plan Formulation & File-to-Class/Function Matrix**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
   - Maintain an explicit File-to-Class/Function Accounting Table showing the exact target class for every legacy PHP file, class, method, and constructor.

8. **Step 8: Controlled Implementation & Modernization**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `drush.services.yml`).
   - Implement services, controllers, forms, plugins, and Drush classes strictly inside `target.path/web/modules/custom/<MODULE>/`.
   - Delegate scoped complex service authoring and DI modernization to `api-modernization` where required.
   - Log all file creations and modifications in `logs/file-change-log/`.

9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting modernized services, controllers, and classes using `skills/testing`.

10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
    - Verify that every discovered custom PHP file, class, method, and function has an explicit modern equivalent or valid reason.

11. **Step 11: Gap Analysis & Outcome Accounting**
    - Verify that every custom PHP file, class, and function ends in an approved outcome state:
      `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`.
    - Reject any `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, or `SILENTLY_OMITTED` items.

12. **Step 12: Sign-Off & Manifest Update**
    - Generate `reports/custom-modules/REPORT-<MODULE>.md`.
    - Propose updating component status to `CODE_COMPLETE` via `agent_result`.
