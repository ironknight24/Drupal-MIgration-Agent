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

### 21. Exhaustive Configuration, State & Variable Discovery
Discover all configuration, variable, state, settings, and persistent key/value access patterns across `*.module`, `*.inc`, `*.php`, `*.install`, `*.profile`, `*.drush.inc`, and `.info` files:
- **D7 Variable API**: `variable_get()`, `variable_set()`, `variable_del()`, `variable_initialize()`, `variable_realm_*()`, variable defaults, `$conf` array references.
- **D7 Configuration & Admin Forms**: `system_settings_form()`, `system_settings_save()`, `system_settings_form_submit()`, `variable_get()` inside form builders, configuration forms, admin settings callbacks, settings validation, submit handlers.
- **Direct Global & Environment Configuration**: `$conf`, global configuration arrays, `$GLOBALS`, static configuration caches, constants representing configuration, environment-derived configuration (`getenv()`, `$_ENV`, `$_SERVER`), `settings.php` references.
- **Persistent State & Value Storage**: `variable_get/set/del` used as flags or timestamps, state-like persistent values, `cache_get/set` used as persistent application state, custom tables used specifically to persist configuration/state (`db_query()` / `db_select()`), key/value storage patterns, serialized configuration values, JSON configuration values, arrays stored as serialized variables, counters/timestamps/locks stored in variables.
- **Module Lifecycle Configuration**: `hook_install()`, `hook_uninstall()`, `hook_update_N()`, variable initialization, variable cleanup, default configuration creation, configuration migration logic, update-time variable transformations.

### 22. 20-Type Configuration Taxonomy
Classify every discovered configuration/state artifact into the generic taxonomy:
1. `D7_VARIABLE`: Standard variable accessed via `variable_get()`.
2. `D7_VARIABLE_DEFAULT`: Default fallback value specified in `variable_get()` or module constants.
3. `D7_VARIABLE_WRITE`: Runtime or administrative write via `variable_set()`.
4. `D7_VARIABLE_DELETE`: Variable cleanup via `variable_del()`.
5. `D7_GLOBAL_CONFIG`: Global configuration array or `$conf` / `$GLOBALS` access.
6. `D7_FORM_SETTING`: Form field bound to a configuration variable in standard forms.
7. `D7_ADMIN_SETTING`: Administrative setting managed via `system_settings_form()`.
8. `D7_RUNTIME_SETTING`: Runtime operational flag or threshold evaluated during requests.
9. `D7_PERSISTENT_STATE`: Non-configuration persistent state (timestamp, counter, lock, sync marker).
10. `D7_CACHE_STATE`: Persistent application state stored incorrectly in Drupal cache bins.
11. `D7_CUSTOM_TABLE_STATE`: Dedicated custom key-value or configuration table.
12. `D7_SERIALIZED_VALUE`: Complex PHP data structure persisted via `serialize()` / `variable_set()`.
13. `D7_JSON_VALUE`: JSON-encoded configuration or payload.
14. `D7_ENVIRONMENT_VALUE`: Environment/deployment-specific value, external endpoint, or credential.
15. `D7_INSTALL_CONFIGURATION`: Default variable initialized during `hook_install()`.
16. `D7_UPDATE_CONFIGURATION`: Variable created, renamed, or transformed in `hook_update_N()`.
17. `D7_UNINSTALL_CLEANUP`: Variable deleted during `hook_uninstall()`.
18. `D7_DERIVED_CONFIGURATION`: Dynamically computed or merged configuration value.
19. `D7_EXTERNAL_CONFIGURATION`: Configuration pulled from external API, service, or remote file.
20. `D7_UNKNOWN_UNVERIFIED`: Ambiguous, dynamically assembled, or unresolvable configuration key.

