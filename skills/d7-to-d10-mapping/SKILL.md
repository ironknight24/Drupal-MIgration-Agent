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

### 6. Entity & Database Abstraction
- Direct `db_query()` targeting core tables (`{node}`, `{users}`) MUST be replaced by Entity Queries via `EntityTypeManagerInterface`.
- Direct `db_query()` targeting bespoke custom tables must be refactored into either:
  1. A custom Content Entity type (preferred for structured business data).
  2. The injected `Connection` service using parameterized SQL queries.

### 7. Hook Alter & Event Conversion
- System events (e.g., user login, response filters, routing alterations) map to Symfony `EventSubscriberInterface`.
- Form alters (`hook_form_alter()`) remain in `.module` but must delegate business processing to an injected service.
