---
name: custom-module-migration
description: End-to-end modernization methodology for migrating Drupal 7 custom modules, procedural hooks, database schemas, configuration variables, entities, forms, AJAX interactions, frontend assets, Views/custom plugins, theme presentation layers, and dynamic runtime dependencies into PSR-4 Drupal 10/11 modules.
version: 1.10.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files. It enforces exhaustive discovery and re-engineering of legacy procedural hook implementations (core, contrib, custom, alter, entity, form, theme, install/update), `hook_menu()` decomposition, configuration and state variables (`variable_get/set/del`), custom entities, field definitions, revisions, translations, forms (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`), Form API structures, AJAX commands, custom event dispatching, legacy custom PHP source files, OOP classes, constructors, interfaces, traits, `.inc` files, inclusion trees, Drush commands, frontend JavaScript/CSS/libraries, Views definitions (`views.view.*.yml`), custom Views plugins, `hook_views_data`, theme presentation layers, and dynamic runtime dependencies into modern PSR-4 architectures.

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
## Module Migration Lifecycle: 12-Step Execution Methodology

For every custom module assigned in an execution wave, execute the following 12-step playbook:

1. **Step 1: Context Ingestion & Read-Only Source Introspection**
   - Read module declaration and static inventory in `state/migration-manifest.yml`.
   - Inspect all module files in `source.path` (`.module`, `.info`, `.install`, `.inc`, `.php`, `.drush.inc`, `templates/`, `js/`, `css/`).
   - Parse all procedural functions, custom OOP classes, constructors, methods, hooks, database tables, variables, entities, fields, forms, AJAX callbacks, frontend scripts/styles, Views definitions, displays, custom Views plugins, and dynamic dependencies.

2. **Step 2: Dependency & Wave Verification**
   - Verify all upstream dependencies assigned in earlier waves are in state `COMPLETED` or `CODE_COMPLETE` in `state/migration-state.yml`.
   - Re-verify cross-module services, shared database tables, and entity reference integrity.

3. **Step 3: Procedural Hook & Custom Class Deconstruction**
   - Deconstruct procedural hooks into modern architectural destinations:
     - `hook_menu()` $\rightarrow$ `<module>.routing.yml`, `src/Controller/`, `src/Form/`, `<module>.links.menu.yml`, `<module>.permissions.yml`, `src/Access/`.
     - Procedural forms $\rightarrow$ `src/Form/<FormName>.php` (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`).
     - Entity hooks $\rightarrow$ Modern entity hooks or Event Subscribers (`src/EventSubscriber/`).
     - Custom hooks $\rightarrow$ Symfony Event classes (`src/Event/`) and Event Subscribers (`src/EventSubscriber/`).
     - Procedural blocks $\rightarrow$ Modern Block Plugins (`src/Plugin/Block/`).
     - Procedural Views hooks $\rightarrow$ `hook_views_data()` in `<module>.views.inc` and custom Views plugins under `src/Plugin/views/`.
     - Drush commands $\rightarrow$ Drush 12/13 command classes under `src/Drush/Commands/`.
   - Deconstruct custom PHP classes, interfaces, traits, and constructors:
     - Move legacy classes to PSR-4 `src/` hierarchy.
     - Extract legacy constructor dependencies into DI constructor parameters.
     - Eliminate global variable references (`$user`, `$language`, `variable_get()`, `db_query()`).

4. **Step 4: Configuration, State & Entity Architecture Alignment**
   - Map `variable_get()` administrative settings to CMI schemas (`config/schema/<module>.schema.yml`) and install files (`config/install/<module>.settings.yml`).
   - Map runtime flags/timestamps to State API (`\Drupal::state()`).
   - Define custom Content Entities (`src/Entity/<Entity>.php`) and Config Entities (`src/Entity/<ConfigEntity>.php`) with complete field definitions and annotations/attributes.

5. **Step 5: Frontend Assets, Forms & Views Architecture Alignment**
   - Map Form API structures, validation/submit handlers, `#states`, and `#ajax` callbacks to `FormStateInterface` and `AjaxResponse` commands.
   - Package JavaScript behaviors with `@drupal/once` and CSS stylesheets into `<module>.libraries.yml` per SMACSS standards.
   - Map default Views to `config/install/views.view.<view_id>.yml` and custom Views plugins to `src/Plugin/views/`.

6. **Step 6: Dynamic, Runtime & Data-Driven Dependency Alignment (Step 21)**
   - Account for all dynamic callables, variable functions, dynamic class instantiations, dynamic hooks, dynamic entity/field types, and serialized payloads.
   - Re-engineer dynamic function dispatches to Plugin Managers (`DefaultPluginManager`) or tagged service collections.
   - Specify deterministic, safe runtime probes for runtime-dependent artifacts and mark unverified probes with explicit boundary markers.

7. **Step 7: Migration Plan Formulation & Complete Accounting Matrix**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
   - Maintain an explicit File/Class/Hook/Database/Configuration/Entity/Form/Frontend/Views/Dynamic Accounting Table showing the exact target class, service, entity, field config, form class, AJAX handler, library definition, JavaScript behavior, View configuration, custom Views plugin, dynamic plugin manager, config object, state key, event subscriber, plugin, or routing artifact for every legacy item.

8. **Step 8: Controlled Implementation & Modernization**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`, `.links.menu.yml`, `.links.task.yml`, `drush.services.yml`, `.libraries.yml`, `.views.inc`).
   - Generate default configuration (`config/install/<module>.settings.yml`), schema (`config/schema/<module>.schema.yml`), field definitions (`config/install/field.storage.*`, `field.field.*`), and Views definitions (`config/install/views.view.*.yml`).
   - Implement entity classes (`src/Entity/`), access handlers, storage handlers, services, controllers, form classes (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`), AJAX handlers, JavaScript `once()` behaviors (`js/`), SMACSS stylesheets (`css/`), `.libraries.yml` definitions, custom Views plugins (`src/Plugin/views/`), dynamic plugin managers (`src/Plugin/`), event subscribers, plugins, repository classes, and Drush classes strictly inside `target.path/web/modules/custom/<MODULE>/`.
   - Delegate scoped complex service authoring, DI modernization, and database query modernization to `api-modernization` where required.
   - Log all file creations and modifications in `logs/file-change-log/`.

9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting modernized entities (CRUD, revisions, translations), field storage, services, controllers, form submissions (`submitForm()`), form validation (`validateForm()`), AJAX response commands, JavaScript/CSS library registrations, Views configuration schemas, custom Views plugin executions, query alterations, configuration schemas, state persistence, event subscribers, dynamic plugin managers, runtime probes, repositories, and entities using `skills/testing`.

10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
    - Verify that every discovered custom PHP file, class, method, function, procedural hook, custom database table, configuration/state variable, entity type, field, form builder, form alter, AJAX callback, JavaScript behavior, CSS asset, View definition, custom Views plugin, and dynamic dependency has an explicit modern equivalent or valid reason.

11. **Step 11: Gap Analysis & Outcome Accounting**
    - Verify that every custom PHP file, class, function, procedural hook implementation, custom database table, configuration/state artifact, entity type, field, form, AJAX callback, frontend asset, View definition, Views plugin, and dynamic dependency ends in an approved outcome state:
      `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`.
    - Reject any `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, or `SILENTLY_OMITTED` items.

12. **Step 12: Sign-Off & Manifest Update**
    - Generate `reports/custom-modules/REPORT-<MODULE>.md`.
    - Propose updating component status to `CODE_COMPLETE` via `agent_result`.