### 23. Read / Write / Delete Lifecycle Analysis
For every discovered configuration artifact, trace the complete lifecycle:
- **Reads**: Function/class reading it, location evidence, fallback behavior, type expectations, conditional logic, downstream consumers.
- **Writes**: Function/class writing it, written value types, triggering lifecycle stage (`INSTALL`, `UPDATE`, `ADMIN_FORM`, `RUNTIME`, `CRON`, `BATCH`, `REQUEST`, `INTEGRATION`).
- **Deletes**: Location of deletion, uninstall cleanup verification, migration cleanup.
- **Lifecycle Chain**: Trace `CREATE -> READ -> MODIFY -> DELETE` and identify all callers and dependencies.

### 24. Default Value Accounting
Exhaustively capture and verify default values:
- **Key & Fallback Value**: Variable key, default value literal, default data type (`string`, `int`, `float`, `bool`, `array`, `object`, `null`, `dynamic`).
- **Default Source**: `static_literal`, `variable_get_fallback`, `hook_install`, `conf_override`, `dynamic_expression`, `unknown`.
- **Static vs Dynamic**: Determine whether the default is a static literal or dynamically computed at runtime.
- **Context Dependencies**: Identify if the default depends on user, role, language, environment, site, domain, module state, database query, or external service. Never assume `variable_get()` second parameter is the authoritative business default if overridden during installation or bootstrap.

### 25. Serialized & JSON Value Analysis
- **Serialization Patterns**: Detect `serialize()`, `unserialize()`, `json_encode()`, `json_decode()`, nested configuration structures, and array structures stored in variables.
- **Data Type & Schema Extraction**: Determine structural schema, key-value mappings, required/optional fields, and type constraints.
- **Opaque PHP Objects & Complex State**: Serialized PHP classes, closures, or ambiguous binary payloads must be classified as `UNVERIFIED` or `HUMAN_DECISION_REQUIRED`. Never silently discard or truncate serialized data structures.

### 26. Configuration Forms & Admin Semantics Preservation
- **Form Discovery**: Detect `system_settings_form()`, custom administration form builders, validation callbacks (`_validate`), submit handlers (`_submit`), AJAX settings forms, and permission requirements.
- **Admin Semantics Preservation**: Preserve configuration key mappings, form element validation rules, dependency toggles (`#states`), and submit transformations.
- **Modern Target Mapping**: Map D7 admin settings forms to `ConfigFormBase` classes (`src/Form/SettingsForm.php`), defining `getEditableConfigNames()`, `buildForm()`, `validateForm()`, `submitForm()`, and linking routes in `<module>.routing.yml` and menu links in `<module>.links.menu.yml`.

### 27. Install, Update & Uninstall Lifecycle Accounting
- **Installation Defaults**: Trace `hook_install()` variable creations and initializations $\rightarrow$ modern default configuration files (`config/install/<module>.settings.yml`).
- **Update Hook Transformations**: Trace `hook_update_N()` variable renames, value migrations, structural splits/merges, and schema updates $\rightarrow$ modern `hook_post_update_NAME()` or `hook_update_N()`.
- **Uninstall Cleanup**: Trace `hook_uninstall()` `variable_del()` calls $\rightarrow$ modern CMI automatic config deletion or State API cleanup in `hook_uninstall()`.

### 28. Exhaustive Entity & Field Discovery
Discover all core, contrib, and custom entity types, bundles, properties, and field implementations across `*.module`, `*.inc`, `*.php`, `*.install`, `*.profile`, and `.info` files:
- **Core Entity Types**: `node`, `user`, `taxonomy_term`, `taxonomy_vocabulary`, `comment`, `file`.
- **Contrib & Custom Entity Systems**: Entity API implementations (`hook_entity_info()`, `entity_get_info()`), custom entity controllers extending `DrupalDefaultEntityController` or `EntityAPIController`, custom entity tables, entity metadata wrappers (`entity_metadata_wrapper()`), and entity properties (`hook_entity_property_info()`).
- **Entity Metadata & Keys Extraction**: For every entity type, capture `entity_type`, `bundle`, `label`, `base_table`, `data_table`, `revision_table`, `translation_table`, `controller_class`, `access_callback`, `entity_keys` (`id`, `revision`, `bundle`, `label`, `language`, `uuid`, `status`), fieldability, ownership, and revision support.
- **Content vs Config Entity Classification**: Determine whether discovered entities classify as a `content_entity` (storing transactional, revisionable, user-generated business data) or a `config_entity` (storing administrative settings, reusable schemas, mappings, exportable configurations, or workflows).

