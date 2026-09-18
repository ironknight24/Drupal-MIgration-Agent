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

## 4. Legacy Custom Database, Schema, Data Model, Legacy Custom PHP File, OOP Class & Legacy `.inc` File Re-engineering Architecture

The factory recursively discovers and re-engineers Legacy Custom Database schemas, database access calls, stored data models, Legacy Custom PHP Files, OOP classes, constructors, interfaces, traits, and Legacy `.inc` Files within Drupal 7 custom modules into modern Drupal 10/11 architectures.

- **Recursive Scanning & Zero Naming Assumptions**: Scans module roots and nested subdirectories discovering all `*.php`, `*.inc`, `*.module`, `*.install`, `*.profile`, and `*.drush.inc` files (e.g. `lib/Processor.php`, `admin.inc`, `includes/foo.inc`, `commands/*.inc`).
- **Custom Database & Schema Discovery (`hook_schema`)**: Analyzes custom schema definitions in `hook_schema()`, columns, types, lengths, primary keys, unique constraints, indexes, compound indexes, and foreign keys. Catalogs entity reference fields (`uid`, `nid`, `tid`, `fid`, `entity_id`).
- **Database Lifecycle & Update Hooks**: Analyzes `hook_install()`, `hook_uninstall()`, and `hook_update_N()`, distinguishing base schema from historical upgrade steps to determine resulting schema and data behavior.
- **Database API, Static & Dynamic SQL Analysis**: Analyzes procedural database operations (`db_query`, `db_select`, `db_insert`, `db_update`, `db_delete`, `db_merge`, `db_transaction`). Detects dynamic SQL concatenations and flags unresolvable dynamic queries as `[UNVERIFIED RESULT]` / `HUMAN_DECISION_REQUIRED`.
- **SQL Safety & Parameterization**: Identifies missing placeholders, raw concatenations, and user inputs, modernizing queries into safe parameterized statements or Query Builders.
- **17 Data Semantic Categories**: Semantically classifies custom data into `CONTENT`, `CONFIGURATION`, `STATE`, `USER_DATA`, `ENTITY_DATA`, `FIELD_DATA`, `RELATIONSHIP_DATA`, `TRANSACTION_DATA`, `AUDIT_DATA`, `CACHE_DATA`, `QUEUE_DATA`, `TEMPORARY_DATA`, `INTEGRATION_DATA`, `LOOKUP_DATA`, `REFERENCE_DATA`, `LEGACY_DATA`, or `UNKNOWN`.
- **Serialized Data & Transformation**: Detects PHP serialized strings (`serialize()` / `unserialize()`), JSON, and encoded objects, defining safe migration transformation pipelines into modern structured formats.
- **CRUD & Concurrency Accounting**: Maps complete CREATE, READ, UPDATE, DELETE call trees across all services, controllers, forms, queue workers, cron, and Drush commands, preserving transactional consistency (`$connection->startTransaction()`).
- **Target Architecture & Non-1:1 Mapping**: Re-engineers custom tables and data models into Content Entities (`src/Entity/`), Config Entities, Config API (`config.factory`), State API (`\Drupal::state()`), KeyValue stores, or dedicated Repository Services (`src/Repository/`) utilizing `\Drupal\Core\Database\Connection`. Supports one-to-many and many-to-one transformations.
- **10 Migration Data Strategies**: Applies standardized ETL strategies: `DIRECT_MIGRATION`, `TRANSFORMED_MIGRATION`, `ENTITY_MIGRATION`, `CONFIG_MIGRATION`, `STATE_MIGRATION`, `CUSTOM_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Class, Interface, Trait & Constructor Discovery**: Extracts classes, interfaces, traits, abstract classes, constants, properties, and methods. Analyzes constructors (`__construct()` and legacy `ClassName()`), parameter dependencies, global state usage (`$user`, `$language`, `variable_get()`), and side effects.
- **Autoloading & Include / Require Resolution**: Inspects `require`, `include`, `module_load_include()`, `.info` `files[]`, and custom autoloaders, replacing manual loading with Composer PSR-4 autoloading. Marks unverified dynamic includes/calls as `[UNVERIFIED RESULT]`.
- **22-Class Architectural Taxonomy**: Classifies every functional unit into standard architectural roles (`SERVICE_BUSINESS_LOGIC`, `CONTROLLER`, `FORM`, `PLUGIN`, `EVENT_SUBSCRIBER`, `ACCESS_CHECKER`, etc.).
- **Constructor Dependency Injection & Non-1:1 Mapping**: Refactors constructors to modern `__construct(...)` with injected services (`database`, `entity_type.manager`, `config.factory`, `current_user`) avoiding service proliferation. Supports 1-to-many class decomposition and many-to-one service consolidation.
- **Strict Zero-Omission Outcome Accounting**: Every custom database table, schema, data model, custom PHP file, class, constructor, method, and `.inc` file must resolve to `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`. The states `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, and `SILENTLY_OMITTED` are strictly forbidden.

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
