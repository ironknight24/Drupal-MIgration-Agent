---
name: d7-to-d10-mapping
description: Behavioral and architectural mapping rules for converting procedural Drupal 7 APIs and legacy custom PHP classes into modern Drupal 10/11 object-oriented patterns.
version: 1.1.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep
---

# Drupal 7 to Drupal 10/11 Architectural Mapping Skill

## Overview
This skill provides the architectural mapping rules required to translate Drupal 7 procedural constructs, legacy custom PHP classes, constructors, interfaces, traits, and `.inc` files into modern Symfony/Drupal 10 and Drupal 11 object-oriented paradigms, prioritizing Dependency Injection, PSR-4 autoloading, service containers, and testability.

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
- **One-to-Many**: A single legacy D7 PHP or `.inc` file containing mixed procedural duties or monolithic classes must be decomposed into dedicated, single-responsibility PSR-4 classes.
- **Many-to-One**: Multiple legacy procedural helper scripts or related class shims can be consolidated into a unified modern service class where cohesive.

### 4. hook_menu() Separation
In Drupal 7, `hook_menu()` handled page routing, menu items, tabs, contextual links, and form endpoints simultaneously. In modern Drupal, these are decoupled:
- Page URLs & Handlers -> `<module>.routing.yml` & `ControllerBase`
- Menu links -> `<module>.links.menu.yml`
- Local tasks (tabs) -> `<module>.links.task.yml`
- Contextual actions -> `<module>.links.action.yml`
- Permission definitions -> `<module>.permissions.yml`

### 5. State & Settings Modernization
- **Configuration (CMI)**: Static settings that should be deployed across environments map to Configuration Objects (`config/install/<module>.settings.yml` and `config/schema/`).
- **State API**: Dynamic environment-specific values (`last_cron_run`, synchronization timestamps) map to the `state` service (`\Drupal::state()` or injected `StateInterface`).

### 6. Entity, Custom Database & Repository Abstraction
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

### 7. Hook Alter & Event Conversion
- System events (e.g., user login, response filters, routing alterations) map to Symfony `EventSubscriberInterface`.
- Form alters (`hook_form_alter()`) remain in `.module` but must delegate business processing to an injected service.
