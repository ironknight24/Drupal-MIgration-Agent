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

### 15. Generic & Custom Hook Discovery & Taxonomy
Recursively detect and catalog all procedural hook implementations across custom module source files (`*.module`, `*.inc`, `*.php`, `*.install`, `*.profile`, `*.drush.inc`):
- **Hook Name Resolution**:
  - Pattern matching: `{module}_{hook_name}(...)` or `{module}_{alter_hook_name}_alter(...)`.
  - Resolve function signature, arguments, return value expectations, invoking subsystems, and related hooks.
- **Hook Classification Taxonomy (9 Types)**:
  1. `CORE_HOOK`: Standard Drupal 7 core hook (e.g. `hook_init`, `hook_cron`, `hook_permission`, `hook_theme`, `hook_mail`).
  2. `CONTRIB_HOOK`: Hooks defined by contributed modules (e.g. `hook_views_data`, `hook_token_info`, `hook_ctools_plugin_api`).
  3. `CUSTOM_HOOK`: Custom extension points defined by custom modules via `module_invoke_all('{custom_hook}', ...)` or `module_invoke(...)`.
  4. `ALTER_HOOK`: Alterations modifying arrays or queries (`hook_form_alter`, `hook_menu_alter`, `hook_query_TAG_alter`).
  5. `ENTITY_HOOK`: Entity lifecycle hooks (`hook_node_insert`, `hook_user_update`, `hook_taxonomy_term_delete`).
  6. `FORM_HOOK`: Form builders, form validation, and submission handlers.
  7. `THEME_HOOK`: Preprocessors, theme declarations, and asset altering hooks (`hook_preprocess_*`, `hook_css_alter`).
  8. `INSTALL_UPDATE_HOOK`: Module installation, uninstallation, schema, and update hooks (`hook_install`, `hook_update_N`).
  9. `UNKNOWN_UNVERIFIED_HOOK`: Procedural function whose hook origin cannot be statically confirmed without runtime reflection.

### 16. Custom Hook Invocation & Modern Event Dispatching
Identify bespoke extension points created by custom modules:
- **Invocation Patterns**: `module_invoke_all('my_event', ...)`, `module_invoke('module', 'my_hook', ...)`, `drupal_alter('my_data', ...)`.
- **Target Modernization Architecture**:
  - Map custom hook invocations to Symfony Event Dispatcher (`\Drupal::service('event_dispatcher')->dispatch(...)` or injected `EventDispatcherInterface`).
  - Define custom Event classes (`src/Event/<EventName>Event.php`) extending `Symfony\Contracts\EventDispatcher\Event`.
  - Convert custom hook implementations into Symfony Event Subscribers (`src/EventSubscriber/<SubscriberName>.php`) implementing `EventSubscriberInterface`.

### 17. Alter Hook Behavioral Analysis
Analyze the behavioral impact of alter hooks:
- **Alter Hooks Discovered**: `hook_form_alter()`, `hook_form_FORM_ID_alter()`, `hook_menu_alter()`, `hook_views_data_alter()`, `hook_views_query_alter()`, `hook_query_TAG_alter()`, `hook_entity_info_alter()`, `hook_theme_registry_alter()`.
- **Analysis Matrix**: Trace modified data keys, injected validation/submit handlers, condition alterations, and downstream dependencies.

### 18. Mandatory hook_menu() Decomposition
Exhaustively dissect every router item in `hook_menu()` implementations:
- **Router Item Attributes Extracted**:
  - `path`: URL pattern, wildcards (`%`, `%node`, `%user`, `%custom_loader`), and load arguments.
  - `page callback` & `page arguments`: Callback function and parameter indices.
  - `access callback` & `access arguments`: Permission strings (`'access content'`) or custom access check functions.
  - `title`, `title callback`, `title arguments`, `description`.
  - `type`: `MENU_NORMAL_ITEM`, `MENU_CALLBACK`, `MENU_SUGGESTED_ITEM`, `MENU_LOCAL_TASK`, `MENU_DEFAULT_LOCAL_TASK`, `MENU_LOCAL_ACTION`, `MENU_CONTEXTUAL_TAB`.
  - `file`, `file path`, `delivery callback`, `theme callback`, `weight`, `menu_name`.
- **Non-1:1 Modernization Mapping**:
  - Decompose 1 `hook_menu()` into multiple modern D10/D11 artifacts:
    - Route Definitions $\rightarrow$ `<module>.routing.yml`
    - Page Callback $\rightarrow$ Controller class (`src/Controller/`) or Form class (`src/Form/`)
    - Access Callback $\rightarrow$ Route `_permission`, `_custom_access`, or `AccessCheckInterface` service (`src/Access/`)
    - Wildcard Loaders $\rightarrow$ Route parameter converters (`ParamConverterInterface`)
    - Menu Items $\rightarrow$ `<module>.links.menu.yml`
    - Tabs / Local Tasks $\rightarrow$ `<module>.links.task.yml`
    - Actions $\rightarrow$ `<module>.links.action.yml`
    - Contextual Links $\rightarrow$ `<module>.links.contextual.yml`

