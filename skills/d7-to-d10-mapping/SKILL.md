---
name: d7-to-d10-mapping
description: Behavioral and architectural mapping rules for converting procedural Drupal 7 APIs, hooks, and legacy custom PHP classes into modern Drupal 10/11 object-oriented patterns.
version: 1.2.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep
---

# Drupal 7 to Drupal 10/11 Architectural Mapping Skill

## Overview
This skill provides the architectural mapping rules required to translate Drupal 7 procedural constructs, hooks (core, contrib, custom, alter, entity, form, theme, install/update), legacy custom PHP classes, constructors, interfaces, traits, and `.inc` files into modern Symfony/Drupal 10 and Drupal 11 object-oriented paradigms, prioritizing Dependency Injection, PSR-4 autoloading, service containers, event subscribers, and testability.

---

## Technical References
For detailed syntax examples and conversion catalogs, consult:
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)

---

## Core Mapping Rules

### 1. Legacy Custom PHP Class & OOP Modernization
- **PSR-4 Namespacing**: Custom classes declared in root, `includes/`, `lib/`, or `classes/` must be moved into PSR-4 compliant `src/` subdirectories:
  - Domain / Business Logic $\rightarrow$ `Drupal\<module>\Service\<ClassName>` (`src/Service/`)
  - Page / Endpoint Handlers $\rightarrow$ `Drupal\<module>\Controller\<ClassName>` (`src/Controller/`)
  - Form Handlers $\rightarrow$ `Drupal\<module>\Form\<ClassName>` (`src/Form/`)
  - Drush CLI Commands $\rightarrow$ `Drupal\<module>\Drush\Commands\<ClassName>` (`src/Drush/Commands/`)
  - Event Subscribers $\rightarrow$ `Drupal\<module>\EventSubscriber\<ClassName>` (`src/EventSubscriber/`)
  - Access Handlers $\rightarrow$ `Drupal\<module>\Access\<ClassName>` (`src/Access/`)
  - Value / Domain Objects $\rightarrow$ `Drupal\<module>\Model\<ClassName>` (`src/Model/` or `src/ValueObject/`)
- **Autoloading Modernization**: Eliminate manual `require`, `include`, `module_load_include()`, or `.info` `files[]` declarations. Target classes rely exclusively on Composer / Drupal PSR-4 autoloading.

### 2. Constructor Modernization & Dependency Injection
- **Constructor Refactoring**:
  - Legacy PHP4/D7 constructors (`function ClassName(...)`) must be refactored to standard `public function __construct(...)` with explicit parameter typehints and return types.
  - Eliminate global variable fetches inside constructors (`global $user, $conf, $language;` $\rightarrow$ injected `AccountProxyInterface`, `ConfigFactoryInterface`, `LanguageManagerInterface`).
  - Eliminate direct procedural calls inside constructors (`variable_get()` $\rightarrow$ injected `config.factory`, `db_query()` $\rightarrow$ injected `database`).
- **Dependency Injection Rules**:
  - Only inject services genuinely consumed by the resulting class. Avoid service proliferation.
  - For service classes: register arguments in `<module>.services.yml` and inject via constructor.
  - For controllers and form classes: implement `create(ContainerInterface $container)` and pass injected services to the constructor.

### 3. Non-1:1 Transformations (Decomposition & Consolidation)
- **One-to-Many**: A single legacy D7 PHP file, `.inc` file, or monolithic hook implementation (e.g. `hook_menu()`) must be decomposed into dedicated, single-responsibility PSR-4 classes, plugins, and YAML route/link files.
- **Many-to-One**: Multiple legacy procedural helper scripts, hook implementations, or related class shims can be consolidated into a unified modern service class where cohesive.

### 4. hook_menu() Exhaustive Decomposition
In Drupal 7, `hook_menu()` handled page routing, menu items, tabs, contextual links, and form endpoints simultaneously. In modern Drupal, these are decoupled:
- **Routes**: Page callbacks, form routes, delivery callbacks $\rightarrow$ `<module>.routing.yml` pointing to Controller (`_controller`) or Form (`_form`).
- **Controllers & Forms**: Procedural page callbacks $\rightarrow$ `src/Controller/<Name>Controller.php` extending `ControllerBase`; procedural form callbacks $\rightarrow$ `src/Form/<Name>Form.php` extending `FormBase` or `ConfigFormBase`.
- **Access Checkers**: Procedural access callbacks $\rightarrow$ custom access check services in `src/Access/` implementing `AccessCheckInterface` registered in `.services.yml` with `_custom_access` route requirements.
- **Permissions**: Defined in `<module>.permissions.yml` and referenced via `_permission` route requirement.
- **Menu Links**: `MENU_NORMAL_ITEM` $\rightarrow$ `<module>.links.menu.yml`.
- **Local Tasks (Tabs)**: `MENU_LOCAL_TASK` / `MENU_DEFAULT_LOCAL_TASK` $\rightarrow$ `<module>.links.task.yml`.
- **Local Actions**: `MENU_LOCAL_ACTION` $\rightarrow$ `<module>.links.action.yml`.
- **Contextual Links**: `MENU_CONTEXT_PAGE` / `MENU_CONTEXT_INLINE` $\rightarrow$ `<module>.links.contextual.yml`.
- **Parameter Converters & Wildcard Loaders**: `%node`, `%user`, `%custom` loaders $\rightarrow$ ParamConverters or route parameter auto-upcasting.

