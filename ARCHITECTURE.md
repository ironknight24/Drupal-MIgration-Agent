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

## 4. Legacy `.inc` File Re-engineering & Accounting Architecture

The factory recursively analyzes `.inc` files within Drupal 7 custom modules and migrates the functionality they contain into appropriate Drupal 10 architecture.

- **Recursive Scanning & Zero Naming Assumptions**: Scans module roots and nested subdirectories discovering all `.inc` and `.php` files (e.g. `module.inc`, `admin.inc`, `includes/foo.inc`, `commands/*.inc`).
- **Include / Require Graph Resolution**: Inspects `include`, `require`, `module_load_include()`, `form_load_include()`, `ctools_include()`, and `hook_menu()` `'file'` declarations. Marks unverified dynamic includes as `[UNVERIFIED RESULT]`.
- **Fine-Grained Callable Dissection**: Extracts functions, classes, callbacks, form builders, access checkers, batch/queue workers, and Drush commands.
- **18-Class Functional Taxonomy**: Classifies every functional piece into standard architectural roles.
- **Non-1:1 Architectural Mapping**: `.inc` files are not copied blindly or mapped 1:1 to target files. Functionality is re-engineered into modern Symfony/Drupal OOP services, controllers, forms, plugins, and Drush command classes.
- **Strict Zero-Omission Outcome Accounting**: Every `.inc` file and function must resolve to `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`. The states `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, and `SILENTLY_OMITTED` are forbidden.

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