### 19. Subsystem Hook Modernization Mapping
Explicitly analyze and map specialized D7 subsystem hooks:
- **Form Behavior (`hook_form_*`, `hook_form_alter`, `hook_form_FORM_ID_alter`)**: Form builders, form validation callbacks, submit callbacks, AJAX callbacks, form state, `#states`, `#ajax`, `#submit`, `#validate`, `#tree`, `#access`, `#attached` assets $\rightarrow$ modern Form API classes (`FormBase`, `ConfigFormBase`, `ConfirmFormBase`).
- **Entity Lifecycle Hooks (`hook_node_insert`, `hook_node_update`, `hook_node_delete`, `hook_entity_insert`, `hook_entity_update`, `hook_entity_delete`, `hook_user_insert`, `hook_user_update`, `hook_user_delete`, `hook_taxonomy_term_insert`, `hook_taxonomy_term_update`, `hook_taxonomy_term_delete`, `hook_comment_insert`, `hook_comment_update`, `hook_comment_delete`, `hook_file_insert`, `hook_file_update`, `hook_file_delete`, `hook_file_presave`)**: Pre/post save logic, side effects, notifications, presave, postsave $\rightarrow$ modern entity hooks or Event Subscribers (`hook_ENTITY_TYPE_insert`, `hook_ENTITY_TYPE_presave`).
- **Access Control Hooks (`hook_permission`, `hook_node_access`, `hook_file_download`, `user_access`)**: Permissions and granular access checks $\rightarrow$ `<module>.permissions.yml`, Entity Access Control Handlers (`EntityAccessControlHandler`), or Custom Access Checkers implementing `AccessCheckInterface`. Ambiguous access logic must be flagged as `HUMAN_DECISION_REQUIRED` or `UNVERIFIED`.
- **Theme & Rendering Hooks (`hook_theme`, `hook_theme_registry_alter`, `hook_preprocess_*`, `hook_process_*`, `hook_page_build`, `hook_page_alter`, `hook_html_head`, `hook_css_alter`, `hook_js_alter`)**: Template registrations, render array alterations, and assets $\rightarrow$ Twig templates, `<theme>.theme` preprocess functions, and `<module>.libraries.yml`.
- **Block Hooks (`hook_block_info`, `hook_block_view`, `hook_block_configure`, `hook_block_save`)**: Procedural block callbacks $\rightarrow$ modern Block Plugin classes (`src/Plugin/Block/`) extending `BlockBase` with annotations/attributes.
- **Views Hooks (`hook_views_data`, `hook_views_data_alter`, `hook_views_query_alter`, `hook_views_pre_execute`, `hook_views_post_execute`, `hook_views_pre_render`, `hook_views_post_render`)**: Custom views data, query alters, and render handlers $\rightarrow$ modern `hook_views_data()` and Views plugins.
- **Token Hooks (`hook_token_info`, `hook_tokens`)**: Token definitions and replacements $\rightarrow$ modern `hook_token_info()`, `hook_tokens()`, and `BubbleableMetadata` caching.
- **Mail Hooks (`hook_mail`)**: Email formatting and body construction $\rightarrow$ modern `MailInterface` plugins or Mail Manager service.
- **Cron & Request Lifecycle Hooks (`hook_cron`, `hook_init`, `hook_exit`, `hook_boot`)**: Scheduled jobs and request interceptors $\rightarrow$ Cron services, QueueWorker plugins (`src/Plugin/QueueWorker/`), or Symfony Kernel Event Subscribers (`KernelEvents::REQUEST`, `KernelEvents::RESPONSE`, `KernelEvents::TERMINATE`).

### 20. Hook Call Graph & Execution Ordering
- **Call Graph Dependencies**: Trace functions, services, database queries, and config objects invoked by every hook.
- **Execution Ordering Constraints**: Account for module weight (`{system}.weight`), `hook_module_implements_alter()`, execution_order, alter_order, presave vs postsave lifecycle timings, and form validation sequences.

---

## Output Reporting Standard
All discovery outputs must:
1. Provide verifiable file paths, class names, method signatures, table names, hook names, and line numbers (`[OBSERVED FACT]`).
2. Populate `custom_php_files`, `inc_files`, `custom_database_tables`, and `hook_implementations` in `state/migration-manifest.yml`.
3. Flag any dynamic or unresolvable include / reflection / dynamic instantiation / dynamic SQL / dynamic hook call as `[UNVERIFIED RESULT]`.
