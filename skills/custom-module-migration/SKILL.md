---
name: custom-module-migration
description: Comprehensive 12-step engineering playbook for migrating custom Drupal 7 modules into modern Drupal 10/11 modules, with recursive custom PHP file/class re-engineering, procedural hook decomposition, configuration and state re-engineering, constructor DI modernization, and Drush modernization.
version: 1.4.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files. It enforces exhaustive discovery and re-engineering of legacy procedural hook implementations (core, contrib, custom, alter, entity, form, theme, install/update), `hook_menu()` decomposition, configuration and state variables (`variable_get/set/del`), admin settings forms (`system_settings_form`), custom event dispatching, legacy custom PHP source files, OOP classes, constructors, interfaces, traits, `.inc` files, inclusion trees, and Drush commands into modern PSR-4 architectures.

---

## Technical References & Associated Skills
- Associated Skills:
  - [`skills/d7-analysis`](../d7-analysis/SKILL.md)
  - [`skills/d7-to-d10-mapping`](../d7-to-d10-mapping/SKILL.md)
  - [`skills/configuration-migration`](../configuration-migration/SKILL.md)
  - [`skills/d10-architecture`](../d10-architecture/SKILL.md)
  - [`skills/dependency-analysis`](../dependency-analysis/SKILL.md)
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

1. **Step 1: Recursive Inventory, Source Asset, Hook & Configuration Discovery**
   - Recursively catalog all source files (`.info`, `.module`, `.inc`, `.install`, `*.php`, `*.profile`, `.drush.inc`, `.js`, `.css`) across root and subdirectories (`includes/`, `lib/`, `classes/`, `src/`, `admin/`, `commands/`, etc.).
   - Dissect every custom PHP file, class, interface, trait, constructor, procedural hook implementation, and configuration/state access.
   - Catalog every D7 hook implementation (`<module>_<hook>`), custom hook invocation (`module_invoke_all`, `module_invoke`), alter hook into the 9-type taxonomy, and configuration/state artifact into the 20-type configuration taxonomy.

2. **Step 2: Dependency, Caller Graph, Hook Invocation & Config Lifecycle Mapping**
   - Identify core module, contrib module, custom module, and configuration/state dependencies using `skills/dependency-analysis`.
   - Map inter-file and inter-module calls to custom classes (`new ClassName()`, static calls), procedural functions, custom hook subscribers/callers, and configuration reads/writes/deletes.
   - Analyze hook execution order, module weights (`{system}.weight`), alter sequencing (`hook_module_implements_alter`), and variable lifecycle (`CREATE -> READ -> MODIFY -> DELETE`).

3. **Step 3: Business Behavior, Hook Dissection & Configuration Decomposition**
   - Extract discrete functional units from custom PHP classes, `.inc` files, procedural hooks, and configuration forms.
   - Decompose `hook_menu()` implementations into discrete routes, controllers, form classes, access checkers, menu links, local tasks, local actions, and contextual links.
   - Decompose `system_settings_form()` into `ConfigFormBase` classes, typed schemas (`config/schema/*.schema.yml`), default configuration (`config/install/*.yml`), and menu routes.
   - Classify every unit, hook, and variable into the architectural targets and migration strategies.

4. **Step 4: Legacy API Audit, Constructor Inspection, State & Database Analysis**
   - Audit constructors (`__construct()` and legacy `ClassName()`): extract parameters, global references (`$user`, `$conf`), and procedural calls (`variable_get()`, `db_query()`).
   - Audit legacy Drupal 7 procedural APIs (`variable_get()`, `variable_set()`, `variable_del()`, `system_settings_form()`).
   - Distinguish Configuration (CMI) vs State (State API) vs Content vs Environment/Secrets vs Cache.
   - Inspect custom database schemas in `hook_schema()`: column definitions, primary keys, indexes, foreign keys, and entity reference columns (`uid`, `nid`, `tid`, `fid`, `entity_id`).
   - Audit all procedural database queries (`db_query()`, `db_select()`, `db_insert()`, `db_update()`, `db_delete()`, `db_merge()`, `db_transaction()`) for dynamic SQL and parameter safety.

