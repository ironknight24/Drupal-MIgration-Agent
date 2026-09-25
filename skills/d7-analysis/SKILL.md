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

### 1. Exact Path Derivation & Recursive Source File Discovery
For every custom module in scope, derive its exact path `SOURCE_MODULE_PATH = os.path.join(source.path, source.custom_modules_path, MODULE)` from `migration.config.yml`. Confine all discovery strictly to `SOURCE_MODULE_PATH` without broad searches across adjacent directories (Rule 16 & Rule 18):
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

### 38. Exhaustive Form & Form Builder Discovery
Discover all Drupal 7 forms, builders, and callbacks across `.module`, `.inc`, `.php`, `.install`, `.profile`, and `.drush.inc` files:
- **Form Builder Functions**: Detect standard form builders (`function module_form($form, &$form_state)`), named form builders, and form constructor functions.
- **Form Invocation APIs**: `drupal_get_form()`, `drupal_build_form()`, `drupal_form_submit()`, `drupal_execute()`, `drupal_rebuild_form()`, and programmatic form dispatches.
- **Entry Points & Routing**: Menu callbacks (`hook_menu()` with `drupal_get_form`), controller callbacks, entity edit/create operations, admin settings pages, and AJAX callback endpoints.
- **Dynamic & Programmatic Forms**: Detect dynamically constructed form IDs, variable builder callbacks, and render array form inclusions (`$form['#type'] = 'form'`). Flag dynamic form IDs with unknown builders as `UNVERIFIED` or `HUMAN_DECISION_REQUIRED`.

### 39. Drupal 7 Form API Structures & Property Taxonomy
Exhaustively parse Form API element structures and property declarations:
- **Element Types**: `#type` (`textfield`, `textarea`, `select`, `checkbox`, `checkboxes`, `radios`, `value`, `hidden`, `submit`, `button`, `file`, `managed_file`, `fieldset`, `container`, `vertical_tabs`, `markup`, `item`, `tableselect`, `date`, `password`, etc.).
- **Core Form Properties**: `#title`, `#description`, `#required`, `#default_value`, `#value`, `#return_value`, `#options`, `#tree`, `#parents`, `#weight`, `#access`, `#disabled`, `#attributes`, `#prefix`, `#suffix`, `#markup`, `#theme`, `#theme_wrappers`, `#states`, `#ajax`, `#validate`, `#submit`, `#element_validate`, `#after_build`, `#pre_render`, `#process`, `#attached`, `#limit_validation_errors`, `#executes_submit_callback`, `#value_callback`, `#input`.
- **Attached Assets**: `#attached` arrays defining JavaScript (`js`), CSS stylesheets (`css`), settings (`js` settings array), and library attachments (`library`).

### 40. Form Validation & Submission Call Graph
Trace the complete validation and submission execution paths:
- **Validation Handlers**: Form-level validation (`#validate`, `hook_form_validate`, `hook_form_FORM_ID_validate`), element-level validation (`#element_validate`), custom validation callbacks, `form_set_error()`, `form_error()`, cross-field validation rules, and entity validation invocations.
- **Submission Handlers**: Form-level submit callbacks (`#submit`, `hook_form_submit`, `hook_form_FORM_ID_submit`), button-specific submit callbacks, database transactions, entity saves, configuration writes (`variable_set()`), state updates, file operations, queue insertions, email dispatches, and cache clearing.
- **Side Effect & Call Graph Tracing**: Map `Form -> Validation -> Submit -> Database / Config / Entity / Service / Redirect / Message`.

### 41. Form Alteration Analysis
Discover and map all procedural form alteration hooks:
- **Hook Form Alter Implementations**: `hook_form_alter()`, `hook_form_FORM_ID_alter()`, theme form alters, and module-specific alteration pipelines.
- **Alter Execution Semantics**: Identify target form IDs, added/modified/removed form elements, custom validation/submit injections, `#states` overrides, access restrictions, and hook execution weight ordering.
- **Modern Target Mapping**: Map D7 form alters to modern `hook_form_alter()`, `hook_form_FORM_ID_alter()`, or Symfony Event Subscribers where decoupled alter events are utilized.

### 42. AJAX Behavior, Callbacks & Commands Analysis
Exhaustively analyze Drupal 7 AJAX Form API interactions and command structures:
- **Form `#ajax` Declarations**: `#ajax['callback']`, `#ajax['wrapper']`, `#ajax['method']`, `#ajax['effect']`, `#ajax['event']`, `#ajax['path']`, `#ajax['progress']`.
- **AJAX Delivery & Rendering**: `ajax_render()`, `ajax_deliver()`, `ajax_prepare_response()`, `ajax_process_form()`, partial form rebuilds, wrapper replacement, and custom AJAX response builders.
- **AJAX Command Inventory**: `ajax_command_replace()`, `ajax_command_html()`, `ajax_command_append()`, `ajax_command_prepend()`, `ajax_command_after()`, `ajax_command_before()`, `ajax_command_remove()`, `ajax_command_changed()`, `ajax_command_alert()`, `ajax_command_css()`, `ajax_command_settings()`, `ajax_command_data()`, `ajax_command_invoke()`, `ajax_command_restripe()`, and custom AJAX commands.
- **Modern Target Mapping**: Map D7 AJAX callbacks to modern `AjaxResponse` returning objects implementing `CommandInterface` (`ReplaceCommand`, `HtmlCommand`, `AppendCommand`, `InvokeCommand`, `SettingsCommand`, `MessageCommand`, `RedirectCommand`).

### 43. `$form_state` Lifecycle, Rebuilds & Multistep Flows
Analyze `$form_state` internal state management and multi-step lifecycle:
- **`$form_state` Property Analysis**: `$form_state['values']`, `$form_state['storage']`, `$form_state['rebuild']`, `$form_state['redirect']`, `$form_state['submitted']`, `$form_state['triggering_element']`, `$form_state['clicked_button']`, `$form_state['build_info']`, `$form_state['input']`, `$form_state['cache']`.
- **Multistep & Wizard Flows**: Detect step counters in `$form_state['storage']['step']`, wizard branch logic, back/next/finish button handling, temporary state persistence across rebuilds, and multi-step validation.
- **Modern Target Mapping**: Modernize to `FormStateInterface` methods (`getValue()`, `setValue()`, `getStorage()`, `setStorage()`, `setRebuild()`, `setRedirect()`, `isSubmitted()`, `getTriggeringElement()`).

### 44. Form Security, Access, File Uploads & Confirmation Forms
Audit form security and specialized form types:
- **Form Security & Access**: CSRF token validation (`#token`), permission checks, entity access validation, custom access callbacks (`#access`), input sanitization, output escaping, and open redirect validation (`drupal_redirect_form()`, `drupal_get_destination()`, `drupal_set_message()`). Flag insecure redirect patterns as `HUMAN_DECISION_REQUIRED`.
- **File Upload Forms**: Identify `#type => 'file'`, `#type => 'managed_file'`, `#upload_validators`, destination URI schemes (`public://`, `private://`), permanent file status transitions, and `file_save_upload()` calls $\rightarrow$ modern `managed_file` element and `FileInterface` storage.
- **Confirmation Forms**: Identify `confirm_form()` calls, cancel paths, question prompts, and description texts $\rightarrow$ modern `ConfirmFormBase` classes implementing `getQuestion()`, `getCancelUrl()`, and `getConfirmText()`.

### 45. Forms & AJAX Target Architecture Taxonomy & Migration Strategies
- **Target Architecture Classifications (19 Classes)**: `FORM_BASE`, `CONFIG_FORM_BASE`, `CONFIRM_FORM_BASE`, `ENTITY_FORM`, `CONTENT_ENTITY_FORM`, `CONFIG_ENTITY_FORM`, `PLUGIN_FORM`, `ROUTED_FORM`, `AJAX_FORM`, `AJAX_CALLBACK`, `AJAX_COMMAND`, `FORM_ALTER`, `FORM_VALIDATOR`, `FORM_SUBMIT_HANDLER`, `SERVICE_BACKED_FORM`, `MULTISTEP_FORM`, `FILE_UPLOAD_FORM`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Standardized Migration Strategies (15 Strategies)**: `DIRECT_MODERNIZATION`, `FORM_API_REWRITE`, `FORMBASE_REWRITE`, `CONFIG_FORM_REWRITE`, `ENTITY_FORM_REWRITE`, `AJAX_REWRITE`, `CONTROLLER_PLUS_FORM`, `SERVICE_BACKED_REWRITE`, `MULTISTEP_REWRITE`, `CALLBACK_REFACTOR`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

