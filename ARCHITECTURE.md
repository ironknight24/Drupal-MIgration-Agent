# System Architecture: Drupal Migration Agent Framework

## 1. Overview & Architectural Philosophy

The **Drupal Migration Agent Framework** (`drupal-migration-agent`) is a reusable, AI-assisted multi-agent system designed to orchestrate the replatforming of legacy Drupal 7 codebases to modern Drupal 10 and Drupal 11 architectures.

The architecture decouples **workflow coordination** (Agents) from **reusable domain playbooks** (Skills) and **factual technical truth** (References), driven by a single source of truth for runtime state (`migration-state.yml`) and an itemized scope manifest (`migration-manifest.yml`).

---

## 2. Execution Architecture & Coordination Topology

```text
                            USER / CLI
                                │
                                ▼
                          SLASH COMMANDS  [/orchestrate, /discover, /status]
                                │
                                ▼
                        ORCHESTRATOR AGENT
                  (Single-Writer State Authority)
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
          DISCOVERY AGENT              DEPENDENCY AGENT
       [Inspects baseline]           [Builds dependency DAG]
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ▼
                    DYNAMIC WAVE DISPATCHER
              (Topological Execution Batches: wave_0, wave_1, ... wave_N)
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
    CONTRIB AGENT         CUSTOM MODULE          CUSTOM THEME / CONFIG /
                          (Delegates API work)   DATA MIGRATION AGENTS
          │                     │                     │
          │                     ▼                     │
          │              API-MODERNIZATION            │
          │              (Scoped DI conversion)       │
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                                ▼
                   CANONICAL `agent_result` (v1.0)
                                │
                                ▼
                   ORCHESTRATOR VALIDATION GATE
              (Validates schema, scope, evidence, paths)
                                │
                                ▼
                   AUTHORITATIVE STATE UPDATE
                 (state/migration-state.yml)
                                │
                                ▼
                          TESTING AGENT
           (Component-Appropriate Testing & Verification Strategy)
                                │
                                ▼
                        VALIDATION AGENT
           (12-Dimensional Comparative Behavioral Parity Audit)
                                │
                                ▼
                        FINAL AUDIT AGENT
              (8 Evidence-Based Lifecycle Acceptance Gates)
                                │
                                ▼
                         FINAL OUTCOME
           [COMPLETE | COMPLETE_WITH_GAPS | BLOCKED | INCOMPLETE]
```

---

## 3. Source of Truth & Dual State Separation

```text
1. Evidence / Execution Artifacts   (Terminal logs, query counts, diffs, test logs)
                 ↓
2. Component Runtime State          (state/migration-state.yml -> component_states)
                 ↓
3. Global Lifecycle State           (state/migration-state.yml -> lifecycle_phase, current_wave)
                 ↓
4. Manifest Scope Metadata          (state/migration-manifest.yml -> inventory & dependencies)
                 ↓
5. Reports / Summaries / Dashboards (reports/* -> generated views of state & evidence)
```

- **`state/migration-manifest.yml`** ("WHAT are we migrating?"): Static inventory of discovered custom modules, .inc source files, functions, inclusion trees, contrib modules, themes, content types, and data pipelines with declared dependencies and target strategy.
- **`state/migration-state.yml`** ("WHERE are we in the migration?"): The single source of truth for dynamic lifecycle progress, active wave batch, component statuses, health monitoring, and active blocker tickets.

---

## 4. Legacy Custom Database, Schema, Data Model, Custom Entities, Bundles, Fields, Revisions, Translations, Forms, Form Alters, AJAX, Frontend JavaScript, CSS, Libraries, Procedural Hooks, Configuration, State, Variables, Legacy Custom PHP File, OOP Class & Legacy `.inc` File Re-engineering Architecture

