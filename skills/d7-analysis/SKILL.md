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
Every custom PHP file, class, interface, trait, function, constructor, custom database table, and data-model artifact must reach an explicit outcome:
- **Approved Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Silent States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`. (Any presence of forbidden states triggers a fatal validation failure).

### 9. Custom Database & Schema Discovery (`hook_schema`)
Explicitly detect, inventory, and inspect all custom schema definitions in `*.install`, `*.module`, and include files:
- **Schema Definitions Detected**:
  - `hook_schema()` implementations returning schema arrays: `$schema['table_name'] = [...]`.
  - Columns: name, type (`serial`, `int`, `varchar`, `text`, `blob`, `numeric`, `float`), length/size (`tiny`, `small`, `medium`, `big`, `normal`), `not null`, `default`, `description`, `unsigned`.
  - Keys & Constraints: `primary key`, `unique keys`, `indexes`, compound indexes.
  - Foreign Key Definitions: explicit `foreign keys` declarations in `$schema` arrays or implicit code relationships.
  - Indicators of special storage: timestamps (`created`, `updated`, `changed`, `timestamp`), status flags (`status`, `enabled`, `active`), delta fields (`delta`), language fields (`language`).
- **Entity Reference Heuristics**:
  - Identify column names referencing Drupal entities: `uid` (user), `nid` / `vid` (node / node revision), `tid` (taxonomy term), `fid` (file), `cid` (comment), `entity_id` / `entity_type` (dynamic entity reference), `delta` (field item delta).
  - Cross-reference with codebase queries and joins to confirm whether an integer field genuinely represents an entity reference rather than an arbitrary internal identifier.

### 10. Install / Update / Uninstall Database Lifecycle Analysis
Detect and analyze database schema manipulations across module lifecycle hooks:
- **Lifecycle Hooks Detected**: `hook_install()`, `hook_uninstall()`, `hook_schema()`, `hook_update_N()`.
- **Schema Modification Functions**: `db_create_table()`, `db_drop_table()`, `db_add_field()`, `db_drop_field()`, `db_change_field()`, `db_add_index()`, `db_drop_index()`, `db_add_unique_key()`, `db_drop_unique_key()`, `db_add_primary_key()`, `db_drop_primary_key()`.
- **Lifecycle Role Classification**:
  - *Initial Schema*: Base table structure required for module operation.
  - *Historical Upgrade*: One-off historical migration from older versions (e.g. D6 $\rightarrow$ D7). Do NOT automatically recreate historical `hook_update_N()` scripts in D10/D11; account for the final resulting schema and data state.
  - *Runtime Table Management*: Tables dynamically created/dropped during module execution.
  - *Cleanup Logic*: Proper `hook_uninstall()` table and variable cleanup.

### 11. D7 Database API & Static SQL Query Analysis
Exhaustively inventory procedural D7 database API calls across all module source files:
- **Database APIs Detected**: `db_query()`, `db_query_range()`, `db_select()`, `db_insert()`, `db_update()`, `db_delete()`, `db_merge()`, `db_transaction()`, `db_set_active()`, `db_ignore_replication()`.
- **Static SQL Inspection**:
  - Parse SQL operations: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `JOIN` (INNER, LEFT, RIGHT), `UNION`, `GROUP BY`, `ORDER BY`, `HAVING`, subqueries, aggregations (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`), table locking (`FOR UPDATE`).
  - Trace target tables, column projections, join conditions, and filter expressions.
- **Dynamic SQL & Variable Table Detection**:
  - Detect dynamically constructed SQL strings (e.g., `db_query("SELECT ... FROM {" . $table_var . "}")` or `$sql = $base . $where_clause;`).
  - Flag dynamically constructed SQL where table or query structure cannot be statically verified as `[UNVERIFIED RESULT]` or `HUMAN_DECISION_REQUIRED` with explicit evidence.