### 46. Exhaustive Frontend Asset Discovery
Recursively discover all frontend assets across `.js`, `.css`, `.scss`, `.less`, `.info`, `.module`, `.theme`, `.inc`, `.php`, and template files:
- **Direct Asset Files**: Discovers JavaScript files, stylesheets, CSS preprocessor files, vendor libraries, and theme assets.
- **Attachment Mechanisms**: Detects `drupal_add_js()`, `drupal_add_css()`, `drupal_add_library()`, `#attached` render array declarations, preprocess attachment routines (`hook_preprocess_page`, `hook_preprocess_node`), and theme `.info` declarations (`scripts[]`, `stylesheets[]`).
- **Dynamic & Inline Assets**: Detects `drupal_add_js(..., 'inline')`, `drupal_add_css(..., 'inline')`, inline `<script>` tags, inline `<style>` tags, and PHP-generated CSS/JS blocks.

### 47. JavaScript Behaviors, Attach/Detach Lifecycle & `once()` Modernization
Exhaustively parse JavaScript behavior implementations and execution lifecycles:
- **`Drupal.behaviors` Implementations**: Discovers all `Drupal.behaviors.<name>` objects, `attach(context, settings)` methods, `detach(context, settings, trigger)` methods, and context DOM scopes.
- **DOM Ready & Event Handlers**: Detects legacy `$(document).ready()`, `$(function() { ... })`, and unbound event listeners (`click`, `change`, `submit`, `resize`, `scroll`, `keydown`, `keyup`), mapping them to proper `Drupal.behaviors` execution contracts.
- **`once()` Pattern Modernization**: Modernizes legacy `jQuery.once()` (`$(selector, context).once('key')`) and `.once()` plugins to modern `@drupal/once` / `once('key', selector, context)` iterating natively via `forEach()`.

### 48. `Drupal.settings` $\rightarrow$ `drupalSettings` Data Flow Analysis
Trace the lifecycle and transmission of PHP runtime configurations to client-side scripts:
- **PHP Configuration Producers**: Discovers `drupal_add_js(array('myModule' => $data), 'setting')` and `#attached['js'] = array(array('data' => array('myModule' => $data), 'type' => 'setting'))` $\rightarrow$ modern `$attachments['#attached']['drupalSettings']['myModule'] = $data`.
- **Client-Side Consumers**: Maps `Drupal.settings.myModule.key` read access in JavaScript to `drupalSettings.myModule.key` passed via behavior closures. Flag dynamically assembled or opaque settings as `UNVERIFIED`.

### 49. Client-Side AJAX Behavior, Custom Commands & Event Handling
Analyze client-side AJAX interactions and response reactions:
- **`Drupal.ajax` Client Instances**: Discovers `Drupal.ajax`, `Drupal.ajax.instances`, custom submit button bindings, progress indicators (`throbber`, `bar`), and AJAX URL endpoints.
- **Custom AJAX Commands**: Detects custom `Drupal.ajax.prototype.commands.<command_name>` or `Drupal.AjaxCommands.prototype.<command_name>` client-side implementations reacting to server-side `CommandInterface` responses.
- **AJAX Lifecycle Events**: Analyzes event reactions (`ajaxStart`, `ajaxComplete`, `ajaxError`, `ajaxSuccess`) and dynamic behavior reattachment across DOM updates.

### 50. CSS Stylesheets, Media Queries, Preprocess & SMACSS Architecture
Analyze stylesheet rules, selectors, and structural categories:
- **CSS Selectors & SMACSS Categories**: Classifies stylesheet rules into SMACSS categories (`base`, `layout`, `component`, `state`, `theme`) for modern `*.libraries.yml` asset grouping.
- **Responsive & Media Rules**: Analyzes `@media` queries (screen, print, min-width, max-width, orientation) and responsive breakpoint assumptions.
- **Dynamic & Preprocessed CSS**: Detects preprocess CSS alterations (`hook_css_alter()`), stylesheet overrides, and aggregation weight assumptions (`CSS_SYSTEM`, `CSS_DEFAULT`, `CSS_THEME`).

### 51. Asset Attachment Mechanisms, Modern `*.libraries.yml` & Info Declarations
Modernize legacy asset registration into Drupal 10/11 library definitions:
- **Legacy `.info` Declarations**: Converts `scripts[] = js/my_script.js` and `stylesheets[all][] = css/my_style.css` into modern `<module>.libraries.yml` definitions.
- **Modern Library Dependencies**: Explicitly discovers and declares modern core library dependencies (`core/drupal`, `core/drupalSettings`, `core/once`, `core/jquery`, `core/drupal.ajax`).
- **Render Attachment**: Maps `drupal_add_library('system', 'ui.dialog')` to modern `#attached['library'][] = 'core/drupal.dialog'`.

### 52. Frontend Security, Accessibility & Third-Party Library Management
Audit frontend security vulnerabilities, accessibility hooks, and external dependencies:
- **Security & XSS Analysis**: Audits DOM manipulation for unsafe HTML insertion (`.html()`, `innerHTML`, `document.write()`, `eval()`), ensuring `Drupal.checkPlain()` or `Drupal.t()` string placeholder escaping is utilized.
- **Accessibility & Focus Management**: Audits keyboard event bindings (`keydown`, `keypress`), ARIA live regions (`aria-live="polite"`), focus preservation on AJAX updates, and dialog focus trapping.
- **Third-Party & External Assets**: Identifies external CDN scripts, third-party plugin libraries, vendor files, and license compatibilities $\rightarrow$ modern Composer asset management or local library bundling.

### 53. 21 Frontend Target Architecture Taxonomy & Migration Strategies
- **21 Frontend Target Architecture Classifications**: `DRUPAL_LIBRARY`, `JS_BEHAVIOR`, `JS_ONCE_BEHAVIOR`, `AJAX_FRONTEND_BEHAVIOR`, `DRUPAL_SETTINGS_CONSUMER`, `CSS_LIBRARY`, `INLINE_JS`, `INLINE_CSS`, `EXTERNAL_LIBRARY`, `THIRD_PARTY_LIBRARY`, `THEME_LIBRARY`, `MODULE_LIBRARY`, `PREPROCESS_ATTACHMENT`, `RENDER_ARRAY_ATTACHMENT`, `AJAX_ATTACHMENT`, `CUSTOM_AJAX_COMMAND_CLIENT`, `TEMPLATE_SCRIPT`, `TEMPLATE_STYLE`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Standardized Migration Strategies (17 Strategies)**: `LIBRARY_YML_REWRITE`, `BEHAVIOR_REWRITE`, `ONCE_API_REWRITE`, `DRUPAL_SETTINGS_REWRITE`, `AJAX_CLIENT_REWRITE`, `CSS_LIBRARY_REWRITE`, `INLINE_TO_LIBRARY`, `INLINE_TO_BEHAVIOR`, `PREPROCESS_ATTACHMENT_REWRITE`, `THIRD_PARTY_LIBRARY_REPLACEMENT`, `EXTERNAL_ASSET_REVIEW`, `THEME_ASSET_HANDOFF`, `OBSOLETE`, `REPLACED`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

### 54. Exhaustive Views & View Definition Discovery
Recursively discover all Drupal 7 Views and executable configurations:
- **Default Views in Code**: Discovers `hook_views_default_views()` implementations in `*.views_default.inc`, `*.views.inc`, and `*.module` files.
- **Exported View Definitions**: Parses `$view = new view();` builder scripts, display definitions (`$view->new_display(...)`), handler assignments, and display options.
- **Programmatic View Dispatches**: Discovers `views_get_view()`, `views_get_all_views()`, `views_embed_view()`, `views_get_view_result()`, `views_execute_display()`, `views_get_handler()`, and runtime view object mutations across controllers, blocks, and menu callbacks.

### 55. Views Displays & Display Plugin Taxonomy
Categorize every display attached to discovered Views:
- **Display Types**: Page (`page`), Block (`block`), Feed (`feed`), REST Export (`rest_export`), Attachment (`attachment`), Embed (`embed`), and custom display plugins.
- **Display Configurations**: Path/routing, menu item links, administrative titles, access control, contextual filters, exposed filter widgets, pager options, caching configuration, and AJAX enablement.

### 56. Views Handlers & `hook_views_data()` Analysis
Exhaustively inspect handler assignments and schema definitions:
- **Handler Classifications**:
  - Field Handlers (`views_handler_field` $\rightarrow$ `@ViewsField`)
  - Filter Handlers (`views_handler_filter` $\rightarrow$ `@ViewsFilter`)
  - Contextual Filter / Argument Handlers (`views_handler_argument` $\rightarrow$ `@ViewsArgument`)
  - Sort Handlers (`views_handler_sort` $\rightarrow$ `@ViewsSort`)
  - Relationship Handlers (`views_handler_relationship` $\rightarrow$ `@ViewsRelationship`)
  - Area Handlers (`views_handler_area` $\rightarrow$ `@ViewsArea`)
  - Pager Plugins (`views_plugin_pager` $\rightarrow$ `@ViewsPager`)
  - Access Plugins (`views_plugin_access` $\rightarrow$ `@ViewsAccess`)
  - Query Plugins (`views_plugin_query` $\rightarrow$ `@ViewsQuery`)
  - Style Plugins (`views_plugin_style` $\rightarrow$ `@ViewsStyle`)
  - Row Plugins (`views_plugin_row` $\rightarrow$ `@ViewsRow`)
