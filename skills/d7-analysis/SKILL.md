---
name: d7-analysis
description: Procedural and object-oriented inspection heuristics for Drupal 7 modules, PHP classes, constructors, interfaces, traits, legacy .inc files, database schemas, and variables without mutating source files.
version: 1.2.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Drupal 7 Codebase Analysis Skill

## Overview
This skill provides structured, non-destructive heuristics for inspecting Drupal 7 codebases, custom modules, PHP classes, interfaces, traits, legacy `.inc` files, themes, and database schemas. It explicitly discovers, dissects, and accounts for all custom PHP source files and OOP classes—analyzing constructors, dependencies, caller trees, autoloading mechanisms, and legacy APIs to prepare for modern Drupal 10/11 PSR-4 re-engineering.

---

## Technical References
For deep technical catalogs, consult:
- [Drupal 7 Core APIs Reference](../../references/drupal-7/apis.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)
- [Drupal 10 & 11 Architecture Reference](../../references/drupal-10/architecture.md)

---

## Analysis Workflow & Heuristics

### 1. Recursive Source File Discovery & Inventory
For every custom module in scope, recursively discover all PHP source files regardless of directory nesting:
- **Target File Extensions**: `*.php`, `*.inc`, `*.module`, `*.install`, `*.profile`, `*.drush.inc`, `*.admin.inc`, `*.pages.inc`, `*.forms.inc`.
- **Zero Naming Assumptions**: Never assume PHP or `.inc` files follow fixed naming conventions (`filename != architecture`). Discover files at the module root, in `includes/`, `lib/`, `classes/`, `src/`, `admin/`, `commands/`, or arbitrary subdirectories (e.g., `module.inc`, `admin.inc`, `pages.inc`, `forms.inc`, `functions.inc`, `includes/foo.inc`, `includes/bar.inc`, `custom-command.inc`, `arbitrary-name.inc`, `MyProcessor.php`, `LegacyClass.php`, `arbitrary-name.php`).
- **Discovery Output**: Record relative path, file type, line count, byte size, and detected constructs in the manifest.

### 2. Custom OOP PHP Class Discovery
For every discovered PHP source file, inspect and extract all OOP structures:
- **Structures Identified**:
  - Concrete classes, abstract classes, interfaces, traits, and anonymous classes.
  - Namespaces (if present in D7/PSR-0 code) and aliases (`use` statements).
  - Class inheritance (`extends ParentClass`) and interface implementations (`implements InterfaceA, InterfaceB`).
  - Trait usage (`use TraitName;`).
  - Class constants (`const CONST_NAME = ...;`).
  - Class properties: visibility (`public`, `protected`, `private`), typehints (if modern PHP), default values, static properties (`static $property`).
  - Methods: visibility (`public`, `protected`, `private`), static methods (`public static function ...`), abstract methods, final methods, return types.
  - Destructors (`__destruct()`) and magic methods (`__get`, `__set`, `__call`, `__toString`).
- **Unverified Constructs**: If complex dynamic code generation or `eval()` prevents static AST resolution, mark as `[UNVERIFIED RESULT]`.

### 3. Constructor & Initialization Analysis
Explicitly analyze every class constructor:
- **Constructor Types Recognized**:
  - Modern PHP constructor: `public function __construct(...)` or `__construct()`.
  - Legacy PHP4 / Drupal 7 constructor pattern: `public function ClassName(...)` or `ClassName()` matching the enclosing class name.
  - Static factory initialization: `public static function create(...)` or `public static function getInstance(...)`.
- **Constructor Inspection Matrix**:
  - Constructor parameters, parameter typehints, and default values.
  - Instantiations inside constructor (`new ExternalHelper()`).
  - Global variable references (`global $user, $language, $conf;`, `$GLOBALS['...']`).
  - Procedural Drupal 7 API calls (`variable_get()`, `db_query()`, `drupal_set_message()`, `module_load_include()`).
  - Direct database / storage calls, configuration access, current user access, and entity loads.
  - External network / filesystem calls (`drupal_http_request()`, `file_get_contents()`).
  - Side effects executed during construction.
- **Architectural Constructor Role**:
  - Classify initialization role: *Dependency Injection candidate*, *Service Locator pattern*, *Global State Dependency*, *Hidden Dependency*, *Configuration Dependency*, *Runtime Side Effect*, or *Legacy Procedural Wrapper*.

### 4. Class Instantiation & Caller Analysis
Identify where custom classes and functions are instantiated and consumed:
- **Search Patterns**:
  - Object creation: `new ClassName(...)`, `new ClassName()`, `new \Namespace\ClassName(...)`.
  - Static method calls: `ClassName::staticMethod(...)`.
  - Static property access: `ClassName::$staticProp`.
  - Polymorphic / dynamic creation: `new $class_var(...)` (flagged as `[UNVERIFIED RESULT]`).
  - Callbacks: `[$object, 'methodName']`, `['ClassName', 'staticMethod']`.
  - Cross-module consumers across all in-scope custom modules.