5. **Step 5: Modern Architecture Design (Non-1:1 Mapping, Data Models, CMI & PSR-4)**
   - Re-engineer functionality into modern Symfony/Drupal OOP architectures rather than 1:1 file renaming:
     - D7 business logic class / function / procedural hook $\rightarrow$ D10 Service class in `src/Service/` registered in `.services.yml`
     - D7 page callback from `hook_menu()` $\rightarrow$ D10 Controller in `src/Controller/`
     - D7 form callback / `hook_form_*` builder $\rightarrow$ D10 Form API class in `src/Form/`
     - D7 admin settings form / `system_settings_form()` $\rightarrow$ D10 `ConfigFormBase` in `src/Form/` + `config/install/*.yml` + `config/schema/*.schema.yml`
     - D7 runtime state / flag / timestamp $\rightarrow$ D10 State API (`StateInterface` / `\Drupal::state()`)
     - D7 secrets / credentials / environment values $\rightarrow$ `settings.php` overrides / `getenv()` / Key module (Rule 10: zero secrets in CMI)
     - D7 custom hook invocation (`module_invoke_all`) $\rightarrow$ Symfony EventDispatcher event dispatching with custom `Event` class and `EventSubscriberInterface`
     - D7 lifecycle / request hook (`hook_init`, `hook_exit`, `hook_boot`, `hook_node_*`) $\rightarrow$ Event Subscriber (`src/EventSubscriber/`) or Entity Hook / Post-save handler
     - D7 block hooks (`hook_block_info`, `hook_block_view`) $\rightarrow$ Block Plugin (`src/Plugin/Block/`)
     - D7 Drush command $\rightarrow$ modern Drush Command class in `src/Drush/Commands/`
     - D7 access callback / `hook_permission` / `hook_node_access` $\rightarrow$ `permissions.yml` + Custom Access Check service in `src/Access/`
     - D7 batch/queue callback $\rightarrow$ D10 Batch API / QueueWorker plugin in `src/Plugin/QueueWorker/`
     - D7 value / domain object $\rightarrow$ PSR-4 typed class in `src/Model/` or `src/ValueObject/`
     - D7 custom database table $\rightarrow$ Content Entity (`src/Entity/`), Config Entity, Config API (`config.factory`), State API (`\Drupal::state()`), KeyValue store, or dedicated Repository Service (`src/Repository/`).
   - Support One-to-Many and Many-to-One transformations.

6. **Step 6: Target-Ready Design Review, Constructor DI & CMI Schema Verification**
   - Enforce constructor Dependency Injection, typehints, strict return types, and interface contracts; eliminate static `\Drupal::*` calls.
   - Refactor constructors to modern `public function __construct(...)` injecting only genuinely utilized dependencies (`config.factory`, `state`, `database`, `current_user`).
   - Modernize database access into repository classes injecting `\Drupal\Core\Database\Connection` and `\Drupal\Core\Entity\EntityTypeManagerInterface`.
   - Validate CMI schema definitions in `config/schema/*.schema.yml` against typed configuration standards.

7. **Step 7: Migration Plan Formulation & File/Class/Hook/Database/Config Matrix**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
   - Maintain an explicit File/Class/Hook/Database/Configuration Accounting Table showing the exact target class, service, config object, state key, event subscriber, plugin, or routing artifact for every legacy item.

8. **Step 8: Controlled Implementation & Modernization**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `.links.menu.yml`, `.links.task.yml`, `drush.services.yml`).
   - Generate default configuration (`config/install/<module>.settings.yml`) and schema (`config/schema/<module>.schema.yml`).
   - Implement services, controllers, forms (`ConfigFormBase`), event subscribers, plugins, repository classes, and Drush classes strictly inside `target.path/web/modules/custom/<MODULE>/`.
   - Delegate scoped complex service authoring, DI modernization, and database query modernization to `api-modernization` where required.
   - Log all file creations and modifications in `logs/file-change-log/`.

9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting modernized services, controllers, form submissions, configuration schemas, state persistence, event subscribers, repositories, and entities using `skills/testing`.

10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
    - Verify that every discovered custom PHP file, class, method, function, procedural hook, custom database table, and configuration/state variable has an explicit modern equivalent or valid reason.

11. **Step 11: Gap Analysis & Outcome Accounting**
    - Verify that every custom PHP file, class, function, procedural hook implementation, custom database table, and configuration/state artifact ends in an approved outcome state:
      `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`.
    - Reject any `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, or `SILENTLY_OMITTED` items.

12. **Step 12: Sign-Off & Manifest Update**
    - Generate `reports/custom-modules/REPORT-<MODULE>.md`.
    - Propose updating component status to `CODE_COMPLETE` via `agent_result`.