### 29. D7 Entity API & EntityFieldQuery Pattern Discovery
Trace all procedural and object-oriented entity interactions:
- **Entity CRUD APIs**: `entity_load()`, `entity_load_multiple()`, `entity_save()`, `entity_delete()`, `entity_extract_ids()`, `entity_id()`, `entity_uri()`, `entity_get_info()`, `entity_view()`, `entity_access()`.
- **Subsystem APIs**: Node APIs (`node_load`, `node_save`, `node_view`), user APIs (`user_load`, `user_save`), taxonomy APIs (`taxonomy_term_load`, `taxonomy_vocabulary_machine_name_load`), file APIs (`file_load`, `file_save`), comment APIs (`comment_load`, `comment_save`).
- **EntityFieldQuery (EFQ)**: Detect `new EntityFieldQuery()`, `entityCondition()`, `propertyCondition()`, `fieldCondition()`, `fieldOrderBy()`, `propertyOrderBy()`, `range()`, and `execute()` call patterns across custom code.

### 30. Field & Field Storage Taxonomy
Exhaustively discover and classify all Drupal 7 fields across `field_info_field()`, `field_info_instance()`, `field_info_fields()`, `field_info_instances()`, `field_create_field()`, `field_create_instance()`, `field_update_field()`, `field_update_instance()`, `field_delete_field()`, `field_delete_instance()`, `field_attach_load()`, `field_attach_presave()`, `field_attach_insert()`, `field_attach_update()`, `field_attach_delete()`, `field_get_items()`, `field_view_field()`, `field_form_field()`, and `.install` schema declarations:
- **Field Attributes & Storage**: Field name, entity type, bundle, field type, cardinality (single: 1, unlimited: -1, specific: N), required status, translatability, revisionability, storage backend (`SQL_DEFAULT`, `CUSTOM_TABLE`, `COMPUTED`), storage table, schema, indexes, language columns, delta columns, entity id relationship, revision relationship, bundle relationship, formatters, widgets, validation constraints, default values, and allowed values.
- **Generic Field Taxonomy**: Text (`text`, `long text`, `text_long`, `text_with_summary`), Numeric (`number_integer`, `integer`, `decimal`, `float`, `number_decimal`, `number_float`), Boolean (`list_boolean`, `boolean`), Date/Time (`date`, `datetime`, `datestamp`), Options/List (`list`, `list_text`, `list_integer`), References (`taxonomy reference`, `taxonomy_term_reference`, `entity reference`, `entityreference`, `user reference`, `user_reference`, `node_reference`), Media (`file`, `image`), Links (`link`), Addresses (`addressfield`), and custom/contrib field types.

### 31. Entity References & Relationship Topologies
Discover and map cross-entity relationship graphs:
- **Reference Types**: `entityreference`, `taxonomy_term_reference`, `user_reference`, `node_reference`, `taxonomy reference`, `user reference`, `file_usage`, and custom foreign key joins.
- **Relationship Metadata**: Source entity, source field, target entity type, target bundle, cardinality, dependency direction, cascade delete behavior, orphan cleanup, and reference validation constraints.

### 32. Revision Discovery & Historical Semantics
Identify entity revisioning mechanisms:
- **Revision Artifacts & Mechanics**: Revision tables (`{node_revision}`, `{custom_entity_revision}`), revision IDs (`vid`, `revision_id`), revision log fields, timestamps, revision authors (`uid`), revision flags, revision callbacks, revision loading, revision comparison, revision publishing, and `default_revision` flags.
- **Revision APIs & Operations**: `node_revision_delete()`, `entity_revision_load()`, custom revision compare routines, and revision publishing logic. Determine whether full revision history is business-critical for migration or if latest active revision suffices (`HUMAN_DECISION_REQUIRED`).