### 5. Autoloading & Include / Require Analysis
Analyze how each custom PHP file and class becomes available in the D7 runtime:
- **Loading Mechanisms Detected**:
  - Direct PHP includes: `include`, `include_once`, `require`, `require_once`.
  - Drupal info autoloading: `files[] = lib/MyClass.php` in `{module}.info`.
  - Drupal include helpers: `module_load_include('inc', '{module}', '{name}')`, `module_load_include('php', ...)`.
  - Form state includes: `form_load_include($form_state, 'inc', '{module}', '{name}')`.
  - CTools / Plugin loading: `ctools_include(...)`, `ctools_plugin_load_includes(...)`.
  - Custom registry / SPL autoloaders (`spl_autoload_register(...)`).
  - Menu routing declarations: `hook_menu()` items with `'file' => '...'`.
- **Modernization Target**: Do NOT preserve manual include calls in D10/D11; migrate classes to PSR-4 (`src/`) with Composer/Drupal autoloading.

### 6. Standardized Architectural Taxonomy
Classify every custom PHP class, interface, trait, and standalone function into exactly one of the standardized architectural categories:
1. `CONTROLLER_PAGE` / `CONTROLLER`: Page routing, rendering callbacks, REST/JSON output endpoints.
2. `FORM_HANDLER` / `FORM`: Form definition, validation, submission, and AJAX handling.
3. `SERVICE_BUSINESS_LOGIC`: Reusable business logic, calculations, domain workflows.
4. `PLUGIN_CANDIDATE` / `PLUGIN`: Block, field formatter, field widget, views handler, or CTools plugin behavior.
5. `EVENT_SUBSCRIBER`: Lifecycle hooks, state change reactions, event-driven triggers.
6. `ACCESS_CHECKER`: Custom permission checks, route access callbacks, entity access logic.
7. `ENTITY_FIELD_LOGIC` / `ENTITY_LOGIC` / `FIELD_LOGIC`: Entity operations, bundle definitions, custom field storage/formatting.
8. `QUEUE_WORKER`: Asynchronous job processors, queue processing logic.
9. `BATCH_PROCESSOR`: Step-by-step batch operations and completion callbacks.
10. `CRON_HANDLER`: Scheduled recurring tasks, periodic maintenance jobs.
11. `DRUSH_COMMAND`: CLI commands, Drush generators, maintenance scripts.
12. `CONFIGURATION_HANDLER`: Settings forms, configuration read/write schemas.
13. `THEME_RENDERER`: Twig/theme preprocessors, render array builders, template logic.
14. `UTILITY_HELPER`: Generic string, array, date, or math manipulation helpers.
15. `DATABASE_DATA_ACCESS` / `DATA_ACCESS`: Direct SQL queries, custom schema definitions, complex joins.
16. `INTEGRATION_CLIENT`: External web services, REST/SOAP/GraphQL clients, webhook receivers.
17. `VALUE_OBJECT`: Immutable data structures, DTOs, typed parameter bags.
18. `DOMAIN_OBJECT`: Domain entities, models, state machine objects.
19. `TEST_SUPPORT`: SimpleTest cases, mock fixtures, test helpers.
20. `LIBRARY_EXTERNAL_DEPENDENCY`: Bundled third-party libraries, vendor SDK shims.
21. `LEGACY_OBSOLETE`: Dead code, deprecated D6-era wrappers, obsolete workarounds.
22. `HUMAN_DECISION_REQUIRED` / `UNVERIFIED`: Ambiguous intent, unresolved dynamic behavior, or unverified results.

### 7. Non-1:1 Architectural Re-engineering & Dependency Injection
- **Non-1:1 Transformations**:
  - *One-to-Many*: A single legacy PHP file containing mixed duties (e.g. data processing, form building, page rendering) must be decomposed into distinct PSR-4 classes (e.g., `src/Service/DataProcessor.php`, `src/Form/SettingsForm.php`, `src/Controller/ViewController.php`).
  - *Many-to-One*: Multiple related procedural helper files or procedural shims can be consolidated into a cohesive modern service.
- **Dependency Injection Modernization**:
  - Extract global references (`$user`, `$language`, `variable_get()`, `db_query()`) and convert to constructor DI (`EntityTypeManagerInterface`, `Connection`, `ConfigFactoryInterface`, `AccountProxyInterface`).
  - Avoid service proliferation; only inject dependencies genuinely utilized by the modernized class.

### 8. Approved Outcome States vs Forbidden Silent States
Every custom PHP file, class, interface, trait, function, and constructor must reach an explicit outcome:
- **Approved Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Silent States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`. (Any presence of forbidden states triggers a fatal validation failure).

---

## Output Reporting Standard
All discovery outputs must:
1. Provide verifiable file paths, class names, method signatures, and line numbers (`[OBSERVED FACT]`).
2. Populate `custom_php_files` and `inc_files` in `state/migration-manifest.yml`.
3. Flag any dynamic or unresolvable include / reflection / dynamic instantiation as `[UNVERIFIED RESULT]`.
