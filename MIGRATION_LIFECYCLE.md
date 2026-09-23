# Migration Lifecycle & Recursive Execution Model

## 1. Lifecycle Philosophy

The Drupal 7 to Drupal 10/11 migration framework follows a **recursive, evidence-driven, dynamic execution lifecycle**. Rather than assuming an immutable linear pass, the framework implements iterative analysis, automated remediation of fixable gaps, recursive dependency resolution, and strict human decision gates.

### Core Lifecycle Axioms:
1. **Evidence-Driven Completion**: A component is `COMPLETE` **only** when empirical evidence proves all material functional requirements are migrated, replaced, superseded, obsolete, or explicitly excluded with justification.
2. **"Implemented" ≠ "Complete"**: Writing PHP files or passing static linters does not constitute migration completeness.
3. **Recursive Dependency Resolution**: When a target component is requested, the framework recursively analyzes, orders, and resolves its upstream custom dependencies before implementing the parent task.
4. **Task-Level Recursion**: Missing or partially implemented items identified during audits are decomposed into discrete, stable remediation tasks (`TASK_ID`), fixed, and re-audited iteratively.
5. **Three-Branch Remediation Gate**:
   - **Fixable from Evidence** $\rightarrow$ Automatically remediate and re-audit.
   - **Requires Human Decision** $\rightarrow$ Halt with `HUMAN_INTERVENTION_REQUIRED` (never invent business logic).
   - **Runtime Unavailable** $\rightarrow$ Mark `RUNTIME_UNVERIFIED` and proceed with static verification without false completion claims.

---

## 2. Target Recursive Architecture

```
                       USER REQUEST
                            ↓
               COMMAND (/orchestrate [target])
                            ↓
                      TASK ANALYSIS
                            ↓
                  DEPENDENCY DISCOVERY
                            ↓
             RECURSIVE DEPENDENCY RESOLUTION
                            ↓
                  SPECIALIST EXECUTION
                            ↓
                   EVIDENCE COLLECTION
                            ↓
                     ANALYSIS REPORT
                            ↓
            COMPLETENESS & QUALITY ASSESSMENT
                            ↓
                    CLASSIFY EACH ITEM
                            ↓
        ┌───────────────────────────────────────┐
        │ COMPLETE                              │
        │ PARTIAL                               │
        │ MISSING                               │
        │ BLOCKED                               │
        │ HUMAN_INTERVENTION_REQUIRED           │
        │ RUNTIME_UNVERIFIED                    │
        │ SUPERSEDED                            │
        │ REPLACED                              │
        │ OBSOLETE                              │
        │ EXCLUDED                              │
        └───────────────────────────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
[FIXABLE FROM EVIDENCE] [REQUIRES HUMAN DECISION] [RUNTIME UNAVAILABLE]
       │                    │                    │
  REMEDIATION PLAN    HUMAN_INTERVENTION_REQUIRED RUNTIME_UNVERIFIED
       │                    │                    │
  IMPLEMENT FIX            STOP            Continue Static Work
       │                    │                    │
   RE-ANALYZE        Decision Supplied     Runtime Test Later
       │                    │
  RE-VALIDATE             RESUME
       │
STILL HAS MATERIAL GAPS?
     ↙          ↘
   YES           NO
    ↓             ↓
RECURSIVE LOOP  COMPLETE
```

---

## 3. Canonical Lifecycle Phases

```text
INITIALIZED
    ↓
DISCOVERY
    ↓
DEPENDENCY_ANALYSIS
    ↓
MIGRATION_PLANNING
    ↓
WAVE_EXECUTION / TARGETED EXECUTION
    ↓
TESTING (Component QA & Static Analysis)
    ↓
BEHAVIORAL_VALIDATION (Comparative Auditing)
    ↓
REMEDIATION_LOOP (Iterative Gap Fixes & Re-auditing)
    ↓
FINAL_AUDIT (Acceptance Gates)
    ↓
COMPLETED (or COMPLETED_WITH_GAPS)
```

---

## 4. Canonical Component Status Model

A standardized vocabulary governs component lifecycles in `state/migration-state.yml`:

```text
                      NOT_STARTED
                           │
                           ▼
                       DISCOVERED
                           │
                           ▼
                        ANALYZED
                           │
               ┌───────────┴───────────┐
               ▼                       ▼
             READY                  DEFERRED
          (Deps met)              (Deps pending)
               │                       ▲
               ▼                       │
          IN_PROGRESS ◄────────────────┼──────── (Dependencies unblocked)
               │                       │
               ├───────────────────────┴────────► BLOCKED_UPSTREAM
               │                                   (Upstream unmigrated)
               ▼
            MIGRATED ◄──────────────────────────┐
               │                                │
               ▼                                │
            TESTING ◄───────────────────┐       │
               │                        │       │
               ▼                        │       │
           VALIDATING                   │       │
               │                        │       │
      ┌────────┴────────┬───────────────┤       │
      ▼                 ▼               ▼       │
   VALIDATED         PARTIAL         FAILED     │
      │                 │               │       │
      │                 └─────────► REMEDIATING ┤ (Iterative Fix Loop)
      │                                 ▲       │
      ├─────────────────────────────────┘       │
      ▼                                         │
   COMPLETE / COMPLETE_WITH_GAPS                │
      │                                         │
      ├─────────────────────────────────────────┼──► HUMAN_INTERVENTION_REQUIRED
      │                                         │     (Awaiting Human Input)
      ▼                                         │
   BLOCKED ─────────────────────────────────────┘
```

---

## 5. Recursive Dependency Resolution & Sub-DAG Ordering (Single-Module Execution Mode)

### Sub-DAG Topological Scheduler
When a specific module or task is requested (e.g. `/orchestrate custom_booking` or `/migrate-module custom_booking` in Single-Module Execution Mode):