### 5. Hook Modernization & Event Architecture
- **Custom Hooks (`module_invoke_all`, `module_invoke`)**: Modernized to Symfony Event Dispatcher:
  - Define custom `Event` class extending `Symfony\Contracts\EventDispatcher\Event` in `src/Event/`.
  - Dispatch event via injected `EventDispatcherInterface`.
  - Implement listeners as `EventSubscriberInterface` classes in `src/EventSubscriber/` tagged with `event_subscriber` in `.services.yml`.
- **Lifecycle & Request Hooks (`hook_init`, `hook_exit`, `hook_boot`)**:
  - Map to Symfony Kernel Events (`KernelEvents::REQUEST`, `KernelEvents::RESPONSE`, `KernelEvents::TERMINATE`) in an event subscriber or HTTP middleware.
- **Alter Hooks**:
  - `hook_form_alter()` / `hook_form_FORM_ID_alter()`: Retained in `.module` but must delegate business processing to injected services.
  - `hook_menu_alter()` $\rightarrow$ Route subscriber extending `RouteSubscriberBase`.
  - `hook_views_data_alter()`, `hook_views_query_alter()` $\rightarrow$ Retained in `.views.execution.inc` or Views plugins.
  - `hook_theme_registry_alter()`, `hook_js_alter()`, `hook_css_alter()` $\rightarrow$ Target `.theme` hooks or `hook_page_attachments_alter()`.
- **Subsystem Procedural Hooks**:
  - *Entity Lifecycles (`hook_node_*`, `hook_user_*`, `hook_entity_*`)* $\rightarrow$ Entity hooks in `.module` delegating to entity service / event subscriber, or custom entity class overrides (`preSave()`, `postSave()`).
  - *Blocks (`hook_block_info`, `hook_block_view`, `hook_block_configure`, `hook_block_save`)* $\rightarrow$ Block plugins extending `BlockBase` in `src/Plugin/Block/`.
  - *Access Control (`hook_permission`, `hook_node_access`)* $\rightarrow$ `<module>.permissions.yml`, custom access checkers, or entity access control handlers.
  - *Tokens (`hook_token_info`, `hook_tokens`)* $\rightarrow$ Retained in `.tokens.inc` with modern `BubbleableMetadata` caching.
  - *Mail (`hook_mail`)* $\rightarrow$ Retained in `.module` or modernized via Mail plugins / `plugin.manager.mail`.
  - *Cron (`hook_cron`)* $\rightarrow$ Retained in `.module` delegating to a dedicated cron service or QueueWorker plugin in `src/Plugin/QueueWorker/`.

### 6. State & Settings Modernization
- **Configuration (CMI)**: Static settings that should be deployed across environments map to Configuration Objects (`config/install/<module>.settings.yml` and `config/schema/`).
- **State API**: Dynamic environment-specific values (`last_cron_run`, synchronization timestamps) map to the `state` service (`\Drupal::state()` or injected `StateInterface`).

### 7. Entity, Custom Database & Repository Abstraction
- **Core Entity Queries**: Direct `db_query()` targeting core tables (`{node}`, `{users}`, `{taxonomy_term_data}`, `{file_managed}`) MUST be replaced by Entity Queries or Entity Storage via `EntityTypeManagerInterface`.
- **Custom Database Table Target Architecture Mapping**:
  - *Content Entity (`src/Entity/`)*: Appropriate when the table represents domain content, user submissions, or business objects with fieldable requirements, revisioning, or access control.
  - *Config Entity / Config API (`config.factory`)*: Appropriate when table stores site/module configuration, settings, or administrative options.
  - *State API (`\Drupal::state()`)*: Appropriate for transient, environment-specific timestamps, counters, or flags.
  - *KeyValue API (`keyvalue` / `keyvalue.expirable`)*: Appropriate for key-value collections, tokens, or temporary storage.
  - *Custom Repository Service (`src/Repository/`)*: Appropriate when non-entity relational data requires high-performance direct SQL access via injected `\Drupal\Core\Database\Connection`.
  - *Queue Storage (`@queue`)*: Appropriate when table stores asynchronous work payloads.
- **Database API & Query Builder Modernization**:
  - Procedural `db_query()`, `db_query_range()`, `db_select()` $\rightarrow$ Injected `Connection` service `$connection->query()`, `$connection->select()`, or Repository query methods.
  - Procedural `db_insert()`, `db_update()`, `db_delete()`, `db_merge()` $\rightarrow$ `$connection->insert()`, `$connection->update()`, `$connection->delete()`, `$connection->merge()`.
  - Transaction Modernization: Procedural `db_transaction()` $\rightarrow$ `$transaction = $connection->startTransaction()` with comprehensive `try { ... } catch (\Exception $e) { $transaction->rollBack(); ... }` error handling.
  - SQL Safety & Injection Hardening: Eliminate string concatenation in SQL queries; enforce named parameter arrays (`[':id' => $id]`). Dynamic SQL where query structure or tables cannot be verified statically must be marked `HUMAN_DECISION_REQUIRED` or `UNVERIFIED`.
- **Serialized Data Modernization**:
  - Migrate legacy PHP serialized strings (`serialize()` / `unserialize()`) to modern structured formats (JSON, typed entity properties, or typed arrays).
  - Explicitly flag serialized PHP objects requiring custom migration process plugins.