- **`hook_views_data()` & `hook_views_data_alter()`**: Audits table definitions, joins (`left_table`, `left_field`), field definitions, filters, arguments, and custom relationship chains.

### 57. Custom Views Plugins & OOP Class Hierarchy
Audit custom plugin classes and procedural registrations:
- **Plugin Annotations & Class Inheritance**: Traces legacy class extensions (`views_handler_field_custom`, `views_plugin_style_default`) to modern Drupal 10/11 PSR-4 plugin classes under `src/Plugin/views/` annotated with `@ViewsHandler`, `@ViewsPlugin`, or specialized annotations.
- **Service Dependency Injection**: Refactors procedural global calls in plugin methods into `ContainerFactoryPluginInterface::create()` dependency injection.

### 58. Views Query Analysis & Alteration Lifecycle
Audit query construction, custom SQL, and Views execution lifecycle hooks:
- **Query Alterations**: Discovers `hook_views_query_alter()`, analyzing `$query->add_where()`, `$query->add_table()`, `$query->add_field()`, `$query->set_distinct()`, and `$query->add_groupby()`.
- **Execution Lifecycle Hooks**: Discovers `hook_views_pre_view()`, `hook_views_pre_build()`, `hook_views_post_build()`, `hook_views_pre_execute()`, `hook_views_post_execute()`, `hook_views_pre_render()`, and `hook_views_post_render()`.

### 59. Views Access, Caching, Contexts & Security
Audit security, authorization, and cache metadata:
- **Access Control**: Evaluates permission checks, role checks, custom access plugins (`@ViewsAccess`), and contextual filter argument access validations.
- **Cache Metadata & Invalidation**: Maps D7 time-based caching (`views_plugin_cache_time`) to modern cache tags (`node_list`, `user:uid`), cache contexts (`user.roles`, `url.query_args`, `languages`), and cache max-age.

### 60. Views Exposed Forms, AJAX, Frontend & Programmatic Usage
Audit interactive frontend components and programmatic executions:
- **Exposed Forms & AJAX**: Cross-references exposed filter widgets (`#type => select`, `radios`, `bef`) with Step 17 Form API handling and Step 18 client-side AJAX pagination / filtering behavior.
- **Frontend & Templates**: Identifies Views template suggestions (`views-view.html.twig`, `views-view-unformatted.html.twig`, `views-view-fields.html.twig`) and asset attachments (`#attached['library']`).
- **Programmatic Usage Modernization**: Maps `views_get_view($name)` to `\Drupal\views\Views::getView($name)` and `views_embed_view($name, $display_id, ...$args)` to `views_embed_view()`.

### 61. 30 Views Target Architecture Taxonomy & 21 Migration Strategies
- **30 Views Target Architecture Classifications**: `VIEW_CONFIG`, `VIEW_DISPLAY_PAGE`, `VIEW_DISPLAY_BLOCK`, `VIEW_DISPLAY_FEED`, `VIEW_DISPLAY_REST`, `VIEW_DISPLAY_EXPORT`, `VIEW_DISPLAY_ATTACHMENT`, `VIEW_DISPLAY_EMBED`, `VIEW_FIELD_PLUGIN`, `VIEW_FILTER_PLUGIN`, `VIEW_CONTEXTUAL_FILTER_PLUGIN`, `VIEW_SORT_PLUGIN`, `VIEW_RELATIONSHIP_PLUGIN`, `VIEW_AREA_PLUGIN`, `VIEW_PAGER_PLUGIN`, `VIEW_ACCESS_PLUGIN`, `VIEW_QUERY_PLUGIN`, `VIEW_STYLE_PLUGIN`, `VIEW_ROW_PLUGIN`, `VIEW_DISPLAY_PLUGIN`, `VIEW_CACHE_PLUGIN`, `VIEW_EXPOSED_FORM_PLUGIN`, `CUSTOM_VIEWS_PLUGIN`, `VIEWS_DATA_DEFINITION`, `VIEWS_QUERY_ALTER`, `VIEWS_RENDER_ALTER`, `VIEWS_ACCESS_RULE`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Standardized Migration Strategies (21 Strategies)**: `VIEW_CONFIG_REBUILD`, `VIEW_DISPLAY_REBUILD`, `HANDLER_PLUGIN_REWRITE`, `CUSTOM_PLUGIN_REWRITE`, `VIEWS_DATA_REWRITE`, `QUERY_PLUGIN_REWRITE`, `QUERY_ALTER_REWRITE`, `FILTER_REWRITE`, `CONTEXTUAL_FILTER_REWRITE`, `RELATIONSHIP_REWRITE`, `ACCESS_REWRITE`, `CACHE_METADATA_REWRITE`, `EXPOSED_FORM_REWRITE`, `AJAX_VIEW_REWRITE`, `PROGRAMMATIC_VIEW_REWRITE`, `THEME_HANDOFF`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

### 62. Exhaustive Theme, Sub-theme & Metadata Discovery
Recursively discover all Drupal 7 custom and contrib themes without location assumptions:
- **Theme `.info` Declarations**: Scans `*.info` in theme directories, parsing `name`, `description`, `core`, `engine`, `base theme`, `regions`, `stylesheets`, `scripts`, `settings`, and `features`.
- **Theme Source Artifacts**: Scans `template.php`, `theme-settings.php`, `*.tpl.php`, `*.theme`, theme-specific `.inc` files, CSS/SCSS/LESS stylesheets, and JavaScript files.
- **Base Theme & Sub-theme Hierarchy**: Traces parent-child theme inheritance (`base theme = parent_theme`), inherited regions, inherited templates, inherited preprocess functions, and asset override chains.

### 63. PHPTemplate `.tpl.php` to Twig Analysis Heuristics
Analyze every `.tpl.php` template for variables, markup structure, and business logic:
- **Template Types & Core Hooks**: Page (`page.tpl.php`), Region (`region.tpl.php`), Block (`block.tpl.php`), Node (`node.tpl.php`, `node--<type>.tpl.php`), User (`user-profile.tpl.php`), Comment (`comment.tpl.php`), Taxonomy (`taxonomy-term.tpl.php`), Field (`field.tpl.php`, `field--<field_name>.tpl.php`), Views (`views-view.tpl.php`, `views-view-fields.tpl.php`), and custom component templates.
- **Variable Inputs & Render Array Tracing**: Catalogs all variables consumed (`$title`, `$content`, `$classes`, `$attributes`, `$submitted`, `$user_picture`) and render array extractions (`render($content['field_name'])`).
- **PHP Logic Extraction & Decoupling**: Identifies embedded SQL queries, direct entity loading (`node_load()`), global state access (`$user`, `$language`), and procedural API calls $\rightarrow$ flag for extraction to preprocess functions (`.theme`) or custom module services.
- **Markup, Sanitization & Escaping**: Audits PHP print statements (`print $title`, `print render($content)`) for raw HTML output vs `check_plain()` / `filter_xss()`, mapping to Twig auto-escaping or explicit `|raw` / `|t` / `|striptags` filters.

### 64. Theme Functions, `hook_theme()`, Registry & Alterations
Exhaustively discover and analyze procedural theme functions and theme hooks:
- **Theme Functions**: Discovers `theme_<hook_name>()` implementations in `template.php` and custom modules.
- **Theme Registry Implementations**: Discovers `hook_theme()` declarations, auditing registered hooks, variables, render elements, template file references, and path declarations.
- **Theme Registry Alterations**: Discovers `hook_theme_registry_alter()`, tracing modified template paths, overridden preprocess call chains, and changed theme implementations.
- **Modern Mapping Target**: Re-engineers theme functions into modern Twig templates (`templates/`), render elements (`#type`), preprocess functions in `<theme>.theme`, or dedicated theme helper services.

### 65. Preprocess & Process Hook Discovery & Execution Flow
Audit preprocess and process execution chains across themes and custom modules:
- **Preprocess Hooks**: Discovers `hook_preprocess()`, `hook_preprocess_HOOK()`, `template_preprocess_*()`, and theme-specific preprocess implementations (`<theme>_preprocess_*`).
- **Process Hooks**: Discovers legacy `hook_process()` and `hook_process_HOOK()`, refactoring execution into modern D10/D11 `hook_preprocess_HOOK()` implementations in `<theme>.theme`.
- **Variable Mutation Call Graph**: Traces variables added, modified, or removed across the execution sequence:
  $$\text{Module Preprocess} \longrightarrow \text{Base Theme Preprocess} \longrightarrow \text{Sub-theme Preprocess} \longrightarrow \text{Twig Template}$$