1. **Dependency Extraction**: The Orchestrator inspects the module's declared and implicit dependencies from `state/migration-manifest.yml`.
2. **Sub-DAG Construction**: Builds the recursive ancestor set:
   $$\text{Ancestors}(M) = \{M\} \cup \text{TransitiveAncestors}(M)$$
3. **Cycle Detection & Blocker Emission**: Performs Depth-First Search (DFS) topological sort with cycle detection. If a cyclic dependency is found (e.g., $A \rightarrow B \rightarrow A$):
   - If resolvable via service decoupling, schedules decoupling.
   - If architectural deadlock occurs, marks both modules `BLOCKED` with ticket `BLOCKED-CYCLE-001.md` and halts.
4. **Bottom-Up Execution**: Upstream dependencies with in-degree 0 are scheduled and executed first.
5. **Dependency Validation**: Each upstream dependency is validated and transitioned to `COMPLETE` or `VALIDATED`.
6. **Parent Task Dispatch**: Once all dependencies are satisfied, the parent task is dispatched.

---

## 6. Architectural Replacement Detection & Behavioral Remediation Cycle

When a legacy subsystem has been replaced by a modern target architecture (e.g. legacy procedural group/community subsystem $\to$ modern entity/access architecture):

```text
SOURCE SUBSYSTEM
       ↓
ARCHITECTURAL REPLACEMENT DISCOVERY (Evidence from composer.json, installed modules, custom classes)
       ↓
BEHAVIORAL DECOMPOSITION (Extract discrete source behaviors)
       ↓
INSPECT EXISTING TARGET IMPLEMENTATION (Extend existing target code; avoid duplicate classes)
       ↓
BEHAVIORAL MAPPING & GAP AUDIT (Classify 10 canonical statuses)
       ↓
EMIT STRUCTURED REMEDIATION TASKS (Stable IDs, YAML LLM remediation input)
       ↓
IMPLEMENT & VALIDATE BEHAVIORAL PARITY (Kernel assertions, access checks, cache invalidation)
       ↓
RE-AUDIT & CONVERGENCE (Loop 1..3 until COMPLETE or escalated)
```

---

## 7. Task-Level Recursion & Iterative Remediation

Within an individual component migration:

1. **Initial Audit**: Forensic comparison of D7 source vs D10 target across 12 dimensions.
2. **Gap Classification**: Every gap is assigned one of the 10 canonical statuses.
3. **Remediation Task Generation**:
   - Each fixable gap receives a stable ID (e.g. `CUSTOM-BOOKING-ROUTE-001`, `CUSTOM-BOOKING-SERVICE-004`).
   - Tasks are compiled in the report's `## LLM REMEDIATION INPUT` section.
4. **Execution & Targeted Re-validation**:
   - The specialist agent applies the fix.
   - Targeted unit/kernel tests and static checks re-run against the modified artifact.
5. **Re-audit & Convergence Check**:
   - Re-evaluates completeness.
   - If material gaps remain and the retry/iteration budget is not exhausted, loops back to Step 1.
   - If all material items are `COMPLETE`, `SUPERSEDED`, `REPLACED`, `OBSOLETE`, or `EXCLUDED`, marks component `COMPLETE`.
   - If non-material gaps remain and are accepted, marks component `COMPLETE_WITH_GAPS`.

---

## 8. Loop Prevention & Guardrails

To prevent unbounded execution loops:

- `max_remediation_iterations: 3`: Maximum number of remediation cycles per module.
- `max_retries_per_component: 2`: Maximum attempts to fix a single failing component.
- `dependency_cycle_detection`: Strict DFS check emitting `BLOCKED-CYCLE-XXX.md`.
- `human_decision_gate`: Immediate halt on `HUMAN_INTERVENTION_REQUIRED` with prompt in `reports/human_decisions/`.

| Guardrail | Default Threshold | Configuration Key | Action on Breach |
|:---|:---:|:---|:---|
| **Max Remediation Iterations** | `max_remediation_iterations: 3` | `agents.max_remediation_iterations` | Halts loop, generates `GAP_ANALYSIS`, sets `COMPLETE_WITH_GAPS` or `BLOCKED`. |
| **Max Retries Per Component** | `max_retries_per_component: 2` | `agents.max_retries_per_component` | Marks component `FAILED` / `BLOCKED`. |
| **Dependency Cycle Detector** | Strict DFS check | Core engine | Halts on cycle with `BLOCKED-CYCLE-XXX.md`. |
| **Human Decision Gate** | Immediate Halt | `agents.require_human_gate` | Sets `HUMAN_INTERVENTION_REQUIRED`, halts, logs prompt in `reports/human_decisions/`, resumes after decision. |
| **D7 Read-Only Monitor** | 0 file mutations | Core safety rule | Immediate `SAFETY_VIOLATION` global halt. |
| **Target Path Isolation** | Component folder | Core safety rule | Rejects any write outside `<target_path>/<MODULE>/`. |

---

## 8. Idempotency & Resumption Protocol

1. **State Audit**: Reads `state/migration-state.yml` and verifies `global_block == false`.
2. **Evidence Reconciliation**:
   - Components marked `COMPLETE` or `VALIDATED` with existing backing reports are skipped.
   - Components marked `IN_PROGRESS` or `REMEDIATING` resume at their lowest incomplete step.
   - Components marked `HUMAN_INTERVENTION_REQUIRED` check if a human decision file exists in `reports/blocked/DECISION-<ID>.md` or `reports/human_decisions/`; if provided, transitions back to `IN_PROGRESS` and resumes.
3. **Wave / Task Recalculation**: Resumes dynamic execution from the updated state baseline.
