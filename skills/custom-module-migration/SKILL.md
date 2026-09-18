---
name: custom-module-migration
description: End-to-end modernization methodology for migrating Drupal 7 custom modules, procedural hooks, database schemas, configuration variables, entities, forms, AJAX interactions, frontend assets, and Views/custom plugins into PSR-4 Drupal 10/11 modules.
version: 1.8.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files. It enforces exhaustive discovery and re-engineering of legacy procedural hook implementations (core, contrib, custom, alter, entity, form, theme, install/update), `hook_menu()` decomposition, configuration and state variables (`variable_get/set/del`), custom entities, field definitions, revisions, translations, forms (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`), Form API structures, AJAX commands, custom event dispatching, legacy custom PHP source files, OOP classes, constructors, interfaces, traits, `.inc` files, inclusion trees, Drush commands, frontend JavaScript/CSS/libraries, Views definitions (`views.view.*.yml`), custom Views plugins, and `hook_views_data` into modern PSR-4 architectures.

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

## The 12-Step Modernization Playbook

1. **Step 1: Recursive Inventory, Source Asset, Hook, Entity, Form, Frontend & Views Discovery**
   - Recursively catalog all source files (`.info`, `.module`, `.inc`, `.install`, `*.php`, `*.profile`, `.drush.inc`, `.js`, `.css`, `*.views_default.inc`, `*.views.inc`) across root and subdirectories (`includes/`, `lib/`, `classes/`, `src/`, `admin/`, `commands/`, `views/`, etc.).
   - Dissect every custom PHP file, class, interface, trait, constructor, procedural hook implementation, custom entity type, field definition, revision mechanism, translation setting, form builder, form alter, AJAX callback, configuration/state access, frontend behavior, and Views definition / custom handler plugin.
   - Catalog discovered artifacts into the respective taxonomies (9-type hook taxonomy, 20-type configuration taxonomy, 26-target entity taxonomy, 19-target form/AJAX taxonomy, 21-target frontend taxonomy, 30-target Views taxonomy).

2. **Step 2: Dependency, Caller Graph, Hook Invocation, Entity Reference & Config Lifecycle Mapping**
   - Identify core module, contrib module, custom module, entity reference, form dependency, frontend asset dependency, Views dependency, and configuration/state dependencies using `skills/dependency-analysis`.
   - Map inter-file and inter-module calls to custom classes (`new ClassName()`, static calls), procedural functions, custom hook subscribers/callers, entity reference topologies, form callers, AJAX endpoints, Views handlers, and configuration reads/writes/deletes.
   - Analyze hook execution order, module weights (`{system}.weight`), alter sequencing (`hook_module_implements_alter`), entity reference hierarchy, and variable lifecycle (`CREATE -> READ -> MODIFY -> DELETE`).

3. **Step 3: Business Behavior, Hook Dissection, Form & Entity/Configuration Decomposition**
   - Extract discrete functional units from custom PHP classes, `.inc` files, procedural hooks, custom entities, field definitions, form builders, configuration forms, and default Views.
   - Decompose `hook_menu()` implementations into discrete routes, controllers, form classes (`src/Form/`), access checkers, menu links, local tasks, local actions, and contextual links.
   - Decompose `system_settings_form()` into `ConfigFormBase` classes, typed schemas (`config/schema/*.schema.yml`), default configuration (`config/install/*.yml`), and menu routes.
   - Decompose `confirm_form()` into `ConfirmFormBase` classes.
   - Decompose custom D7 entities into Content Entity classes (`src/Entity/`), interfaces, access control handlers, view builders, and field definitions.
   - Decompose default Views and `hook_views_default_views()` into CMI configuration files (`config/install/views.view.*.yml`).

4. **Step 4: Legacy API Audit, Constructor Inspection, Form API, Entity & State Analysis**
   - Audit constructors (`__construct()` and legacy `ClassName()`): extract parameters, global references (`$user`, `$conf`), and procedural calls (`variable_get()`, `db_query()`, `entity_load()`, `drupal_get_form()`, `views_get_view()`).
   - Audit legacy Drupal 7 procedural APIs (`variable_get()`, `variable_set()`, `variable_del()`, `entity_load()`, `entity_save()`, `field_info_field()`, `EntityFieldQuery`, `drupal_get_form()`, `ajax_render()`, `ajax_command_*()`, `views_get_view()`, `views_embed_view()`).
   - Distinguish Content Entities vs Config Entities vs Configuration (CMI) vs State (State API) vs Forms vs Views vs Cache.
   - Inspect custom database schemas in `hook_schema()`: column definitions, primary keys, indexes, foreign keys, revision tables, data tables, and entity reference columns (`uid`, `nid`, `tid`, `fid`, `entity_id`).
   - Audit all procedural database queries (`db_query()`, `db_select()`, `db_insert()`, `db_update()`, `db_delete()`, `db_merge()`, `db_transaction()`, `EntityFieldQuery`, `hook_views_query_alter()`) for dynamic SQL and parameter safety.

5. **Step 5: Modern Architecture Design (Non-1:1 Mapping, Data Models, Entities, Forms, AJAX, CMI, Views & PSR-4)**
   - Re-engineer functionality into modern Symfony/Drupal OOP architectures rather than 1:1 file renaming:
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
     - D7 lifecycle / request hook (`hook_init`, `hook_exit`, `hook_boot`, `hook_node_*`) $\rightarrow$ Event Subscriber (`src/EventSubscriber/`) or Entity Hook / Post-save handler
     - D7 block hooks (`hook_block_info`, `hook_block_view`) $\rightarrow$ Block Plugin (`src/Plugin/Block/`)
     - D7 Drush command $\rightarrow$ modern Drush Command class in `src/Drush/Commands/`
     - D7 access callback / `hook_permission` / `hook_node_access` $\rightarrow$ `permissions.yml` + Custom Access Check service in `src/Access/`
     - D7 batch/queue callback $\rightarrow$ D10 Batch API / QueueWorker plugin in `src/Plugin/QueueWorker/`
     - D7 value / domain object $\rightarrow$ PSR-4 typed class in `src/Model/` or `src/ValueObject/`
     - D7 custom database table $\rightarrow$ Content Entity (`src/Entity/`), Config Entity, Config API (`config.factory`), State API (`\Drupal::state()`), KeyValue store, or dedicated Repository Service (`src/Repository/`).
   - Support One-to-Many and Many-to-One transformations.

6. **Step 6: Target-Ready Design Review, Constructor DI & Entity/Form/Views Schema Verification**
   - Enforce constructor Dependency Injection, typehints, strict return types, and interface contracts; eliminate static `\Drupal::*` calls.
   - Refactor constructors to modern `public function __construct(...)` injecting only genuinely utilized dependencies (`entity_type.manager`, `config.factory`, `state`, `database`, `current_user`).
   - Modernize database, entity, and Views plugin access into repository classes or storage handlers injecting `\Drupal\Core\Entity\EntityTypeManagerInterface`.
   - Validate CMI schema definitions in `config/schema/*.schema.yml`, field storage YAMLs, and Views YAMLs against typed configuration standards.

7. **Step 7: Migration Plan Formulation & Complete Accounting Matrix**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
   - Maintain an explicit File/Class/Hook/Database/Configuration/Entity/Form/Frontend/Views Accounting Table showing the exact target class, service, entity, field config, form class, AJAX handler, library definition, JavaScript behavior, View configuration, custom Views plugin, config object, state key, event subscriber, plugin, or routing artifact for every legacy item.

8. **Step 8: Controlled Implementation & Modernization**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `.links.menu.yml`, `.links.task.yml`, `drush.services.yml`, `.libraries.yml`, `.views.inc`).
   - Generate default configuration (`config/install/<module>.settings.yml`), schema (`config/schema/<module>.schema.yml`), field definitions (`config/install/field.storage.*`, `field.field.*`), and Views definitions (`config/install/views.view.*.yml`).
   - Implement entity classes (`src/Entity/`), access handlers, storage handlers, services, controllers, form classes (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`), AJAX handlers, JavaScript `once()` behaviors (`js/`), SMACSS stylesheets (`css/`), `.libraries.yml` definitions, custom Views plugins (`src/Plugin/views/`), event subscribers, plugins, repository classes, and Drush classes strictly inside `target.path/web/modules/custom/<MODULE>/`.
   - Delegate scoped complex service authoring, DI modernization, and database query modernization to `api-modernization` where required.
   - Log all file creations and modifications in `logs/file-change-log/`.

9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting modernized entities (CRUD, revisions, translations), field storage, services, controllers, form submissions (`submitForm()`), form validation (`validateForm()`), AJAX response commands, JavaScript/CSS library registrations, Views configuration schemas, custom Views plugin executions, query alterations, configuration schemas, state persistence, event subscribers, repositories, and entities using `skills/testing`.

10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
    - Verify that every discovered custom PHP file, class, method, function, procedural hook, custom database table, configuration/state variable, entity type, field, form builder, form alter, AJAX callback, JavaScript behavior, CSS asset, View definition, and custom Views plugin has an explicit modern equivalent or valid reason.

11. **Step 11: Gap Analysis & Outcome Accounting**
    - Verify that every custom PHP file, class, function, procedural hook implementation, custom database table, configuration/state artifact, entity type, field, form, AJAX callback, frontend asset, View definition, and Views plugin ends in an approved outcome state:
      `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`.
    - Reject any `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, or `SILENTLY_OMITTED` items.

12. **Step 12: Sign-Off & Manifest Update**
    - Generate `reports/custom-modules/REPORT-<MODULE>.md`.
    - Propose updating component status to `CODE_COMPLETE` via `agent_result`.
