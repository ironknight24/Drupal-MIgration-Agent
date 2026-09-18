# Migration Lifecycle & Dynamic Execution Model

## 1. Lifecycle Philosophy

The migration from Drupal 7 to Drupal 10/11 follows a state-driven, dynamic execution lifecycle. While canonical phase milestones exist, the framework does **not** assume an immutable linear sequence.

Real-world Drupal codebases have complex, interdependent architectures. Therefore, the **Orchestrator** evaluates the **Dependency Graph (DAG)** at runtime to dynamically calculate execution waves, manage parallel execution, serialize shared file modifications, and isolate blocked components.

---

## 2. Canonical Lifecycle Phases

```text
INITIALIZED
    ↓
DISCOVERY
    ↓
DEPENDENCY_ANALYSIS
    ↓
MIGRATION_PLANNING
    ↓
WAVE_EXECUTION (Dynamic Batches: wave_0, wave_1, ... wave_N)
    ↓
TESTING (Component-Appropriate QA)
    ↓
BEHAVIORAL_VALIDATION (12-Point Comparative Parity)
    ↓
FINAL_AUDIT (8 Acceptance Gates)
    ↓
COMPLETED
```

### Phase Definitions & Ownership

| Phase Identifier | Managing Agent | Core Deliverable & Artifact |
|:---|:---|:---|
| `INITIALIZED` | Setup | Master configuration, directory structure, initialized state. |
| `DISCOVERY` | `discovery` | `reports/discovery/`, populated `migration-manifest.yml`. |
| `DEPENDENCY_ANALYSIS` | `dependency` | `reports/dependencies/`, dependency DAG, wave calculations. |
| `MIGRATION_PLANNING` | `custom-module` / Specialist | Per-component migration plans in `reports/*/PLAN-*.md`. |
| `WAVE_EXECUTION` | Specialist Agents | Modernized code in `target.path`, entries in `logs/file-change-log/`. |
| `TESTING` | `testing` | `reports/testing/`, verified test outputs and sniffs. |
| `BEHAVIORAL_VALIDATION` | `validation` | `reports/validation/`, 12-dimensional validation matrices. |
| `FINAL_AUDIT` | `final-audit` | `reports/final/FINAL-AUDIT-REPORT-<DATE>.md`, gap analysis, sign-off. |
| `COMPLETED` | `orchestrator` | Final migration summary and handoff documentation. |

---

## 3. Canonical Component Status Model

A standardized 15-state status vocabulary governs individual component lifecycles in `state/migration-state.yml`:

```text
                      NOT_STARTED
                           │  (Discovery Agent)
                           ▼
                       DISCOVERED
                           │  (Dependency Agent)
                           ▼
                        ANALYZED
                           │  (Orchestrator Wave Scheduler)
               ┌───────────┴───────────┐
               ▼                       ▼
             READY                  DEFERRED
          (Deps met)              (Deps pending)
               │                       ▲
               ▼                       │
          IN_PROGRESS ◄────────────────┼──────── (Dependencies unblocked)
          (Specialist)                 │
               │                       │
               ├───────────────────────┴────────► BLOCKED_UPSTREAM
               │                                   (Upstream blocked)
               ▼
            MIGRATED ◄──────────────────────────┐
               │                                │
               ▼                                │
            TESTING ◄───────────────────┐       │
               │                        │       │
               ▼                        │       │
           VALIDATING                   │       │
               │                        │       │
      ┌────────┴────────┐               │       │
      ▼                 ▼               │       │
  VALIDATED          FAILED             │       │
      │                 │               │       │
      │                 └─────────► REMEDIATION ┤ (Stage-Aware Re-entry)
      ▼                                 ▲       │
   COMPLETE                             │       │
      or                                │       │
COMPLETE_WITH_GAPS                      │       │
                                        │       │
   BLOCKED ─────────────────────────────┘       │
(Direct failure)                                │
                                                │
   BLOCKED_UPSTREAM ────────────────────────────┘ (Upstream remediated)
```

### Component-Aware State Applicability
- **Custom Modules**: Utilize full lifecycle (`NOT_STARTED` -> `DISCOVERED` -> `ANALYZED` -> `READY` -> `IN_PROGRESS` -> `MIGRATED` -> `TESTING` -> `VALIDATING` -> `VALIDATED` -> `COMPLETE`).
- **Contrib Modules**: Utilize evaluation lifecycle (`NOT_STARTED` -> `DISCOVERED` -> `ANALYZED` -> `COMPLETE` / `DEFERRED` / `BLOCKED`).
- **Configuration**: Utilize export lifecycle (`NOT_STARTED` -> `DISCOVERED` -> `READY` -> `IN_PROGRESS` -> `MIGRATED` -> `VALIDATING` -> `VALIDATED` -> `COMPLETE`).
- **Data Migrations**: Utilize pipeline lifecycle (`NOT_STARTED` -> `DISCOVERED` -> `ANALYZED` -> `READY` -> `IN_PROGRESS` -> `MIGRATED` -> `VALIDATING` -> `VALIDATED` -> `COMPLETE`).
- **Themes**: Utilize presentation lifecycle (`NOT_STARTED` -> `DISCOVERED` -> `ANALYZED` -> `READY` -> `IN_PROGRESS` -> `MIGRATED` -> `VALIDATING` -> `VALIDATED` -> `COMPLETE`).

---

