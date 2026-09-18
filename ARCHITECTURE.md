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
                 (Lifecycle & State Authority)
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
                         & API AGENTS           DATA MIGRATION AGENTS
         │                     │                     │
         └─────────────────────┼─────────────────────┘
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

- **`state/migration-manifest.yml`** ("WHAT are we migrating?"): Static inventory of discovered custom modules, contrib modules, themes, content types, and data pipelines with declared dependencies and target strategy.
- **`state/migration-state.yml`** ("WHERE are we in the migration?"): The single source of truth for dynamic lifecycle progress, active wave batch, component statuses, health monitoring, and active blocker tickets.

---

## 4. The 13 Specialized Agents, Skills & References

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

## 5. Dynamic Waves, Concurrency & Failure Recovery

1. **Dynamic DAG Waves**: Wave batches (`wave_0`, `wave_1`, ... `wave_N`) are calculated at runtime from dependency in-degrees and readiness state.
2. **Concurrency Serialization**: Parallel execution is permitted only on disjoint file sets. Concurrently modifying shared files (`.services.yml`, `.routing.yml`), shared configuration, or schemas is strictly serialized.
3. **Stage-Aware Recovery**: Failures re-enter at the appropriate upstream stage (e.g. `SOURCE_AMBIGUITY` -> Discovery; `TEST_FAILURE` -> Implementation/Testing).
4. **Blocker Isolation**: Component blocks generate `BLOCKED` and propagate `BLOCKED_UPSTREAM` to direct dependents, while independent waves continue.

---

## 6. File System & Path Protection Model

```
+-------------------------------------------------------------------+
|                        WORKSPACE ROOT                             |
|                                                                   |
|  [source.path (D7)]       READ-ONLY      (Writes strictly rejected)|
|  ├── modules/                                                     |
|  └── ...                                                          |
|                                                                   |
|  [target.path (D10/11)]   WRITE-ALLOWED  (Logged modifications)    |
|  ├── web/modules/custom/                                          |
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
- Every modified, created, or deleted file in `target.path` must generate an entry in `logs/file-change-log/`.