### 66. Template Suggestions & Dynamic Suggestion Tracking
Exhaustively discover and catalog template suggestions and naming conventions:
- **D7 Theme Hook Suggestions**: Discovers `$variables['theme_hook_suggestions']` array modifications in preprocess functions.
- **Suggestion Patterns**: Path-based (`page--node--1.tpl.php`), bundle-based (`node--article.tpl.php`), view-mode-based (`node--article--teaser.tpl.php`), user/role-based, and language-based suggestions.
- **Modern Alter Hooks**: Maps legacy `$variables['theme_hook_suggestions']` mutations to modern `hook_theme_suggestions_HOOK_alter()` and `hook_theme_suggestions_HOOK()` implementations.
- **Dynamic Suggestions**: Flags runtime-computed or non-deterministic template suggestions as `[UNVERIFIED RESULT]` or `HUMAN_DECISION_REQUIRED`.

### 67. Theme Regions, Page/Block Rendering & Theme Settings
Audit layout regions, page rendering pipelines, and theme configuration forms:
- **Theme Regions**: Reconciles declared regions in `.info` with regions used in `page.tpl.php` / `page.html.twig`, mapping to modern region structures and empty-region conditions (`{% if page.sidebar_first %}`).
- **Theme Settings**: Discovers `theme_get_setting()`, `theme_settings.php`, and custom theme settings forms, modernizing to typed CMI configuration (`config/install/<theme>.settings.yml`) and schema (`config/schema/<theme>.schema.yml`).

### 68. Markup Sanitization, Escaping, Security, Accessibility & Cache Metadata
Audit presentation security, accessibility compliance, and cache dependencies:
- **Presentation Security & XSS**: Replaces manual `check_plain()` / `htmlspecialchars()` with Twig auto-escaping; audits raw markup filters (`|raw`) to guarantee user input sanitization.
- **Accessibility & ARIA Support**: Verifies semantic HTML5 markup (`<header>`, `<main>`, `<nav>`, `<article>`, `<footer>`), ARIA roles/landmarks (`role="navigation"`, `role="banner"`), form labels/descriptions, and image alt text.
- **Cache Metadata & Bubbling**: Identifies dynamic output dependent on user roles, language, or URL parameters, mapping to modern render array cache tags (`$build['#cache']['tags']`), contexts (`user.roles`, `url.path`), and max-age.

### 69. Cross-Capability Coordination & Step 18 Frontend Boundary
- **Step 18 (Frontend)**: Owns generic JavaScript behaviors, `@drupal/once` patterns, and modular `*.libraries.yml` packaging.
- **Step 20 (Themes)**: Owns theme-specific presentation templates (`templates/**/*.html.twig`), `<theme>.info.yml`, `<theme>.libraries.yml`, `<theme>.theme` preprocess logic, and library attachments (`{{ attach_library('theme/library') }}`).

### 70. 30 Theme Target Architecture Taxonomy & 22 Migration Strategies
- **30 Theme Target Architecture Classifications**: `THEME`, `BASE_THEME`, `SUB_THEME`, `THEME_INFO`, `THEME_REGION`, `TWIG_TEMPLATE`, `TWIG_TEMPLATE_OVERRIDE`, `THEME_HOOK`, `CUSTOM_THEME_HOOK`, `PREPROCESS_HOOK`, `PROCESS_HOOK`, `THEME_SUGGESTION`, `DYNAMIC_THEME_SUGGESTION`, `THEME_FUNCTION_REPLACEMENT`, `RENDER_ARRAY`, `RENDER_ELEMENT`, `THEME_SERVICE`, `THEME_CONFIGURATION`, `THEME_LIBRARY`, `TEMPLATE_VARIABLE_PROVIDER`, `ENTITY_TEMPLATE`, `FIELD_TEMPLATE`, `VIEW_TEMPLATE`, `FORM_TEMPLATE`, `BLOCK_TEMPLATE`, `MENU_TEMPLATE`, `PAGE_TEMPLATE`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Standardized Migration Strategies (22 Strategies)**: `DIRECT_TWIG_MIGRATION`, `TWIG_WITH_PREPROCESS`, `THEME_FUNCTION_TO_TWIG`, `THEME_FUNCTION_TO_RENDER_ARRAY`, `THEME_FUNCTION_TO_SERVICE`, `PREPROCESS_REFACTOR`, `PROCESS_TO_PREPROCESS`, `TEMPLATE_SUGGESTION_REFACTOR`, `DYNAMIC_SUGGESTION_HUMAN_REVIEW`, `REGION_TO_THEME_REGION`, `BASE_THEME_REFACTOR`, `SUB_THEME_MIGRATION`, `THEME_SETTINGS_TO_CONFIG`, `LIBRARY_HANDOFF_TO_STEP18`, `ENTITY_TEMPLATE_REFACTOR`, `FIELD_TEMPLATE_REFACTOR`, `SECURITY_ESCAPING_REFACTOR`, `CACHE_METADATA_REFACTOR`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

### 71. Exhaustive Dynamic Dependency Discovery & Source Pattern Detection (Step 21)
Recursively scan all Drupal 7 source files (`*.module`, `*.inc`, `*.php`, `*.install`, `*.profile`, `*.drush.inc`, `*.info`, templates, themes) to detect dynamic behavior and indirect dependencies:
- **Dynamic Invocations & Callables**:
  - Variable function calls: `$func()`, `$callback($arg1, $arg2)`.
  - Callable arrays: `call_user_func($callable, ...)`, `call_user_func_array($callable, $args)`.
  - Static invocations: `forward_static_call($callback, ...)`, `$class::$method()`.
  - Dynamic object methods: `$object->$method()`, `$object->{$property}()`.
- **Dynamic Instantiation & Class/Service Discovery**:
  - Variable class instantiation: `new $class_name()`, `new $class($args)`.
  - Dynamic service lookups and plugin manager lookups.
- **Dynamic Inclusions & Paths**:
  - Dynamic include/require: `include $path`, `require_once DRUPAL_ROOT . '/' . $dynamic_path`.
  - Concatenated or computed include targets: `module_load_include($type, $module, $dynamic_name)`.
- **Dynamic State, Config & Database Queries**:
  - Dynamic variable keys: `variable_get("my_module_{$type}_setting", $default)`.
  - Dynamic SQL and identifiers: `db_query("SELECT * FROM {" . $dynamic_table . "} WHERE " . $where_clause)`.
- **Opaque & Encoded Payloads**:
  - Serialized data structures (`serialize()`, `unserialize()`), JSON decoding (`drupal_json_decode()`), base64 decoding.
  - Reflection APIs (`new ReflectionClass($name)`, `ReflectionMethod`), generated code, and `eval()` constructs.

### 72. Dynamic Callables, Callbacks & Variable Functions Analysis
Analyze every dynamic callable discovered in the codebase:
- **Attributes Captured**: Source location, callable expression, producer of the callable string/array, execution context, caller hierarchy, and possible target candidate set.
- **Static Resolution Gating**:
  - *Statically Bounded*: If the callable variable is derived from a closed enum, switch statement, or explicit mapping array, resolve statically with high confidence.
  - *Unresolvable Statically*: If the callable string originates from database content, request parameters, or unconstrained user input, mark as `RUNTIME_DEPENDENT` or `UNVERIFIED`.
- **Modern Target Modernization**:
  - Re-engineer variable functions into modern Drupal 10/11 Plugin Types (`PluginManagerInterface`), tagged Symfony services (`@my_module.handler`), or Event Subscribers (`EventSubscriberInterface`).

### 73. Dynamic Class, Service & Plugin Resolution
Trace and account for all runtime class lookups and instantiations:
- **Dynamic Instantiation Patterns**: Detect `new $class_name()`, class registries, CTools plugin discovery arrays, and factory callbacks.
- **Cross-Capability Ownership**: Step 21 owns the *dynamic resolution dependency* and *uncertainty classification*; Step 12 retains ownership of class and OOP definitions.
- **Modern Target Architecture**: Map dynamic class instantiation to the Drupal 10/11 Plugin API (`DefaultPluginManager`, Annotated Class Discovery) or Symfony Service Container factories (`factory: ['@factory_service', 'create']`).

### 74. Dynamic Hook & Event Resolution
Discover and account for dynamically generated hook names and dispatches:
- **Dynamic Invocations Detected**: `module_invoke($dynamic_module, $hook)`, `module_invoke_all($dynamic_hook, ...)`, `drupal_alter("{$dynamic_prefix}_alter", ...)`.
- **Consumer Analysis**: Enumerate all statically discoverable implementations matching pattern `{module}_{dynamic_hook}`. Record any open-ended dispatch patterns as `UNRESOLVED` with probe specifications.
- **Modern Target Architecture**: Map dynamic hooks to Symfony Event Dispatcher dispatches with typed `Event` objects or custom Plugin managers.