## 4. Dynamic Dependency-Aware Wave Execution

Waves are **dynamic execution batches** calculated at runtime from the dependency DAG, readiness state, component constraints, and ordering rules. Wave numbers (`wave_0`, `wave_1`, ... `wave_N`) represent topological tiers, NOT hardcoded global categories.

### Upstream Dependency Satisfaction
A component's upstream dependency requirement is satisfied if:
1. The dependency is a custom component whose runtime status is `COMPLETE` or `VALIDATED`.
2. The dependency is satisfied natively by the target Drupal core version (`satisfaction_source: target_core`).
3. The dependency is satisfied by an approved, compatible contributed module (`satisfaction_source: contrib_module`).
4. The dependency is satisfied by an explicitly documented alternative implementation.

### Dynamic Wave Dispatching Algorithm
1. The Orchestrator queries `state/migration-state.yml` and the manifest dependency graph.
2. In-degrees are calculated based on unfulfilled dependencies.
3. Components with 0 unfulfilled dependencies transition to `READY` and are batched into `wave_{N}`.
4. Specialists execute the wave. When complete:
   - Orchestrator updates resolved dependencies.
   - Newly eligible components transition from `DEFERRED` to `READY` and form `wave_{N+1}`.
5. If a component transitions to `BLOCKED`:
   - Orchestrator traverses the downstream DAG.
   - All transitive dependents transition to `BLOCKED_UPSTREAM`.
   - Independent components continue execution uninterrupted.

---

## 5. Parallelism & Concurrency Serialization Gates

### Safe Parallel Work (Concurrently Executable)
- Independent components in the same dynamic wave with strictly disjoint target file sets and zero shared configuration keys.
- Contrib module evaluation alongside custom module discovery.
- Static theme asset conversion alongside independent custom module migrations.

### Mandatory Serialization Rules
Parallel execution is strictly **PROHIBITED** and must be serialized whenever agents may concurrently modify:
1. **Shared Files**: Modifying the same `.services.yml`, `.routing.yml`, `.permissions.yml`, or `.module` file.
2. **Shared Configuration**: Modifying identical CMI configuration objects (e.g. `system.site.yml` or shared field storage).
3. **Database Schemas & Data Pipelines**: Running entity schema generation and Migration API pipeline execution concurrently.
4. **Shared State Records**: Concurrently mutating global `migration-state.yml` without an atomic merge lock.

---

## 6. Idempotency & Safe Resumption Protocol

The framework is strictly **idempotent and resumable**. When an interrupted migration resumes:
1. **State Audit**: Orchestrator reads `state/migration-state.yml` and verifies `global_block == false`.
2. **Evidence Reconciliation**:
   - Components marked `COMPLETE` or `VALIDATED` are checked for backing evidence artifacts. If evidence exists, they are skipped. If evidence is missing, they are flagged as `EVIDENCE_GAP` and scheduled for revalidation.
   - Components marked `IN_PROGRESS` are inspected against `logs/file-change-log/`. Transient files are assessed, and the component plan is cleanly restarted.
   - Components marked `BLOCKED` or `BLOCKED_UPSTREAM` remain paused unless explicit remediation is recorded.
3. **Wave Recalculation**: Orchestrator recalculates dependency readiness from the current evidence baseline and schedules eligible `READY` components into the next dynamic wave.

---

## 7. The 8 Final Acceptance Audit Gates & Outcome Model

### Final Audit Readiness Condition
The Final Audit Agent executes when **no components remain actively executing**:
```text
Zero components remain in:
- NOT_STARTED
- READY
- IN_PROGRESS
- TESTING
- VALIDATING
```
Remaining components may include `COMPLETE`, `COMPLETE_WITH_GAPS`, `BLOCKED`, `BLOCKED_UPSTREAM`, `DEFERRED`, or `FAILED`.

### The 8 Acceptance Gates
1. **Gate 1 (Discovery & Scope Integrity)**: 100% of discovered D7 assets registered in manifest.
2. **Gate 2 (DAG & Wave Integrity)**: Topological order respected; all dependency requirements satisfied.
3. **Gate 3 (Implementation Accounting)**: Zero components remain in transient or undefined states.
4. **Gate 4 (Component-Appropriate Testing Evidence)**: All completed components possess an applicable and sufficient testing strategy with results recorded.
5. **Gate 5 (Behavioral Parity & Validation)**: 12-dimensional validation matrices generated with empirical evidence.
6. **Gate 6 (Blocker & Exception Accounting)**: All blocked items documented in `reports/blocked/` and consolidated into a post-migration backlog.
7. **Gate 7 (Evidence Sufficiency & Anti-Hallucination)**: Zero unearned `PASS` claims or synthetic passes; all claims backed by observed facts or verified results.
8. **Gate 8 (Audit Log & Boundary Completeness)**: Every modified target file registered in `logs/file-change-log/`; zero writes to D7 source path.

### Final Migration Outcomes
- **`COMPLETE`**: 100% of components reached `COMPLETE`; all 8 gates satisfied with high evidence confidence (`VERIFIED`).
- **`COMPLETE_WITH_GAPS`**: Core migration succeeded; non-blocking gaps approved and documented (`PARTIALLY_VERIFIED`).
- **`BLOCKED`**: Critical blocking failure unresolved; actionable blocker report produced.
- **`INCOMPLETE`**: Migration halted prematurely or required deliverables missing.