### 12. SQL Safety & Parameterization Analysis
Analyze every custom SQL execution path for injection vulnerabilities and parameter safety:
- **Safety Patterns Detected**:
  - Named placeholders (`:uid`, `:status`) and positional placeholders (`%d`, `%s` in legacy D6-style wrappers).
  - Unsafe concatenation of user input or request variables (`$_GET`, `$_POST`, `$_REQUEST`, `$form_state['values']`).
  - Dynamic table names and column names derived from runtime configuration or user input.
  - Missing escaping or improper use of `db_escape_table()` / `db_like()`.
- **Modern Target Modernization**:
  - Classify target query architecture: Modern Database API (`\Drupal::database()`), Select Query Builder (`$connection->select(...)`), Entity Query (`\Drupal::entityQuery(...)`), or Custom Repository Service.
  - Any unresolved security-sensitive query pattern must be marked `HUMAN_DECISION_REQUIRED` or `UNVERIFIED`.

### 13. Data Semantics & Serialization Classification
Exhaustively classify stored data semantics and payload formats:
- **17 Data Semantic Categories**:
  - `CONTENT`: Editorial or user-generated domain records (e.g., articles, submissions, profiles).
  - `CONFIGURATION`: Site or module behavioral settings, options, flags.
  - `STATE`: Environment-specific runtime markers, timestamps, sequence counters.
  - `USER_DATA`: User-specific metadata, preferences, historical user actions.
  - `ENTITY_DATA`: Custom entities or field data attachments.
  - `FIELD_DATA`: Field-like key-value or delta storage associated with entities.
  - `RELATIONSHIP_DATA`: Cross-entity mappings, junction tables, many-to-many associations.
  - `TRANSACTION_DATA`: E-commerce orders, payments, audit logs, financial events.
  - `AUDIT_DATA`: Activity logs, revision histories, change tracking.
  - `CACHE_DATA`: Transient computed data, rendered output caches.
  - `QUEUE_DATA`: Asynchronous jobs, work items, retry queues.
  - `TEMPORARY_DATA`: Ephemeral session caches, temporary import buffers.
  - `INTEGRATION_DATA`: External system IDs, synchronization tokens, webhook payloads.
  - `LOOKUP_DATA`: Static code lists, postal codes, country/state lookup dictionaries.
  - `REFERENCE_DATA`: Reusable domain taxonomies, categories, classification tags.
  - `LEGACY_DATA`: Obsolete historical records retained for archival only.
  - `UNKNOWN`: Insufficient evidence to classify with certainty (triggers `HUMAN_DECISION_REQUIRED`).
- **Serialization Formats**:
  - Detect `serialize()` / `unserialize()` usage on text/blob columns.
  - Identify JSON payloads (`drupal_json_encode`, `json_decode`), base64 payloads, delimited strings (`explode`, `implode`), or HTML markup.
  - Explicitly flag serialized PHP objects (`O:`) and class-dependent structures that require migration transforms.

### 14. CRUD & Business Behavior Accounting
For every custom table, trace complete CRUD call trees across the codebase:
- **CREATE**: Trace all `db_insert()`, `db_merge()`, or raw `INSERT` callers (forms, API clients, queue workers, cron).
- **READ**: Trace all `db_query()`, `db_select()`, or raw `SELECT` callers (controllers, views plugins, blocks, services).
- **UPDATE**: Trace all `db_update()`, `db_merge()`, or raw `UPDATE` callers.
- **DELETE**: Trace all `db_delete()`, `hook_user_cancel()`, `hook_node_delete()`, or cleanup routines.
- **Transaction & Concurrency**:
  - Identify `db_transaction()`, explicit locking (`$txn = db_transaction()`), race-condition sensitive counters, atomic increment operations.
  - Ensure target D10/D11 architecture preserves transactional consistency.

---

## Output Reporting Standard
All discovery outputs must:
1. Provide verifiable file paths, class names, method signatures, table names, and line numbers (`[OBSERVED FACT]`).
2. Populate `custom_php_files`, `inc_files`, and `custom_database_tables` in `state/migration-manifest.yml`.
3. Flag any dynamic or unresolvable include / reflection / dynamic instantiation / dynamic SQL as `[UNVERIFIED RESULT]`.