### 75. Dynamic Entity, Field & Bundle Resolution
Identify code paths where entity types, bundles, IDs, or field names are computed dynamically at runtime:
- **Dynamic Sources**: Configuration variables, database columns, request parameters (`$_GET`, `arg(2)`), URL route arguments, or serialized settings.
- **Cross-Capability Ownership**: Step 21 owns the *dynamic dependency edge*; Step 16 retains ownership of entity schemas, field storage, and bundle definitions.
- **Modern Target Architecture**: Modernize to typed `EntityTypeManagerInterface::getStorage($dynamic_type)` with explicit entity type validation constraints and parameter upcasting (`ParamConverterInterface`).

### 76. Dynamic Template, View, Form & Frontend Resolution
Trace dynamic references across presentation, Views, forms, and frontend layers:
- **Dynamic Templates & Suggestions**: `theme($dynamic_hook, $variables)`, dynamically appended `$variables['theme_hook_suggestions'][]` (Step 20 Handoff).
- **Dynamic Views & Displays**: `views_get_view($dynamic_view_id)`, dynamic display IDs (Step 19 Handoff).
- **Dynamic Forms & AJAX**: `drupal_get_form($dynamic_form_id)`, dynamically generated AJAX callback functions (Step 17 Handoff).
- **Dynamic Frontend Assets**: Dynamically constructed JS setting namespaces, dynamic library names in `drupal_add_library()` (Step 18 Handoff).
- **Uncertainty Classification**: Every dynamic presentation or UI edge is explicitly cataloged with confidence scoring and fallback behavior.

### 77. Dynamic Include, File, Config, State & Database/SQL Resolution
Discover and account for runtime file paths, variable keys, and query fragments:
- **Dynamic Includes**: `module_load_include($type, $module, $dynamic_name)` $\rightarrow$ modernized to PSR-4 autoloading or explicit file discovery services (Step 11 Handoff).
- **Dynamic Configuration & State Keys**: `variable_get("my_module_{$bundle}_enabled")` $\rightarrow$ classified into typed CMI configuration collections or State API key/value storage (Step 15 Handoff).
- **Dynamic Database & SQL**: Dynamic table names, concatenated WHERE clauses $\rightarrow$ modernized to `\Drupal::database()->select()` with dynamic conditions (`ConditionInterface`) or entity queries (Step 13 Handoff).

### 78. Serialized, JSON, Data-Driven, Environment & Reflection/Eval Analysis
Exhaustively analyze opaque payloads, environment couplings, and runtime execution constructs:
- **Serialized & JSON Payloads**: Recursively inspect serialized strings and JSON blobs for embedded class names, callback references, entity IDs, or configuration arrays. Flag unparseable payloads as `HUMAN_DECISION_REQUIRED`.
- **Data-Driven & Environment Couplings**: Detect code behavior branching on database rows, user roles, environment variables (`getenv()`, `$_ENV`, `$_SERVER`), or deployment settings.
- **Reflection & `eval()`**: Detect PHP `ReflectionClass`, `ReflectionMethod`, `eval()`, `create_function()`, and dynamic code generators. Flag all instances as elevated risk requiring architectural decisions.

### 79. Runtime Resolution Model, Confidence Taxonomy & Probes
Apply an explicit, deterministic resolution model to every discovered dynamic dependency:
- **6 Resolution Confidence Levels**:
  1. `RESOLVED_STATICALLY`: Statically proven constant/literal value with 100% certainty.
  2. `RESOLVED_WITH_HIGH_CONFIDENCE`: Deterministically bounded candidate set (e.g., closed switch/enum).
  3. `PARTIALLY_RESOLVED`: Statically bounded candidate set requiring runtime confirmation.
  4. `RUNTIME_DEPENDENT`: Requires runtime inspection (CMI/State/DB probe) to resolve actual value.
  5. `UNRESOLVED`: Open-ended dynamic expression without static bounds.
  6. `OPAQUE`: Encrypted, binary, or unparseable reflection/`eval()` construct.
- **Deterministic Runtime Probe Model**:
  - For items requiring runtime confirmation, specify safe, non-destructive, read-only probe specifications (`CALLABLE_RESOLUTION`, `PLUGIN_RESOLUTION`, `SERVICE_RESOLUTION`, `TEMPLATE_RESOLUTION`, `FORM_RESOLUTION`, `VIEW_RESOLUTION`, `CONFIG_DISCOVERY`, `FILE_DISCOVERY`, `ENTITY_RESOLUTION`, `DATABASE_RESOLUTION`).
  - When runtime CLI/environment is unavailable, mark verification status as `[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]` without guessing.