### 33. Translation, Language & Multilingual Semantics
Exhaustively analyze multilingual entity behavior:
- **Language Identifiers**: `$language`, `$language_content`, `LANGUAGE_NONE` (`'und'`), field-level language keys (`$entity->field_name[LANGUAGE_NONE]`), and language negotiation assumptions.
- **Entity & Content Translation**: Entity Translation (`entity_translation` module, `entity translations`), Content Translation (`translation` module, `node translations`), translation tables, translatable field columns, and language-specific default values.

### 34. Entity Lifecycle, Access & Security Analysis
- **Lifecycle Tracing**: `create -> load -> presave -> insert/update -> postsave -> delete -> revision -> translation`. Trace all side effects, database writes, configuration changes, external API calls, cache invalidation, and queues.
- **Entity Access Control**: `entity_access()`, `node_access()`, `hook_node_access()`, `hook_entity_access()`, custom access callbacks, permission grants (`hook_node_grants`, `hook_node_access_records`), field-level access (`hook_field_access`), and bundle restrictions. Ambiguous security logic must be flagged as `HUMAN_DECISION_REQUIRED`.

### 35. Entity Query & Storage Modernization
- **Modern Query Mapping**: Map `EntityFieldQuery` and direct entity SQL queries to modern `EntityQuery` (`\Drupal::entityQuery()`) or injected `EntityTypeManagerInterface` / `EntityStorageInterface` query methods.
- **Storage Handlers**: Map custom entity controllers and storage mechanisms to modern `SqlContentEntityStorage` or custom storage handlers extending `ContentEntityStorageBase`.

### 36. Entity Rendering, Formatters, Widgets & Display Modes
- **Display Configurations**: Identify `entity_view()`, `field_view_field()`, custom field formatters (`hook_field_formatter_info`), custom field widgets (`hook_field_widget_info`), view modes, and form modes $\rightarrow$ modern `EntityViewBuilder`, Plugin formatters (`@FieldFormatter`), Plugin widgets (`@FieldWidget`), and View Mode configuration entities.

### 37. Target Architecture Taxonomy & Migration Strategies
- **Target Architecture Classifications**: `CONTENT_ENTITY`, `CONFIG_ENTITY`, `ENTITY_TYPE`, `BUNDLE`, `ENTITY_STORAGE`, `ENTITY_ACCESS_HANDLER`, `ENTITY_QUERY`, `FIELD_STORAGE`, `FIELD_CONFIG`, `FIELD_TYPE`, `FIELD_WIDGET`, `FIELD_FORMATTER`, `ENTITY_REFERENCE`, `REVISIONABLE_ENTITY`, `TRANSLATABLE_ENTITY`, `TRANSLATION_HANDLER`, `PLUGIN`, `SERVICE`, `REPOSITORY`, `CUSTOM_STORAGE`, `CONFIGURATION`, `STATE`, `EXTERNAL_SYSTEM`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Standardized Migration Strategies**: `DIRECT_ENTITY_MIGRATION`, `TRANSFORMED_ENTITY_MIGRATION`, `ENTITY_TYPE_REBUILD`, `BUNDLE_REBUILD`, `FIELD_REBUILD`, `FIELD_TRANSFORMATION`, `REFERENCE_REMAP`, `REVISION_MIGRATION`, `TRANSLATION_MIGRATION`, `CONFIG_ENTITY_MIGRATION`, `CUSTOM_STORAGE_MIGRATION`, `CONTENT_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

---

## Output Reporting Standard
All discovery outputs must:
1. Provide verifiable file paths, class names, method signatures, table names, hook names, config keys, entity types, field names, and line numbers (`[OBSERVED FACT]`).
2. Populate `custom_php_files`, `inc_files`, `custom_database_tables`, `hook_implementations`, `configuration_state_items`, and `entities_fields_items` in `state/migration-manifest.yml`.
3. Flag any dynamic or unresolvable include / reflection / dynamic instantiation / dynamic SQL / dynamic hook call / dynamic config key / dynamic entity type as `[UNVERIFIED RESULT]` or `HUMAN_DECISION_REQUIRED`.