The factory recursively discovers and re-engineers Legacy Custom Entities, bundles, fields, revisions, translations, entity references, Forms, Form API elements, Form Alters, AJAX callbacks & commands, Frontend JavaScript behaviors, `once()` patterns, `drupalSettings`, CSS stylesheets, SMACSS asset libraries, Custom Database schemas, database access calls, stored data models, Procedural Hook Implementations (`hook_menu`, `hook_form_alter`, `hook_node_*`, custom hooks, alter hooks), Configuration & State Variables (`variable_get/set/del`, `system_settings_form`), Legacy Custom PHP Files, OOP classes, constructors, interfaces, traits, and Legacy `.inc` Files within Drupal 7 custom modules into modern Drupal 10/11 architectures.

- **Recursive Scanning & Zero Naming Assumptions**: Scans module roots and nested subdirectories discovering all `*.php`, `*.inc`, `*.module`, `*.install`, `*.profile`, `*.drush.inc`, `*.js`, `*.css`, `*.scss`, and `*.less` files (e.g. `lib/Processor.php`, `admin.inc`, `includes/foo.inc`, `commands/*.inc`, `js/*.js`, `css/*.css`).
- **Frontend JavaScript & Behavior Discovery (Step 18)**: Discovers all JavaScript files, `Drupal.behaviors` implementations, `attach`/`detach` methods, DOM ready patterns, and `jQuery.once()` invocations. Modernizes to `@drupal/once` / `once()` iterating natively with `forEach()` within strict behavior closures.
- **`Drupal.settings` $\rightarrow$ `drupalSettings` Data Flow**: Traces PHP configuration producers (`drupal_add_js(..., 'setting')`, `#attached['drupalSettings']`) and maps client-side consumers (`Drupal.settings` $\rightarrow$ `drupalSettings`).
- **Client-Side AJAX Behavior & Command Modernization**: Discovers `Drupal.ajax` instances, progress handlers, and custom client-side command handlers (`Drupal.AjaxCommands.prototype`), ensuring seamless reactivity to modern server `CommandInterface` responses.
- **CSS Stylesheet & SMACSS Architecture**: Analyzes stylesheet rules, responsive `@media` queries, and preprocess alterations (`hook_css_alter`), categorizing styles into SMACSS categories (`base`, `layout`, `component`, `state`, `theme`) in `<module>.libraries.yml`.
- **Modern Library Registration (`*.libraries.yml`)**: Converts legacy `.info` `scripts[]` / `stylesheets[]` and procedural `drupal_add_js()` / `drupal_add_css()` / `drupal_add_library()` calls into modern structured `<module>.libraries.yml` asset definitions with explicit core dependencies (`core/drupal`, `core/drupalSettings`, `core/once`, `core/jquery`).
- **Frontend Security & Accessibility**: Audits DOM manipulation for XSS risks (`.html()`, `innerHTML` $\rightarrow$ `Drupal.checkPlain()`, `Drupal.t()`), CSP compliance, ARIA live region updates, and keyboard focus management.
- **21 Frontend Target Architecture Classifications**: Categorizes frontend artifacts into 21 standard target architectures (`DRUPAL_LIBRARY`, `JS_BEHAVIOR`, `JS_ONCE_BEHAVIOR`, `AJAX_FRONTEND_BEHAVIOR`, `DRUPAL_SETTINGS_CONSUMER`, `CSS_LIBRARY`, `INLINE_JS`, `INLINE_CSS`, `EXTERNAL_LIBRARY`, `THIRD_PARTY_LIBRARY`, `THEME_LIBRARY`, `MODULE_LIBRARY`, `PREPROCESS_ATTACHMENT`, `RENDER_ARRAY_ATTACHMENT`, `AJAX_ATTACHMENT`, `CUSTOM_AJAX_COMMAND_CLIENT`, `TEMPLATE_SCRIPT`, `TEMPLATE_STYLE`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`).
- **17 Standardized Frontend Migration Strategies**: Maps frontend assets to 17 explicit strategies: `LIBRARY_YML_REWRITE`, `BEHAVIOR_REWRITE`, `ONCE_API_REWRITE`, `DRUPAL_SETTINGS_REWRITE`, `AJAX_CLIENT_REWRITE`, `CSS_LIBRARY_REWRITE`, `INLINE_TO_LIBRARY`, `INLINE_TO_BEHAVIOR`, `PREPROCESS_ATTACHMENT_REWRITE`, `THIRD_PARTY_LIBRARY_REPLACEMENT`, `EXTERNAL_ASSET_REVIEW`, `THEME_ASSET_HANDOFF`, `OBSOLETE`, `REPLACED`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Custom & Core Entity Discovery**: Exhaustively detects core entity types (`node`, `user`, `taxonomy_term`, `taxonomy_vocabulary`, `comment`, `file`) and custom/contrib entity implementations (`hook_entity_info()`, Entity API, custom entity controllers). Discovers entity keys (`id`, `revision`, `bundle`, `label`, `language`, `uuid`), base tables, data tables, revision tables, translation tables, and access control handlers.
- **Field & Storage Discovery & Taxonomy**: Discovers all field definitions and instances (`hook_field_info()`, `hook_field_instance_info()`, `field_create_field()`, `field_create_instance()`, `field_attach_*`). Classifies fields by type, cardinality, requiredness, translatability, revisionability, storage backend, widgets, and formatters.
- **Entity Reference & Relationship Topologies**: Maps entity references (`entityreference`, `taxonomy_term_reference`, `user_reference`, `node_reference`, junction tables) into modern typed Entity References (`core.base_field_override`, `field.storage.*`). Resolves reference dependencies in DAG wave scheduling.
- **Revision & History Accounting**: Identifies revision tables, revision flags, log fields, timestamps, and revision tracking logic. Maps historical revisions to D10 `RevisionableInterface` entities or assigns `HUMAN_DECISION_REQUIRED` where preservation is ambiguous.
- **Translation & Multilingual Architecture**: Discovers multilingual configurations, `$language`, `LANGUAGE_NONE`, translation tables, and field translation setups. Maps to modern Content Translation (`TranslatableInterface`, `data_table`).
- **Forms, Form API & Form Builder Discovery (Step 17)**: Discovers all form builders, named form builders, and invocation APIs (`drupal_get_form()`, `drupal_build_form()`, `drupal_form_submit()`). Parses Form API element trees (`#type`, `#title`, `#tree`, `#states`, `#attached`, `#validate`, `#submit`, `#element_validate`, `#process`).
- **Form Validation, Submission & Side Effect Call Graph**: Traces validation callbacks (`form_set_error()`, `#validate`), submission handlers (`#submit`), database transactions, entity saves, config writes, redirects (`$form_state['redirect']`), and messages (`drupal_set_message()`).
- **Form Alteration Analysis**: Identifies and analyzes all procedural form alteration hooks (`hook_form_alter()`, `hook_form_FORM_ID_alter()`), mapping modifications to modern form alters or decoupled Symfony Event Subscribers.
- **AJAX Behavior, Callbacks & Command Modernization**: Discovers `#ajax` declarations, `ajax_render()`, `ajax_deliver()`, and procedural `ajax_command_*()` calls. Modernizes to `AjaxResponse` returning OOP command classes (`ReplaceCommand`, `HtmlCommand`, `AppendCommand`, `InvokeCommand`, `MessageCommand`, `SettingsCommand`).
- **`$form_state` Lifecycle, Rebuilds & Multistep Flows**: Analyzes `$form_state` storage, step counters, wizard branch logic, back/next transitions, and temporary state persistence across rebuilds (`$form_state->setRebuild(TRUE)`).
- **Form Security, CSRF & File Uploads**: Audits CSRF token protection (`#token`), route access checks, input sanitization, open redirects, and managed file uploads (`#type => managed_file`, `file_save_upload()`).
- **19 Forms & AJAX Target Architecture Classifications**: Categorizes form artifacts into 19 standard target architectures (`FORM_BASE`, `CONFIG_FORM_BASE`, `CONFIRM_FORM_BASE`, `ENTITY_FORM`, `CONTENT_ENTITY_FORM`, `CONFIG_ENTITY_FORM`, `PLUGIN_FORM`, `ROUTED_FORM`, `AJAX_FORM`, `AJAX_CALLBACK`, `AJAX_COMMAND`, `FORM_ALTER`, `FORM_VALIDATOR`, `FORM_SUBMIT_HANDLER`, `SERVICE_BACKED_FORM`, `MULTISTEP_FORM`, `FILE_UPLOAD_FORM`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`).
- **15 Standardized Form & AJAX Migration Strategies**: Maps form artifacts to 15 explicit strategies: `DIRECT_MODERNIZATION`, `FORM_API_REWRITE`, `FORMBASE_REWRITE`, `CONFIG_FORM_REWRITE`, `ENTITY_FORM_REWRITE`, `AJAX_REWRITE`, `CONTROLLER_PLUS_FORM`, `SERVICE_BACKED_REWRITE`, `MULTISTEP_REWRITE`, `CALLBACK_REFACTOR`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **26 Target Architecture Classifications (Step 16)**: Categorizes discovered entity/field/revision/translation artifacts into 26 standard target architectures (`CONTENT_ENTITY`, `CONFIG_ENTITY`, `ENTITY_TYPE`, `BUNDLE`, `ENTITY_STORAGE`, `ENTITY_ACCESS_HANDLER`, `ENTITY_QUERY`, `FIELD_STORAGE`, `FIELD_CONFIG`, `FIELD_TYPE`, `FIELD_WIDGET`, `FIELD_FORMATTER`, `ENTITY_REFERENCE`, `REVISIONABLE_ENTITY`, `TRANSLATABLE_ENTITY`, `TRANSLATION_HANDLER`, `PLUGIN`, `SERVICE`, `REPOSITORY`, `CUSTOM_STORAGE`, `CONFIGURATION`, `STATE`, `EXTERNAL_SYSTEM`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`). Supports non-1:1 (one-to-many and many-to-one) transformations.
- **16 Standardized Entity & Field Migration Strategies**: Maps discovered artifacts to 16 explicit strategies: `DIRECT_ENTITY_MIGRATION`, `TRANSFORMED_ENTITY_MIGRATION`, `ENTITY_TYPE_REBUILD`, `BUNDLE_REBUILD`, `FIELD_REBUILD`, `FIELD_TRANSFORMATION`, `REFERENCE_REMAP`, `REVISION_MIGRATION`, `TRANSLATION_MIGRATION`, `CONFIG_ENTITY_MIGRATION`, `CUSTOM_STORAGE_MIGRATION`, `CONTENT_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Generic & Custom Procedural Hook Discovery**: Exhaustively detects all procedural hook implementations matching `<module>_<hook>` naming patterns, classifying them into a 9-type taxonomy (`CORE_HOOK`, `CONTRIB_HOOK`, `CUSTOM_HOOK`, `ALTER_HOOK`, `ENTITY_HOOK`, `FORM_HOOK`, `THEME_HOOK`, `INSTALL_UPDATE_HOOK`, `UNKNOWN_UNVERIFIED_HOOK`).
- **Configuration, State & Persistent Variable Discovery**: Exhaustively discovers all configuration, variable, state, and settings access patterns (`variable_get()`, `variable_set()`, `variable_del()`, `variable_initialize()`, `system_settings_form()`, `$conf`, `$GLOBALS`, static caches, environment values).
- **20-Type Configuration Taxonomy**: Classifies every discovered configuration/state item into a 20-type taxonomy (`D7_VARIABLE`, `D7_VARIABLE_DEFAULT`, `D7_VARIABLE_WRITE`, `D7_VARIABLE_DELETE`, `D7_GLOBAL_CONFIG`, `D7_FORM_SETTING`, `D7_ADMIN_SETTING`, `D7_RUNTIME_SETTING`, `D7_PERSISTENT_STATE`, `D7_CACHE_STATE`, `D7_CUSTOM_TABLE_STATE`, `D7_SERIALIZED_VALUE`, `D7_JSON_VALUE`, `D7_ENVIRONMENT_VALUE`, `D7_INSTALL_CONFIGURATION`, `D7_UPDATE_CONFIGURATION`, `D7_UNINSTALL_CLEANUP`, `D7_DERIVED_CONFIGURATION`, `D7_EXTERNAL_CONFIGURATION`, `D7_UNKNOWN_UNVERIFIED`).
- **Semantic Domain Distinction**: Explicitly distinguishes Configuration (CMI) vs State (State API) vs Content/Data vs Environment/Secrets vs Cache.
- **Config API & Typed Schema Modernization**: Generates default configuration YAML (`config/install/<module>.settings.yml`) and typed schemas (`config/schema/<module>.schema.yml`). Re-engineers `system_settings_form()` into modern `ConfigFormBase` classes with Dependency Injection.
- **State API Modernization**: Maps dynamic runtime state, timestamps, counters, and synchronization markers to `\Drupal::state()` / `StateInterface` with uninstallation cleanup in `hook_uninstall()`.
- **Secret Isolation (Rule 10)**: Guarantees zero credentials, API keys, tokens, or passwords are committed to CMI YAML files. Routes sensitive settings to `settings.php` overrides, `getenv()`, or Key module.
- **Serialized & Structured Value Modernization**: Maps serialized arrays and JSON values to typed schema mappings; flags opaque PHP objects as `HUMAN_DECISION_REQUIRED` or `UNVERIFIED`.
- **14 Configuration Migration Strategies**: Standardizes modernization strategies: `DIRECT_CONFIG_MIGRATION`, `TRANSFORMED_CONFIG_MIGRATION`, `CONFIG_ENTITY_MIGRATION`, `STATE_MIGRATION`, `SETTINGS_MIGRATION`, `ENVIRONMENT_MIGRATION`, `KEY_VALUE_MIGRATION`, `CONTENT_MIGRATION`, `CACHE_REBUILD`, `CUSTOM_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Custom Hook Invocation Extraction**: Detects custom hooks invoked via `module_invoke_all('{hook}', ...)`, `module_invoke()`, or declared in module documentation, re-engineering them into Symfony `EventDispatcher` events and `EventSubscriberInterface` listeners.
- **Alter Hook Behavioral Analysis**: Identifies and analyzes all alter hooks (`hook_form_alter`, `hook_menu_alter`, `hook_views_data_alter`, `hook_query_alter`, etc.), delegating execution to injected service instances.
- **hook_menu() Exhaustive Decomposition**: Decomposes monolithic `hook_menu()` implementations into discrete modern artifacts: routes (`.routing.yml`), Controllers (`src/Controller/`), Form classes (`src/Form/`), Custom Access Checkers (`src/Access/`), Menu links (`.links.menu.yml`), Local tasks (`.links.task.yml`), Local actions (`.links.action.yml`), and Contextual links (`.links.contextual.yml`).
- **Custom Database & Schema Discovery (`hook_schema`)**: Analyzes custom schema definitions in `hook_schema()`, columns, types, lengths, primary keys, unique constraints, indexes, compound indexes, and foreign keys. Catalogs entity reference fields (`uid`, `nid`, `tid`, `fid`, `entity_id`).
- **Database Lifecycle & Update Hooks**: Analyzes `hook_install()`, `hook_uninstall()`, and `hook_update_N()`, distinguishing base schema from historical upgrade steps to determine resulting schema and data behavior.
- **Database API, Static & Dynamic SQL Analysis**: Analyzes procedural database operations (`db_query`, `db_select`, `db_insert`, `db_update`, `db_delete`, `db_merge`, `db_transaction`). Detects dynamic SQL concatenations and flags unresolvable dynamic queries as `[UNVERIFIED RESULT]` / `HUMAN_DECISION_REQUIRED`.
- **SQL Safety & Parameterization**: Identifies missing placeholders, raw concatenations, and user inputs, modernizing queries into safe parameterized statements or Query Builders.
- **17 Data Semantic Categories**: Semantically classifies custom data into `CONTENT`, `CONFIGURATION`, `STATE`, `USER_DATA`, `ENTITY_DATA`, `FIELD_DATA`, `RELATIONSHIP_DATA`, `TRANSACTION_DATA`, `AUDIT_DATA`, `CACHE_DATA`, `QUEUE_DATA`, `TEMPORARY_DATA`, `INTEGRATION_DATA`, `LOOKUP_DATA`, `REFERENCE_DATA`, `LEGACY_DATA`, or `UNKNOWN`.
- **Serialized Data & Transformation**: Detects PHP serialized strings (`serialize()` / `unserialize()`), JSON, and encoded objects, defining safe migration transformation pipelines into modern structured formats.
- **CRUD & Concurrency Accounting**: Maps complete CREATE, READ, UPDATE, DELETE call trees across all services, controllers, forms, queue workers, cron, and Drush commands, preserving transactional consistency (`$connection->startTransaction()`).
- **Target Architecture & Non-1:1 Mapping**: Re-engineers custom tables, hooks, variables, entities, fields, and data models into Content Entities (`src/Entity/`), Config Entities, Config API (`config.factory`), State API (`\Drupal::state()`), KeyValue stores, or dedicated Repository Services (`src/Repository/`) utilizing `\Drupal\Core\Database\Connection`. Supports one-to-many and many-to-one transformations.
- **10 Migration Data Strategies**: Applies standardized ETL strategies: `DIRECT_MIGRATION`, `TRANSFORMED_MIGRATION`, `ENTITY_MIGRATION`, `CONFIG_MIGRATION`, `STATE_MIGRATION`, `CUSTOM_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Class, Interface, Trait & Constructor Discovery**: Extracts classes, interfaces, traits, abstract classes, constants, properties, and methods. Analyzes constructors (`__construct()` and legacy `ClassName()`), parameter dependencies, global state usage (`$user`, `$language`, `variable_get()`), and side effects.
- **Autoloading & Include / Require Resolution**: Inspects `require`, `include`, `module_load_include()`, `.info` `files[]`, and custom autoloaders, replacing manual loading with Composer PSR-4 autoloading. Marks unverified dynamic includes/calls as `[UNVERIFIED RESULT]`.
- **22-Class Architectural Taxonomy**: Classifies every functional unit into standard architectural roles (`SERVICE_BUSINESS_LOGIC`, `CONTROLLER`, `FORM`, `PLUGIN`, `EVENT_SUBSCRIBER`, `ACCESS_CHECKER`, etc.).
- **Constructor Dependency Injection & Non-1:1 Mapping**: Refactors constructors to modern `__construct(...)` with injected services (`database`, `entity_type.manager`, `config.factory`, `current_user`) avoiding service proliferation. Supports 1-to-many class decomposition and many-to-one service consolidation.
- **Strict Zero-Omission Outcome Accounting**: Every custom entity type, bundle, field definition, revision table, translation artifact, custom database table, schema, data model, procedural hook implementation, custom hook, configuration/state variable, custom PHP file, class, constructor, method, and `.inc` file must resolve to `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`. The states `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, and `SILENTLY_OMITTED` are strictly forbidden.

---

---

## 5. The 13 Specialized Agents, Skills & References

| # | Agent | Primary Role | Associated Skills & Key References |
|---|---|---|---|
| 1 | **`orchestrator`** | Master workflow coordinator, wave scheduler & state authority. | Pure lifecycle governance; `references/migration-patterns/common-conversions.md` |
| 2 | **`discovery`** | Deep read-only inspection of D7 and D10 environments. | `skills/d7-analysis`, `references/drupal-7/apis.md`, `references/drupal-7/hooks.md` |
| 3 | **`dependency`** | Builds dependency DAG, detects cycles, calculates wave batches. | `skills/dependency-analysis`, `references/drupal-7/apis.md` |
| 4 | **`contrib-module`** | Evaluates contrib compatibility, core merges, and D11 removals. | `skills/contrib-evaluation`, `references/drupal-10/architecture.md` |
| 5 | **`custom-module`** | Coordinates 12-step modernization of custom modules. | `skills/custom-module-migration`, `skills/d7-to-d10-mapping`, `skills/d10-architecture` |
| 6 | **`custom-theme`** | Converts PHPTemplate to Twig and modern asset libraries. | `skills/theme-modernization`, `references/drupal-10/twig-filters.md` |
| 7 | **`configuration`** | Translates variables and settings into CMI YAML. | `skills/configuration-migration`, `references/drupal-10/architecture.md` |
| 8 | **`data-migration`** | Architects core Migration API pipelines and table ETL. | `skills/migration-api`, `references/migration-patterns/field-mapping.md` |
| 9 | **`api-modernization`** | Enforces Dependency Injection; forbids blind `\Drupal::*`. | `skills/d7-to-d10-mapping`, `skills/d10-architecture`, `references/drupal-10/` |
| 10 | **`integration`** | Modernizes REST, SOAP, webhooks, and external DB connections. | `skills/integration-modernization`, `skills/d10-architecture` |
| 11 | **`testing`** | Configures and validates PHPUnit, PHPStan, and PHPCS. | `skills/testing`, `references/drupal-10/architecture.md` |
| 12 | **`validation`** | Conducts 12-point comparative behavioral audits. | `skills/behavioral-validation`, `references/migration-patterns/` |
| 13 | **`final-audit`** | Verifies D11 readiness, security posture, and 8 acceptance gates. | Pure lifecycle governance; All 7 references and validation matrices |

---

## 6. Dynamic Waves, Concurrency & Failure Recovery

1. **Dynamic DAG Waves**: Wave batches (`wave_0`, `wave_1`, ... `wave_N`) are calculated at runtime from dependency in-degrees and readiness state.
2. **Concurrency Serialization**: Parallel execution is permitted only on disjoint file sets. Concurrently modifying shared files (`.services.yml`, `.routing.yml`), shared configuration, or schemas is strictly serialized.
3. **Stage-Aware Recovery**: Failures re-enter at the appropriate upstream stage (e.g. `SOURCE_AMBIGUITY` -> Discovery; `TEST_FAILURE` -> Implementation/Testing).
4. **Blocker Isolation**: Component blocks generate `BLOCKED` and propagate `BLOCKED_UPSTREAM` to direct dependents, while independent waves continue.

---

## 7. File System & Path Protection Model

```text
+-------------------------------------------------------------------+
|                        WORKSPACE ROOT                             |
|                                                                   |
|  [source.path (D7)]       READ-ONLY      (Writes strictly rejected)|
|  ├── modules/                                                     |
|  └── ...                                                          |
|                                                                   |
|  [target.path (D10/11)]   WRITE-ALLOWED  (Config-driven docroot)   |
|  ├── <target_module_dir>/                                         |
|  ├── <target_theme_dir>/                                          |
|  ├── <target_config_dir>/                                         |
|  └── ...                                                          |
|                                                                   |
|  [migration-agent-framework]  STATE & AUDIT                       |
|  ├── agents/                                                      |
|  ├── skills/                                                      |
|  ├── commands/                                                    |
|  ├── reports/                                                     |
|  ├── state/                                                       |
|  └── logs/file-change-log/                                        |
+-------------------------------------------------------------------+
```

- Writes to `source.path` are rejected immediately.
- Overlapping source and target paths trigger an immediate **Global Migration Block**.
- Target paths (`target_module_dir`, `target_theme_dir`, `target_config_dir`) are dynamically derived from `migration.config.yml`.
- Every modified, created, or deleted file in `target.path` must generate an entry in `logs/file-change-log/`.