### 80. 35 Dynamic Target Architecture Taxonomy & 19 Migration Strategies
- **35 Dynamic Target Architecture Classifications**: `DYNAMIC_CALLABLE`, `DYNAMIC_FUNCTION`, `DYNAMIC_METHOD`, `DYNAMIC_CLASS`, `DYNAMIC_SERVICE`, `DYNAMIC_PLUGIN`, `DYNAMIC_HOOK`, `DYNAMIC_EVENT`, `DYNAMIC_ENTITY`, `DYNAMIC_BUNDLE`, `DYNAMIC_FIELD`, `DYNAMIC_TEMPLATE`, `DYNAMIC_THEME`, `DYNAMIC_VIEW`, `DYNAMIC_FORM`, `DYNAMIC_AJAX`, `DYNAMIC_LIBRARY`, `DYNAMIC_FILE`, `DYNAMIC_INCLUDE`, `DYNAMIC_CONFIGURATION`, `DYNAMIC_STATE`, `DYNAMIC_VARIABLE`, `DYNAMIC_DATABASE`, `DYNAMIC_SQL`, `SERIALIZED_DEPENDENCY`, `JSON_DEPENDENCY`, `ENVIRONMENT_DEPENDENCY`, `DATA_DRIVEN_DEPENDENCY`, `REFLECTION_DEPENDENCY`, `GENERATED_CODE`, `EVAL_DEPENDENCY`, `RUNTIME_PROBE`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **19 Standardized Dynamic Migration Strategies**: `STATIC_RESOLUTION`, `PARTIAL_STATIC_RESOLUTION`, `RUNTIME_DISCOVERY_REQUIRED`, `TEST_DRIVEN_RESOLUTION`, `DATA_FIXTURE_RESOLUTION`, `CONFIGURATION_MAPPING`, `SERVICE_CONTAINER_MAPPING`, `PLUGIN_MANAGER_MAPPING`, `EVENT_DISPATCHER_MAPPING`, `ENTITY_API_MAPPING`, `TEMPLATE_MAPPING`, `VIEW_MAPPING`, `FORM_MAPPING`, `FILE_DISCOVERY_MAPPING`, `DATABASE_REFACTOR`, `SERIALIZED_DATA_MIGRATION`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`, `OBSOLETE`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

---

## External Integrations, APIs, Web Services & Third-Party Systems Analysis (Step 22)

### 81. Exhaustive Generic External Integration Discovery
Recursively scan all D7 custom modules, `.module`, `.inc`, `.install`, `.php`, `.drush.inc`, `.info`, and Composer metadata for external system integrations:
- **HTTP Client Mechanisms**: `drupal_http_request()`, `curl_init()`, `curl_exec()`, `file_get_contents()` with HTTP URLs, PHP stream wrappers (`stream_context_create()`), socket connections (`fsockopen()`), Guzzle wrappers.
- **Protocol & API Patterns**: REST, SOAP (`SoapClient`), XML-RPC (`xmlrpc()`), JSON-RPC, GraphQL, custom TCP/IP sockets, SFTP/FTP stream wrappers (`ssh2_sftp()`, `ftp_connect()`), external databases (`Database::getConnection('external')`), external CLI binaries (`exec()`, `shell_exec()`, `proc_open()`).
- **Discovery Independence**: Never assume integrations reside in specific directories. Extract endpoint URLs, hostnames, protocols, HTTP methods, headers, and authentication logic directly from source evidence.

### 82. Outbound HTTP/API Discovery & Inbound Webhook/Endpoint Resolution
Analyze both egress and ingress communication channels:
- **Outbound HTTP / API Calls**: Catalog destination URL, HTTP verb (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), payload format (JSON, XML, Form-URLencoded, Multipart), timeout settings, headers, query parameters, and caller functions.
- **Inbound Endpoints & Webhooks**: Discover custom API routes in `hook_menu()` exposing REST/JSON/XML endpoints, webhook listener callbacks, payment IPN handlers, and OAuth callback endpoints. Extract authorization mechanisms, CSRF protection, signature verification, and input sanitation.

### 83. Authentication, Authorization & Secret Protection (Rule 10)
Exhaustively identify authentication mechanisms and enforce strict secret protection:
- **Authentication Schemes**: API Keys, Basic Auth, Bearer Tokens, OAuth 1.0a / OAuth 2.0 (Authorization Code, Client Credentials, Refresh Tokens), HMAC Request Signing, Client TLS/SSL Certificates, LDAP Bind, SAML 2.0 / OpenID Connect.
- **Secret Protection Standards (Rule 10)**:
  - **Zero Secrets in Manifests/Reports/CMI**: Never copy, persist, or commit real API keys, passwords, bearer tokens, private certificates, or client secrets.
  - **Abstract Credential Sources**: Classify secret locations as `CONFIGURATION_SECRET`, `ENVIRONMENT_SECRET`, `RUNTIME_SECRET`, `KEY_MODULE`, `SETTINGS_PHP`, or `HARDCODED_IN_SOURCE`.
  - Flag any hardcoded secret found in source code as a critical security vulnerability requiring immediate extraction to environment variables or the Drupal Key module (`key` module integration).

### 84. Data Flow Analysis, Transformations & Sensitive Data Classification
Trace the end-to-end data pipeline for every integration:
- **Lineage**:
  $$\text{Data Source (Entity / Form / DB / Session)} \longrightarrow \text{Transformation} \longrightarrow \text{Outbound Payload} \longrightarrow \text{External System} \longrightarrow \text{Response} \longrightarrow \text{Response Parsing} \longrightarrow \text{Destination}$$
- **Sensitive Data Categorization**: Classify payload elements into sensitivity categories (`NONE`, `USER_IDENTIFIERS`, `PERSONAL_INFO`, `PAYMENT_DATA`, `CREDENTIALS`, `HEALTH_DATA`, `BUSINESS_CONFIDENTIAL`) without storing actual values.
- **Transformations**: Document mapping arrays, field normalization, currency/date conversions, and schema translations.

### 85. Payment, Email, SMS & Notification Integrations
Account for specialized external service providers:
- **Payment Gateways**: Discover payment API calls, authorization/capture requests, refund endpoints, checkout form integrations, webhook/IPN verification, and transaction status persistence. Modernize to Drupal Commerce Payment Gateway plugins (`@CommercePaymentGateway`) or custom gateway services.
- **Email, SMS & Push Notifications**: Trace custom mail handlers delegating to external transactional email APIs (SendGrid, Mailgun, AWS SES), SMS APIs (Twilio), or mobile push notification gateways. Modernize to Symfony Mailer plugins or dedicated notification services.

### 86. Storage, File Transfer (SFTP), External Databases & Queues
Catalog non-HTTP external connections:
- **Remote Filesystems & SFTP/FTP**: Discover automated file transfers, remote asset synchronization, cloud/object storage integrations (AWS S3, Google Cloud Storage, Azure Blob). Modernize to Drupal 10/11 Flysystem stream wrappers (`@FlysystemStreamWrapper`).
- **External Databases**: Identify connections to secondary/external database instances (`$databases['external']`). Modernize to Drupal Database API service connections or custom repository services with Step 13 coordination.
- **Message Brokers & Queues**: Detect integrations with RabbitMQ, Kafka, AWS SQS, or Redis queues. Modernize to Drupal Queue API (`@QueueWorker`) or Symfony Messenger handlers.

### 87. Third-Party SDKs, Composer Packages & External CLI Binaries
Audit external code libraries and system command execution:
- **Third-Party PHP Libraries & SDKs**: Identify vendor SDKs included manually or via Composer. Verify D10/D11 compatibility, PHP 8.1–8.3 support, and PSR-4 modernization requirements.
- **External CLI Binaries**: Detect `exec()`, `shell_exec()`, `system()`, `passthru()`, `proc_open()`, and `popen()`. Audit for command injection risks, sanitize arguments via `escapeshellarg()`, and modernize to Symfony `Process` component.

### 88. Retry, Timeout, Idempotency, Error & Failure Behavior
Inspect resilience and error handling semantics:
- **Resilience Characteristics**:
  - `timeout`: Explicit network timeout in seconds (flag missing timeouts as reliability risks).
  - `retry_behavior`: `NONE`, `FIXED_RETRY`, `EXPONENTIAL_BACKOFF`, `QUEUE_RETRY`, `DEAD_LETTER`.
  - `idempotency_behavior`: `NONE`, `IDEMPOTENCY_KEY_HEADER`, `TRANSACTION_TOKEN`, `DATABASE_LOCK`.
- **Failure Semantics**: Analyze HTTP status code parsing, exception catching, fallback data providers, admin alerts, queue retries, and masked audit logging.

### 89. Cross-Capability Coordination & Dynamic/Security/Runtime Handoffs
Ensure clean architectural boundaries across the migration factory:
- **Step 13 (Database)**: External database connections and data mapping.
- **Step 15 (Configuration)**: API endpoint URLs, timeouts, and non-sensitive options migrated to CMI (`config/schema/*.schema.yml`).
- **Step 17 (Forms & AJAX)**: Form submit triggers, AJAX callback responses, and checkout handlers.
- **Step 18 (Frontend)**: Client-side tracking scripts, analytics libraries, and third-party widgets.
- **Step 21 (Dynamic Resolution)**: Dynamically computed endpoint URLs, variable API versions, and runtime plugin lookups.
- **Step 23 (Security & Runtime)**: Transport security (TLS 1.2+), webhook HMAC validation, session storage, and cache tags.

### 90. 35 Integration Target Architecture Taxonomy & 20 Migration Strategies
- **35 Integration Target Architecture Classifications**:
  `EXTERNAL_HTTP_CLIENT`, `REST_CLIENT`, `SOAP_CLIENT`, `XMLRPC_CLIENT`, `WEBHOOK_RECEIVER`, `WEBHOOK_SENDER`, `API_ENDPOINT`, `OAUTH_INTEGRATION`, `TOKEN_AUTH_INTEGRATION`, `API_KEY_INTEGRATION`, `SIGNED_REQUEST_INTEGRATION`, `EXTERNAL_AUTHENTICATION`, `LDAP_INTEGRATION`, `SSO_INTEGRATION`, `PAYMENT_INTEGRATION`, `EMAIL_INTEGRATION`, `SMS_INTEGRATION`, `NOTIFICATION_INTEGRATION`, `EXTERNAL_STORAGE`, `FILE_TRANSFER`, `EXTERNAL_DATABASE`, `QUEUE_INTEGRATION`, `THIRD_PARTY_SDK`, `EXTERNAL_BINARY`, `ANALYTICS_INTEGRATION`, `SEARCH_INTEGRATION`, `CRM_INTEGRATION`, `ERP_INTEGRATION`, `CDN_INTEGRATION`, `CONFIG_DRIVEN_INTEGRATION`, `DYNAMIC_INTEGRATION`, `RUNTIME_ONLY_INTEGRATION`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **20 Standardized Integration Migration Strategies**:
  `DIRECT_HTTP_CLIENT_MIGRATION`, `GATEWAY_SERVICE_MIGRATION`, `SERVICE_CONTAINER_INTEGRATION`, `REST_CLIENT_REFACTOR`, `WEBHOOK_CONTROLLER_MIGRATION`, `OAUTH_SERVICE_MIGRATION`, `AUTHENTICATION_REFACTOR`, `PAYMENT_INTEGRATION_REFACTOR`, `EMAIL_SERVICE_MIGRATION`, `STORAGE_ADAPTER_MIGRATION`, `EXTERNAL_DATABASE_REFACTOR`, `QUEUE_WORKER_MIGRATION`, `THIRD_PARTY_LIBRARY_REPLACEMENT`, `EXTERNAL_BINARY_REFACTOR`, `CONFIGURATION_DRIVEN_PROVIDER`, `DYNAMIC_PROVIDER_RESOLUTION`, `RUNTIME_VERIFICATION_REQUIRED`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`, `OBSOLETE`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

---

## Cache, Session, Security, Concurrency & Runtime Behavior Analysis (Step 23)

### 91. Exhaustive Cache API Discovery, Cache Bins, Keys & Semantics
Recursively scan custom D7 modules and themes for all caching operations:
- **Cache API Calls**: `cache_get()`, `cache_set()`, `cache_clear_all()`, `cache_flush()`, `drupal_static()`, `drupal_static_reset()`, static variable caches (`static $cache = array()`), static cache to service modernizations, persistent caches, and custom cache backend implementations.
- **Cache Bins**: Inventory standard core cache bins (`cache`, `cache_page`, `cache_block`, `cache_menu`, `cache_form`, `cache_views`, `cache_filter`) and custom cache bins/tables declared in `hook_schema()`.
- **Render Cache & Page Cache**: Analyze render cache (`#cache` render arrays), render caching, page cache, page caching, block cache, and Views cache behaviors.
- **Cache Key & Granularity Analysis**: Extract cache keys, key construction logic (e.g., concatenated entity IDs, user roles, language codes, timestamps), cache bin targets, and lifetime/expiration settings (`CACHE_PERMANENT`, `CACHE_TEMPORARY`, unix timestamps). Dynamic cache keys cross-reference Step 21.
- **Context Dependencies**: Analyze if cached values depend on user (`user.roles`, `user.permissions`, `user`), language (`languages:language_interface`), timezone, route/path (`url.path`, `url.query_args`), or HTTP headers.

### 92. Cache Invalidation, Tags, Contexts & Max-Age Modeling
Analyze cache clearing and invalidation mechanics to construct modern cache metadata:
- **Invalidation Calls & Triggers**: Detect `cache_clear_all('prefix', 'bin', TRUE)`, `cache_clear_all('key', 'bin')`, `drupal_static_reset()`, `hook_cache_flush()`, entity hook invalidations (`hook_entity_update`, `hook_node_save`), and configuration-driven invalidations. Map to modern `Cache::invalidateTags()` and `CacheableMetadata`.
- **Modern Cache Metadata Construction**:
  - **Cache Tags (`#cache['tags']`)**: Map entity and data invalidations to granular tags (e.g., `node:123`, `node_list`, `user:45`, `config:system.site`).
  - **Cache Contexts (`#cache['contexts']`)**: Map request-sensitive variations to standard D10/D11 contexts (e.g., `user.roles`, `url.query_args:page`, `languages:language_interface`).
  - **Cache Max-Age (`#cache['max-age']`)**: Map fixed expirations to seconds or `Cache::PERMANENT` / `0` (un-cacheable).

### 93. Session Lifecycle, Session Variables & Anonymous/Authenticated State
Discover all session interactions across custom code:
- **Session API & `$_SESSION` Usage**: Identify `$_SESSION` reads, writes, and unsets, session initialization triggers, and session destruction hooks (`hook_user_logout()`, `drupal_session_destroy_timestamp()`).
- **Session-Dependent Rendering & Logic**: Track logic where rendered output or access decisions depend on session variables (e.g., wizard forms, temporary shopping carts, session flash messages).
- **Anonymous vs Authenticated Sessions**: Distinguish lazy anonymous sessions from authenticated sessions, ensuring migration to `\Symfony\Component\HttpFoundation\Session\SessionInterface` or Drupal `tempstore.private` / `tempstore.shared` without forcing session initiation for anonymous users.
- **Secret Isolation**: Never copy or persist actual session IDs or token values in manifests or reports.

### 94. Cookie Discovery, Temporary Storage & Request State
Catalog cookie manipulation and temporary runtime state:
- **Cookie Usage**: Detect `setcookie()`, `$_COOKIE` reads, and cookie deletion. Document purpose (e.g., UI preferences, affiliate tracking, auth tokens) and security flags (`HttpOnly`, `Secure`, `SameSite`).
- **Temporary State Stores**: Identify custom database temporary tables, serialized scratch buffers, and `ctools_object_cache` usage. Map to modern PrivateTempStore (`tempstore.private`) or KeyValueExpirable stores (`keyvalue.expirable`).

### 95. Access Control, Permissions, Node/Entity/Field Access & Route Access
Exhaustively analyze security and authorization decision points:
- **Routing Access Callbacks**: Detect `access callback` and `access arguments` in `hook_menu()`, custom access functions, and parameter requirements. Map to modern route requirement attributes (`_permission`, `_role`, `_access: 'Drupal\my_module\Access\CustomAccessCheck::access'`).
- **Permission Checks**: Trace `user_access()`, role checks (`in_array('administrator', $user->roles)`), and custom permission declarations in `hook_permission()`. Map to `PermissionInterface` and `permissions.yml`.
- **Entity & Node Access**: Identify `hook_node_access()`, `hook_node_grants()`, `hook_node_access_records()`, and `hook_entity_access()`. Modernize to Entity Access Control Handlers (`@EntityAccessControlHandler` / `AccessResult`).
- **Field Access**: Detect `hook_field_access()`. Modernize to `hook_entity_field_access()`.

### 96. CSRF, XSS, Input Validation, Output Escaping & File/URL Security
Audit input validation, output sanitization, and request security:
- **CSRF Token Validation**: Detect `drupal_get_token()`, `drupal_valid_token()`, Form API `#token`, and custom route token requirements (`_csrf_token: 'TRUE'`).
- **XSS & Output Escaping**: Trace `check_plain()`, `filter_xss()`, `filter_xss_admin()`, `check_url()`, and raw HTML outputs. Modernize to Twig auto-escaping, `Html::escape()`, `Xss::filter()`, and `UrlHelper::filterBadProtocol()`.
- **File & Upload Security**: Discover file upload validation hooks, extension restrictions (`file_validate_extensions`), MIME verification, and public vs private URI schemes (`public://`, `private://`).
- **URL & Redirect Security**: Audit `drupal_goto()`, `url()`, and external redirects for Open Redirect vulnerabilities. Modernize to `TrustedRedirectResponse` and `Url::fromUserInput()`.

### 97. Request Lifecycle, Bootstrap, Shutdown & Cron/Queue/Batch Runtime
Trace lifecycle hooks and execution context constraints:
- **Lifecycle Hooks**: Detect `hook_boot()`, `hook_init()`, `hook_exit()`, and `drupal_register_shutdown_function()`. Modernize to Symfony HttpKernel Event Subscribers (`kernel.request`, `kernel.response`, `kernel.terminate`).
- **Cron, Queue & Batch Processing**: Identify `hook_cron()`, `hook_cron_queue_info()`, `batch_set()`, and batch operation callbacks. Modernize to `@QueueWorker` plugins and modern Batch API controllers.
- **Execution Contexts**: Distinguish CLI execution (`drupal_is_cli()`, Drush command context) from Web requests (`\Drupal::request()`).

### 98. Concurrency, Locking, Transactions & Environment/Runtime Dependencies
Analyze concurrency controls and runtime platform requirements:
- **Lock API**: Detect `lock_acquire()`, `lock_wait()`, `lock_release()`. Modernize to `\Drupal\Core\Lock\LockBackendInterface` (`lock` service).
- **Database Transactions**: Detect `db_transaction()`, transaction rollbacks, and nested transactions. Modernize to `$connection->startTransaction()` with RAII scoping.
- **Environment Dependencies**: Catalog dependencies on PHP extensions (e.g., `ext-curl`, `ext-gd`, `ext-soap`), PHP version constraints, memory limits (`ini_set('memory_limit')`), time limits (`set_time_limit()`), and OS CLI tools (`exec`, `shell_exec`).

### 99. Static/Global State, Runtime Registries & Error/Fallback Behavior
Catalog runtime state containers and error resilience:
- **Global & Static State**: Detect `$GLOBALS`, `$user`, `$language`, global registries, and procedural singletons. Modernize to Dependency Injection and Container services.
- **Error & Exception Handling**: Identify `set_error_handler()`, `try/catch` blocks, custom exception classes, and fallback data providers. Modernize to typed PHP 8.1+ exceptions and Symfony Error Handler event listeners.

### 100. 40 Runtime Target Architecture Taxonomy & 25 Migration Strategies
- **40 Runtime Target Architecture Classifications**:
  `CACHE_METADATA`, `CACHE_CONTEXT`, `CACHE_TAG`, `CACHE_MAX_AGE`, `CACHE_BIN`,
  `RENDER_CACHE`, `STATIC_CACHE`, `PERSISTENT_CACHE`, `CACHE_INVALIDATION`,
  `SESSION_BEHAVIOR`, `SESSION_SERVICE`, `COOKIE_BEHAVIOR`, `TEMPORARY_STATE`,
  `RUNTIME_STATE`, `ACCESS_CHECK`, `ACCESS_CHECKER_SERVICE`, `PERMISSION_CHECK`,
  `ENTITY_ACCESS`, `FIELD_ACCESS`, `CSRF_PROTECTION`, `INPUT_VALIDATION`,
  `OUTPUT_ESCAPING`, `FILE_SECURITY`, `URL_SECURITY`, `WEBHOOK_SECURITY`,
  `REQUEST_LIFECYCLE`, `EVENT_SUBSCRIBER_LIFECYCLE`, `CRON_RUNTIME`, `QUEUE_RUNTIME`,
  `BATCH_RUNTIME`, `LOCKING`, `TRANSACTION`, `CONCURRENCY_CONTROL`,
  `ENVIRONMENT_DEPENDENCY`, `TIME_DEPENDENCY`, `LOCALE_DEPENDENCY`, `USER_CONTEXT_DEPENDENCY`,
  `RUNTIME_REGISTRY`, `ERROR_HANDLER`, `FALLBACK_BEHAVIOR`,
  `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **25 Standardized Runtime Migration Strategies**:
  `CACHE_METADATA_REFACTOR`, `CACHE_CONTEXT_MAPPING`, `CACHE_TAG_MAPPING`,
  `CACHE_INVALIDATION_REFACTOR`, `STATIC_CACHE_TO_SERVICE`, `SESSION_SERVICE_MIGRATION`,
  `COOKIE_BEHAVIOR_MIGRATION`, `TEMPORARY_STORE_MIGRATION`, `ACCESS_CHECK_MIGRATION`,
  `PERMISSION_MIGRATION`, `ENTITY_ACCESS_REFACTOR`, `FIELD_ACCESS_REFACTOR`,
  `CSRF_PROTECTION_MIGRATION`, `INPUT_VALIDATION_REFACTOR`, `OUTPUT_ESCAPING_REFACTOR`,
  `SECURITY_API_REFACTOR`, `REQUEST_LIFECYCLE_REFACTOR`, `CRON_MIGRATION`,
  `QUEUE_WORKER_MIGRATION`, `BATCH_MIGRATION`, `LOCK_API_MIGRATION`,
  `TRANSACTION_REFACTOR`, `CONCURRENCY_REFACTOR`, `ENVIRONMENT_DEPENDENCY_MAPPING`,
  `RUNTIME_SERVICE_MIGRATION`, `ERROR_HANDLER_REFACTOR`, `FALLBACK_BEHAVIOR_PRESERVATION`,
  `RUNTIME_VERIFICATION_REQUIRED`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`, `OBSOLETE`.
- **Approved Terminal Outcomes**: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Forbidden Terminal States**: `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, `SILENTLY_OMITTED`.

### 101. Cross-Capability Ownership & Inter-Step Boundaries (Step 23)
Step 23 establishes explicit boundaries with prior capabilities:
- **Step 11 (.inc Files)**: Inclusion hierarchies and legacy procedural files.
- **Step 12 (OOP PHP Classes)**: Class structures, constructors, and PSR-4 mapping.
- **Step 13 (Database & Schema)**: Schema definitions, table taxonomy, and queries.
- **Step 14 (Hooks)**: Procedural hook cataloging and lifecycle dispatch.
- **Step 15 (Configuration & State)**: Persistent variables, CMI schemas, and State API items.
- **Step 16 (Entities & Fields)**: Entity types, bundles, field storage, revisions, and translations.
- **Step 17 (Forms & AJAX)**: Form builder functions, validation, submit handlers, and AJAX commands.
- **Step 18 (Frontend Assets)**: JavaScript behaviors, `once()`, libraries, and CSS.
- **Step 19 (Views & Plugins)**: Views default definitions, displays, and custom handler plugins.
- **Step 20 (Themes & Templates)**: PHPTemplate conversion, Twig templates, and preprocess hooks.
- **Step 21 (Dynamic Dependencies)**: Dynamic callables, variable plugin IDs, reflection probes, and uncertainty resolution.
- **Step 22 (External Integrations)**: External HTTP clients, endpoints, webhooks, authentication protocols, and third-party SDKs.
- **Step 23 (Runtime & Security)**: Runtime behavior, cache/session semantics, security-sensitive runtime behavior, lifecycle behavior, concurrency, environment/runtime dependencies, and runtime verification requirements.

### 102. External Drupal-Integrated PHP Code Discovery & Evidence Filtering Protocol (Step 24)
When discovering PHP source files residing outside standard `modules/` and `themes/` directories (e.g. standalone scripts, integration scripts, CLI tools, custom endpoints, cron/worker runners, bootstrap scripts, external library folders):

1. **Multi-Vector Evidence Engine & Assessment**:
   Never classify an external PHP file as migration-relevant based solely on file location or name. Require concrete repository evidence:
   - *Drupal Bootstrap Evidence*: `DRUPAL_ROOT`, `drupal_bootstrap()`, `includes/bootstrap.inc`, `$user`, `node_load()`, `user_load()`, `taxonomy_*`, `variable_get()`, `variable_set()`, `module_invoke()`, `watchdog()`, `drupal_set_message()`, etc.
   - *Drupal Database Evidence*: Queries targeting core tables (`{node}`, `{users}`, `{variable}`) or custom Drupal module tables with table prefix `{...}` syntax.
   - *Drupal Module Coupling Evidence*: Invocations of custom or contrib module functions, classes, hooks, or service wrappers.
   - *Runtime Entry Point Evidence*: HTTP endpoints bootstrapping Drupal, CLI scripts, scheduled cron runners, QueueWorker dispatchers, webhooks, or callbacks referenced by Drupal code/config.
   - *Deployment/Configuration References*: References in `.htaccess`, crontab configurations, or Drush alias files.

2. **Confidence Scoring & Standard Functional Role Classification**:
   Assign deterministic confidence levels (`HIGH`, `MEDIUM`, `LOW`) and classify functional roles:
   - `CLI_SCRIPT`: Standalone command-line or maintenance script.
   - `WEBHOOK_ENDPOINT`: Standalone HTTP receiver or webhook script.
   - `STANDALONE_GATEWAY`: Standalone API wrapper or payment gateway client.
   - `CRON_WORKER`: Standalone cron runner or batch background worker.
   - `SHARED_UTILITY`: Shared domain library used across Drupal and external applications.
   - `OBSOLETE_SCRIPT`: Dead or superseded standalone script with zero active callers.

3. **Classification & Relevance Taxonomy**:
   - `MIGRATION_RELEVANT`: Direct Drupal coupling discovered; artifact contains behavior requiring migration into modern D10/D11 architecture.
   - `DRUPAL_INDEPENDENT` (`EXCLUDED`): Standalone utility or external library with zero Drupal coupling; excluded from migration with documented rationale.
   - `SHARED`: Shared domain library or API client consumed by both Drupal and external non-Drupal systems; evaluate whether to migrate Drupal-facing interface or retain as external dependency.
   - `OBSOLETE`: Dead code or deprecated test script with verified zero active callers across codebase, crontab, and configuration.
   - `SUPERSEDED` / `REPLACED`: Subsystem or script replaced by modern platform or core capabilities (e.g. standalone cron script $\to$ Drupal QueueWorker).
   - `HUMAN_INTERVENTION_REQUIRED`: Ambiguous coupling, unverified external dependencies, or unclear architecture.

4. **Multi-Behavior Decomposition per External Artifact**:
   A single external file may host multiple distinct behaviors (e.g. auth check, user lookup, external sync, logging). Apply Behavior Unit Decomposition to decompose the artifact into discrete behavior units so each receives its own canonical status (`COMPLETE`, `PARTIAL`, `MISSING`, `REPLACED`, `SUPERSEDED`, `OBSOLETE`, `HUMAN_INTERVENTION_REQUIRED`, `RUNTIME_UNVERIFIED`).

5. **Obsolete Code Verification Protocol**:
   Before classifying any standalone external code as `OBSOLETE`, verify across multiple evidence sources (code callers, crontab, webserver configs, deployment configs). If dead-code status cannot be conclusively established from evidence, mark as `UNVERIFIED` / `HUMAN_INTERVENTION_REQUIRED`.

6. **Secret & Credential Redaction Protocol (Rule 10)**:
   Detect and redact API keys, tokens, passwords, and connection strings in external scripts (`[REDACTED]`). Never copy raw secrets into discovery manifests, reports, or generated target code. Preserves strict D7 Read-Only Source Protection.

---

## Output Reporting Standard
All discovery outputs must:
1. Provide verifiable file paths, class names, method signatures, table names, hook names, config keys, entity types, field names, form IDs, JavaScript behavior names, library identifiers, view IDs, display IDs, plugin IDs, theme names, template names, dynamic expressions, probe targets, external endpoints, runtime behavior IDs, and external Drupal code paths (`[OBSERVED FACT]`).
2. Populate `custom_php_files`, `inc_files`, `custom_database_tables`, `hook_implementations`, `configuration_state_items`, `entities_fields_items`, `forms_ajax_items`, `frontend_assets_items`, `views_plugins_items`, `theme_items`, `dynamic_dependency_items`, `external_integrations_items`, `runtime_behavior_items`, and `external_code_items` in `state/migration-manifest.yml`.
3. Flag any dynamic or unresolvable include / reflection / dynamic instantiation / dynamic SQL / dynamic hook call / dynamic config key / dynamic entity type / dynamic form ID / dynamic callback / dynamic JS setting / dynamic View ID / dynamic template suggestion / dynamic callable / external endpoint / runtime behavior / ambiguous external code as `[UNVERIFIED RESULT]` or `HUMAN_DECISION_REQUIRED`.
