# Agent Communication & Operational Protocol

## 1. Zero-Memory Artifact Handoff & Operational Contract

Agents in this framework operate without reliance on shared conversational memory or implicit context. Every inter-agent handoff is governed by an **Explicit Artifact Contract** and a **Structured Result Payload (`agent_result`)**.

An agent must never assume another agent has run unless the expected filesystem artifact exists, is parseable, and satisfies the defined preconditions.

### Standardized 18-Part Agent Operational Execution Contract

Every agent specification in `agents/*/agent.md` defines:

1. **Identity**: Name, full namespace (`drupal-migration:<name>`), role, and model configuration.
2. **Purpose**: Specific role in the migration lifecycle.
3. **Allowed Scope**: Explicit domains and tasks the agent is authorized to execute.
4. **Forbidden Scope**: Explicit restrictions, anti-patterns, and boundaries.
5. **Read Permissions**: Exact files, paths, databases, and configs authorized for read access.
6. **Write Permissions**: Exact target directories and artifact paths authorized for write access.
7. **Forbidden Writes**: Paths strictly protected against writes (D7 source is ALWAYS read-only).
8. **Conceptual Tool Capabilities**: Least-privilege capabilities (Read, Search, Write, Command Execution, Network, State Access).
9. **Preconditions**: Required previous phase outputs, manifest entries, state fields, and evidence.
10. **Required Inputs**: Manifest data, state data, configs, source code, reference paths.
11. **Skill & Reference Dependencies**: Explicit links to required Skills and References.
12. **Operational Execution Procedure**: Step-by-step deterministic execution workflow.
13. **Decision Rules & Target Version Branching**: Config-driven D10 vs D11 logic, modern API rules.
14. **Artifact & Evidence Outputs**: Markdown reports, code files, configs, evidence logs.
15. **Proposed State Updates**: Proposes transitions using the 15 canonical states from Step 3.
16. **Structured Result Generation**: Generating the canonical `agent_result` payload.
17. **Stop Conditions & Failure Handling**: STOPPED, BLOCKED, ESCALATED, FAILED with stage routing.
18. **Downstream Handoff**: Target receiving agent, trigger conditions, required handoff package.

---

## 2. Single-Writer State Authority & Result-State-Handoff Flow

To maintain strict state consistency without race conditions or partial writes, the **Orchestrator is the single authoritative writer of runtime lifecycle state (`state/migration-state.yml`)**.

Specialist agents observe state, execute scoped work, generate artifacts, and produce an `agent_result` containing a `proposed_to_state` transition. The Orchestrator validates the result and authoritatively commits the state update.

```text
Specialist Agent starts
           │
           ▼
Validates preconditions
           │
           ▼
Performs scoped work (Skills + References)
           │
           ▼
Generates code & evidence artifacts
           │
           ▼
Generates canonical `agent_result` (v1.0)
           │
           ▼
Orchestrator Result Validation Gate (Validates schema, scope, evidence)
           │
           ▼
Orchestrator commits state update to `migration-state.yml`
           │
           ▼
Orchestrator recalculates dynamic waves & dependency readiness
           │
           ▼
Dispatches next eligible Agent
```

---

## 3. Canonical Structured Agent Result Schema (`agent_result` v1.0)

All specialist agents return execution outcomes using the canonical `agent_result` schema:

```yaml
agent_result:
  schema_version: "1.0"
  execution_id: "exec-<COMPONENT>-<DATE>-<SEQ>" # e.g. exec-custom_booking-20260918-001
  attempt_number: 1
  started_at: "2026-09-18T22:30:00Z"
  completed_at: "2026-09-18T22:32:15Z"
  agent_name: "custom-module"
  component_id: "custom_module.custom_booking"
  lifecycle_phase: "phase_4_implementation"
  current_wave: "wave_1"
  execution_status: "SUCCESS" # SUCCESS | BLOCKED | STOPPED | ESCALATED | FAILED
  state_transition:
    from_state: "IN_PROGRESS"
    proposed_to_state: "CODE_COMPLETE"
  outputs:
    code_artifacts:
      - "web/modules/custom/custom_booking/custom_booking.info.yml"
      - "web/modules/custom/custom_booking/src/BookingManager.php"
    report_artifacts:
      - "reports/custom-modules/REPORT-custom_booking.md"
  evidence:
    observed_facts:
      - "Extracted booking calculation rules from custom_booking.module:L45-L89"
    verified_results:
      - "PHPStan static analysis passed at Level 2 with 0 errors"
  blockers: []
  decisions_required: []
  files_changed:
    - path: "web/modules/custom/custom_booking/custom_booking.info.yml"
      operation: "CREATE"
      reason: "Module metadata declaration"
      evidence: "Verified YAML syntax"
  tests:
    status: "TEST_PASSED" # TEST_PASSED | TEST_FAILED | TEST_NOT_APPLICABLE | TEST_UNAVAILABLE | TEST_NOT_EXECUTED
    summary: "Unit tests executed with exit code 0"
  validation:
    status: "PENDING"
  next_action:
    target_agent: "testing"
    recommended_payload: "web/modules/custom/custom_booking"
```

---

## 4. Orchestrator Result Validation Gate

Before committing any proposed state transition to `state/migration-state.yml`, the Orchestrator validates the `agent_result` against 10 strict integrity checks:

1. **Schema Integrity**: `schema_version` is `"1.0"` and all mandatory fields exist.
2. **Agent Authorization**: `agent_name` matches the agent dispatched for this phase and component.
3. **Component In-Scope**: `component_id` is registered and in-scope in `state/migration-manifest.yml`.
4. **Valid State Transition**: `from_state` matches current runtime state; `proposed_to_state` is a valid forward transition in the 15 canonical states.
5. **Write Boundary Compliance**: All paths in `files_changed` fall strictly within the agent's authorized write scope derived from `migration.config.yml`.
6. **Source Immutability (Rule 1 & 2)**: Zero files in `source.path` were touched or modified.
7. **Secret Protection (Rule 10)**: No credentials, tokens, or private keys committed to config or code.
8. **Evidence Citation**: `evidence` cites empirical facts (`[OBSERVED FACT]`, `[VERIFIED RESULT]`, test logs).
9. **Blocker Classification**: If `execution_status` is `BLOCKED` or `STOPPED`, blocker record exists with valid `remediation_stage`.
10. **Target Version Consistency**: Modern code patterns conform to configured `target.core_version`.
11. **Custom Database, Schema, PHP File, Class & `.inc` Accounting Integrity**: For custom module components, all custom database tables, schemas (`hook_schema`), custom PHP source files, OOP classes, interfaces, traits, constructors, methods, and `.inc` files cataloged in discovery must have an explicit outcome status (`MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`) with zero unaccounted or silently omitted functionality.

*On Validation Failure*: The Orchestrator rejects the result, generates an `EVIDENCE_GAP` or `STATE_INCONSISTENCY` blocker, and does NOT commit the proposed state change.

---

## 5. Legacy Custom Database, Schema, Data Model, Legacy Custom PHP File, OOP Class & Legacy `.inc` File Re-engineering Architecture

The factory recursively discovers and re-engineers Legacy Custom Database schemas, database access calls, stored data models, Legacy Custom PHP Files, OOP classes, constructors, interfaces, traits, and Legacy `.inc` Files within Drupal 7 custom modules into modern Drupal 10/11 architectures.

- **Discovery & Schema Analysis**: Discovery recursively inventories all `*.install`, `*.module`, `*.inc`, and `*.php` files, extracting `hook_schema()` definitions, columns, primary keys, indexes, unique constraints, foreign keys, and entity references (`uid`, `nid`, `tid`, `fid`, `entity_id`).
- **Database APIs, Dynamic SQL & Safety**: Inventories `db_query()`, `db_select()`, `db_insert()`, `db_update()`, `db_delete()`, `db_merge()`, `db_transaction()`. Refactors queries into safe parameterized statements (`:placeholder`) or query builders, flagging unresolved dynamic SQL as `[UNVERIFIED RESULT]` / `HUMAN_DECISION_REQUIRED`.
- **17 Data Semantic Categories**: Semantically classifies custom data into `CONTENT`, `CONFIGURATION`, `STATE`, `USER_DATA`, `ENTITY_DATA`, `FIELD_DATA`, `RELATIONSHIP_DATA`, `TRANSACTION_DATA`, `AUDIT_DATA`, `CACHE_DATA`, `QUEUE_DATA`, `TEMPORARY_DATA`, `INTEGRATION_DATA`, `LOOKUP_DATA`, `REFERENCE_DATA`, `LEGACY_DATA`, or `UNKNOWN`.
- **Serialized Data & Transformations**: Identifies PHP serialized payloads (`serialize()` / `unserialize()`), JSON, and encoded objects, defining safe migration transformation pipelines into modern structured formats.
- **Target Architecture & Non-1:1 Mapping**: Re-engineers custom tables and data models into Content Entities (`src/Entity/`), Config Entities, Config API (`config.factory`), State API (`\Drupal::state()`), KeyValue stores, or dedicated Repository Services (`src/Repository/`) with constructor DI (`ConnectionInterface`). Supports one-to-many and many-to-one transformations.
- **10 Migration Data Strategies**: Executes standardized ETL pipelines: `DIRECT_MIGRATION`, `TRANSFORMED_MIGRATION`, `ENTITY_MIGRATION`, `CONFIG_MIGRATION`, `STATE_MIGRATION`, `CUSTOM_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.
- **Zero Omission**: Every custom database table, schema definition, data model, custom PHP file, class, constructor, method, and `.inc` file must be accounted for with verified outcomes before validation sign-off. The states `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, and `SILENTLY_OMITTED` are strictly forbidden.

---

## 6. Artifact Ownership & Permission Matrix

To eliminate write collisions and ambiguous responsibilities, every writable artifact has an explicit Primary Owner, allowed Delegations, and Serialization Rules:

| Writable Artifact / Target Area | Primary Owner Agent | Delegated Agent(s) | Serialization Rule | Read Access |
|:---|:---|:---|:---|:---|
| `state/migration-state.yml` | `orchestrator` | None (Single-Writer) | Strict Single-Writer serialization | All Agents |
| `state/migration-manifest.yml` | `discovery` | None (Static Scope) | Initialized during discovery | All Agents |
| `reports/dependencies/*` (DAG) | `dependency` | None | Owned by dependency agent | All Agents |
| `reports/contrib/*` | `contrib-module` | None | Advisory only; non-destructive | Orchestrator, Custom Module |
| `<target_module_dir>/<MODULE>/*` | `custom-module` | `api-modernization` | Scoped delegation; component lock | Testing, Validation |
| `<target_theme_dir>/<THEME>/*` | `custom-theme` | None | Component locked during wave | Testing, Validation |
| `<target_config_dir>/*` | `configuration` | None | Component locked during wave | Testing, Data Migration |
| `<target_module_dir>/<PROJECT>_migrate/*` | `data-migration` | None | Component locked during wave | Testing, Validation |
| `reports/testing/*` | `testing` | None | Test runner execution | Validation, Orchestrator |
| `reports/validation/*` | `validation` | None | Comparative audit | Final Audit, Orchestrator |
| `reports/final/*` | `final-audit` | None | Gate audit & sign-off | Human Stakeholders |
| `reports/blocked/*` | Originating Agent | Orchestrator | Atomic ticket generation | Orchestrator, Human |
| `logs/file-change-log/*` | Any Modifying Agent | None | Append-only per file mutation | All Agents |

---

## 6. Dynamic Config-Driven Path Resolution

Agents must NEVER assume fixed directories like `web/` or `config/sync`. Target paths are dynamically resolved from `migration.config.yml`:

```yaml
# Dynamic path resolution formulas:
target_base       = config.target.path
target_docroot    = config.target.docroot              # e.g., "web", "docroot", "html", or ""
target_module_dir = config.target.custom_module_dir   # e.g., "{target_base}/{target_docroot}/modules/custom"
target_theme_dir  = config.target.custom_theme_dir    # e.g., "{target_base}/{target_docroot}/themes/custom"
target_config_dir = config.target.config_sync_dir     # e.g., "{target_base}/config/sync"
```

---

## 7. Scoped Delegation Protocol (`custom-module` ↔ `api-modernization`)

1. `custom-module` owns end-to-end modernization of a custom module component.
2. If complex procedural-to-OOP refactoring or service container injection is required, `custom-module` explicitly delegates the scoped service conversion to `api-modernization`.
3. `api-modernization` refactors the service classes, verifies constructor DI, logs changes in `logs/file-change-log/`, and returns an `agent_result` payload to `custom-module`.
4. `custom-module` incorporates the modern services into the module scaffold, completes component implementation, and returns final `agent_result` to the Orchestrator.
5. Both agents must never concurrently modify the same file.

---

## 8. Human Decision Gates & Escalation Protocol

Agents must NOT autonomously assume high-impact business decisions. The following trigger mandatory human escalation via `decision_required`:

```yaml
decision_required:
  decision_id: "DEC-001-BOOKING-PAYMENT"
  question: "Should legacy offline payment gateway be replaced with modern Commerce payment plugin?"
  context: "Legacy custom_booking module implements direct cURL calls to obsolete payment provider."
  evidence: "custom_booking.module:L120-L155 calls discontinued gateway API."
  options:
    - option_id: "A"
      description: "Port legacy cURL logic into custom Drupal 10 Guzzle service."
      impact: "High maintenance; potential security debt."
    - option_id: "B"
      description: "Replace with Drupal Commerce core payment integration."
      impact: "Requires Drupal Commerce dependency; clean architecture."
  agent_recommendation: "Option B"
  human_decision: null
  decision_status: "REQUIRED" # REQUIRED | APPROVED | REJECTED | DEFERRED
```

Execution cannot proceed past a mandatory human gate until `decision_status` is explicitly updated to `APPROVED` or `REJECTED`.

---

## 9. 4-Way Stop Conditions & Execution Statuses

When an agent cannot complete its normal workflow, it must exit with one of 4 explicit statuses:

| Stop Status | Meaning & Cause | Result Payload Status | Target Remediation Stage |
|:---|:---|:---|:---|
| `STOPPED` | Execution halted intentionally because a prerequisite is absent or unsafe | `execution_status: STOPPED` | Originating / Setup Stage |
| `BLOCKED` | A technical dependency, circular coupling, or unmapped entity prevents progress | `execution_status: BLOCKED` | Stage-Aware Remediation Routing |
| `ESCALATED` | A high-impact architectural or business decision requires human input | `execution_status: ESCALATED` | Human Decision Gate |
| `FAILED` | Code syntax error, static analysis failure, or test assertion failure | `execution_status: FAILED` | Originating Implementation Stage |

---


To prevent conflicting claims between reports, state tracking, and manifests, the framework strictly enforces an explicit precedence hierarchy:

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

- **Precedence Rule**: Reports must summarize underlying state and evidence. Reports can **NEVER** override underlying execution evidence.
- **Inconsistency Escalation**: If contradictory claims appear (e.g., an agent summary asserts complete while underlying test evidence shows failure), the Orchestrator or Final Audit agent flags an `EVIDENCE_GAP` or state inconsistency rather than adopting an unverified claim.

---

## 3. Evidence Taxonomy & Anti-Hallucination Standards

Every migration report, plan, and validation artifact must classify assertions using the 6-level **Evidence Taxonomy**:

| Tag | Level | Definition | Verification Requirement |
|:---|:---|:---|:---|
| `[OBSERVED FACT]` | High Confidence | Direct, empirical observation of existing code, schema, config, or directory structure. | Must cite exact file path, line number, or command output. |
| `[INFERENCE]` | Medium-High | Logical deduction derived from multiple observed facts. | Must document the observed premises and deduction chain. |
| `[PROPOSAL]` | Advisory | Recommended architectural design, target pattern, or replacement candidate. | Must state rationale, advantages, and alternative options. |
| `[ASSUMPTION]` | Unverified Baseline | Condition accepted as true without immediate proof to enable planning. | Must state the risk, impact, and verification criteria. |
| `[VERIFIED RESULT]` | Empirical Proof | Action executed with demonstrable, verifiable success. | Must provide terminal output, exit code 0, query checksum, or clean diff. |
| `[UNVERIFIED RESULT]`| Pending Proof | Action performed or claimed without independent verification. | Strictly temporary; cannot be used for `COMPLETE` or `PASS` verdicts. |

### Evidence Requirements by Lifecycle Milestone
- **`DISCOVERED`**: Cites exact D7 relative file path, line count, and entry `.info` file (`[OBSERVED FACT]`).
- **`ANALYZED`**: Cites declared `.info` dependencies and AST hook calls (`[OBSERVED FACT]`).
- **`MIGRATED`**: Target files exist on disk in `target.path`; logged in `logs/file-change-log/` (`[OBSERVED FACT]`).
- **`TESTING` / `VALIDATING`**: Applicable test commands executed and logged with exit code and duration (`[VERIFIED RESULT]`).
- **`COMPLETE`**: Backed by 100% verified test passes or documented limitations and signed off by 12-dimensional validation matrix.

---

## 4. Blocked Work Escalation & Downstream Propagation

The framework strictly distinguishes direct component failures from transitive upstream blockers:

```text
+-------------------------------------------------------------------------+
|                              ISSUE DETECTED                             |
+-------------------------------------------------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
[Safety / Environmental Violation]              [Isolated Component Failure]
          |                                                   |
          v                                                   v
+-------------------------+                       +-------------------------+
| GLOBAL MIGRATION BLOCKED|                       |    COMPONENT BLOCKED    |
+-------------------------+                       +-------------------------+
| 1. Immediate system halt|                       | 1. Generate BLOCKED-XXX |
| 2. Write BLOCKED-000    |                       | 2. Set status: BLOCKED  |
| 3. Set global_block: true                       | 3. Propagate            |
| 4. Await human fix      |                       |    BLOCKED_UPSTREAM to  |
+-------------------------+                       |    dependents           |
                                                  | 4. Continue independent |
                                                  |    components           |
                                                  +-------------------------+
```

### Tier 1: Component Blocked (`BLOCKED`) & Propagation (`BLOCKED_UPSTREAM`)
- **Direct Block (`BLOCKED`)**: A specific component fails during planning, implementation, testing, or validation due to an internal blocker (e.g., missing API, broken calculation).
  1. Generate `reports/blocked/BLOCKED-<COMPONENT>-<NUM>.md` using `templates/blocked-item.md`.
  2. Set component runtime status to `BLOCKED` in `state/migration-state.yml`.
  3. The **Orchestrator** traverses the downstream DAG and marks all direct and transitive dependent components as `BLOCKED_UPSTREAM`.
  4. Independent components with satisfied dependencies continue execution without interruption.

### Tier 2: Global Migration Blocked (`GLOBAL_BLOCK`)
- **Trigger**: Safety violations (attempted write to `source.path`, path overlap, committed credentials, state corruption, unreachable core environment).
  1. Immediately halt all agent execution.
  2. Generate `reports/blocked/BLOCKED-000-GLOBAL.md`.
  3. Set `global_block: true` and `execution_health: BLOCKED` in `state/migration-state.yml`.
  4. Emit high-priority escalation requiring developer remediation before any further execution.

---

## 5. Stage-Aware Remediation Protocol

Remediation is not a blind loop; it returns the component to the exact upstream lifecycle stage appropriate for the failure type:

| Failure Classification | Root Cause Description | Remediation Re-entry Stage |
| :--- | :--- | :--- |
| `SOURCE_AMBIGUITY` | Undocumented business rule or unparseable D7 logic | `DISCOVERY` / `ANALYSIS` |
| `DEPENDENCY_BLOCKER` | Unresolvable circular dependency or unported module | `DEPENDENCY_ANALYSIS` |
| `TARGET_API_GAP` | Missing target Drupal core plugin or architecture | `MIGRATION_PLANNING` |
| `IMPLEMENTATION_FAILURE`| Syntax error or unhandled exception in migrated code | `IN_PROGRESS` |
| `TEST_FAILURE` | PHPUnit assertion failure, PHPStan error, PHPCS issue | `IN_PROGRESS` or `TESTING` |
| `VALIDATION_FAILURE` | Divergence in business calculation, access leak | `IN_PROGRESS` or `VALIDATING` |
| `ENVIRONMENT_FAILURE` | Broken runner binary, missing PHP extension | Environmental Fix -> Re-run |
| `EVIDENCE_GAP` | Missing execution logs or record count proof | Relevant Evidence Stage |

---

## 6. Concurrency & File-Overlap Safety (Serialization Gates)

Parallel execution is permitted **only** when components have strictly disjoint file boundaries and shared state is safely isolated.

### Mandatory Serialization Rules
Parallel execution is strictly **PROHIBITED** and must be serialized whenever agents may concurrently modify:
1. **Shared Files**: Modifying the same `.services.yml`, `.routing.yml`, `.permissions.yml`, or `.module` file.
2. **Shared Configuration**: Exporting identical CMI configuration objects (e.g. `system.site.yml` or shared field storage).
3. **Database Schemas & Data Pipelines**: Running entity schema generation and Migration API pipeline execution concurrently.
4. **Shared State Records**: Concurrently mutating global `migration-state.yml` without an atomic merge lock.

---

## 7. File Change Tracking Protocol

Git commits are disabled by default (`allow_commits: false`). The framework enforces an append-only audit trail for every file operation in `target.path`.

Before an agent writes, modifies, or deletes any file:
1. Validate destination path is strictly within `target.path`.
2. Reject if destination matches or resides within `source.path`.
3. Perform the file modification.
4. Record the entry in `logs/file-change-log/LOG-<TIMESTAMP>.md` using `templates/file-change-log.md`.

---

## 8. Artifact Freshness & Metadata Protocol

Runtime artifacts record explicit lifecycle metadata in their frontmatter or header to enable deterministic freshness validation without external database state:

```yaml
metadata:
  schema_version: "1.0"
  generated_at: "2026-09-18T22:30:00Z"
  source_context_hash: "sha256-..." # Hash of input D7 code or config state
  component_id: "custom_booking"
  producer_agent: "drupal-migration:custom-module"
  artifact_status: "CURRENT" # CURRENT | STALE | INVALID | SUPERSEDED
```

### Artifact State Lifecycle
- **`CURRENT`**: Backing evidence is fresh, inputs are unchanged, and downstream agents may rely on it.
- **`STALE`**: Underlying source code, dependencies, or migration configuration have changed since generation. Orchestrator triggers re-evaluation before downstream consumption.
- **`INVALID`**: Schema validation failed, required sections are missing, or checksum mismatch detected. Agent result is rejected.
- **`SUPERSEDED`**: Replaced by a newer execution attempt (e.g. attempt 2 after remediation).

---

## 9. Human Decision Gate Protocol

The framework strictly distinguishes an AI **System Recommendation** from an authoritative **Human Decision**:

```text
[Specialist Agent] ──(Generates Proposal)──► [MIGRATION-PLAN-*.md]
                                                     │
                                                     ▼
                                     [Human Decision Gate]
                                                     │
               ┌───────────────────────┬─────────────┴─────────────┬───────────────────────┐
               ▼                       ▼                           ▼                       ▼
          [APPROVED]          [CHANGES_REQUESTED]             [REJECTED]               [PENDING]
               │                       │                           │                       │
               ▼                       ▼                           ▼                       ▼
       Orchestrator enters    Agent re-plans with         Component marked        Orchestrator pauses
       Implementation Wave    human feedback              SKIPPED / BLOCKED       component & halts wave
```

### Decision States
- **`PENDING`**: Default state upon plan generation. The Orchestrator **HALTS** downstream code execution for this component until human review is provided.
- **`APPROVED`**: Explicit sign-off by technical lead. Unlocks wave dispatching and code writing.
- **`CHANGES_REQUESTED`**: Plan returned to specialist with human notes for re-planning.
- **`REJECTED`**: Component will not be migrated; marked `SKIPPED` in runtime state.
- **`NOT_APPLICABLE`**: Automated/deterministic transformation requiring no architectural branching.

---

## 10. Safe Resume & Idempotent Re-entry Protocol

When resuming an interrupted or failed migration, the Orchestrator evaluates the recovery scenario deterministically:

- **Case A (Transient Failure / Retryable Component)**: If `attempt_number < max_retries`, re-enters at the component's designated remediation stage without re-running earlier completed phases.
- **Case B (Blocked Dependency)**: Dependent component is placed in `BLOCKED_UPSTREAM`. When upstream is unblocked and reaches `COMPLETE`, Orchestrator transitions dependent to `READY` for the next dynamic wave.
- **Case C (Global Safety Blocker)**: System-wide halt (`global_block: true`). Execution cannot proceed until developer resolves environment/path issue and resets `global_block`.
- **Case D (Unexpected Process Termination)**: Orchestrator inspects `state/migration-state.yml` against `logs/file-change-log/`. Incomplete components in `IN_PROGRESS` are rolled back to `READY` or `PLANNED` based on verified on-disk artifacts.
- **Case E (Resume After Interruption)**: Running `/orchestrate` inspects completed phases and existing valid artifacts, automatically resuming from the lowest incomplete wave without re-executing verified milestones.
- **Case F (Stale Artifact Encountered)**: If input source hash differs from artifact metadata, Orchestrator marks artifact `STALE` and schedules re-execution of the producing agent.

---

## 11. Runtime Capability & Readiness Matrix

| Functional Area | Capability | Verification Level | Runtime Status |
| :--- | :--- | :---: | :---: |
| **Packaging** | Plugin metadata (`plugin.json`, `marketplace.json`) | `STATIC_VERIFIED` | Verified statically |
| **Packaging** | Claude Code runtime loading (`/plugin install`) | `RUNTIME_REQUIRED` | `[RUNTIME UNVERIFIED]` |
| **Commands** | Slash command definition (`/preflight`, `/discover`, `/orchestrate`, `/status`) | `STATIC_VERIFIED` | Verified statically |
| **Commands** | Claude Code command discovery & execution | `RUNTIME_REQUIRED` | `[RUNTIME UNVERIFIED]` |
| **Configuration** | Canonical template & structure (`migration.config.example.yml`) | `STATIC_VERIFIED` | Verified statically |
| **Configuration** | Dynamic consumer path resolution & env variable loading | `CONSUMER_ENVIRONMENT_REQUIRED` | `[RUNTIME UNVERIFIED]` |
| **Agents** | 18-part operational contracts & scope definitions | `STATIC_VERIFIED` | Verified statically |
| **Agents** | Autonomous turn execution & tool sandboxing | `RUNTIME_REQUIRED` | `[RUNTIME UNVERIFIED]` |
| **State Machine** | Single-writer authority & transition matrix | `STATIC_VERIFIED` | Verified statically |
| **State Machine** | Live atomic state updates during dynamic waves | `RUNTIME_REQUIRED` | `[RUNTIME UNVERIFIED]` |
| **Safety** | D7 read-only policy & non-overlap validation | `STATIC_VERIFIED` | Verified statically |
| **Safety** | Live OS filesystem write blocking | `RUNTIME_REQUIRED` | `[RUNTIME UNVERIFIED]` |
| **Full Migration**| End-to-end AST parsing & database replatforming | `CONSUMER_ENVIRONMENT_REQUIRED` | `[RUNTIME UNVERIFIED]` |

> [!NOTE]
> All runtime-required operations remain: `[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]`.

---

## 12. Canonical Failure Taxonomy & Severity Model

To avoid treating disparate operational anomalies as generic failures, the framework classifies all runtime issues into 8 distinct failure classes and 5 standardized severity levels:

### 8 Failure Classes
1. **Agent Failure (`AGENT_FAILURE`)**: Agent returns execution error, malformed `agent_result`, missing mandatory evidence links, or unauthorized state transition proposal.
2. **Tool Failure (`TOOL_FAILURE`)**: Underlying CLI tools (Drush, PHP, PHPUnit, PHPStan) are unavailable, timed out, or return fatal non-zero exit codes.
3. **Dependency Failure (`DEPENDENCY_FAILURE`)**: Upstream component failure, cyclical dependency detected, or required upstream interface artifact missing/invalid.
4. **Configuration Failure (`CONFIG_FAILURE`)**: Missing configuration keys, invalid target version specification, unresolvable paths, or configuration drift.
5. **Safety Failure (`SAFETY_FAILURE`)**: Attempted write to D7 source path, source/target directory overlap, committed secret/credential detected, unauthorized target write scope, or un-serialized shared file collision.
6. **Artifact Failure (`ARTIFACT_FAILURE`)**: Mandatory artifact missing, malformed YAML frontmatter, stale input context hash, superseded artifact consumed as current, or corrupt state file.
7. **Human Gate Failure (`HUMAN_GATE_FAILURE`)**: Plan remains `PENDING` during execution wave, plan `REJECTED`, changes requested without updated plan, or contradictory human inputs.
8. **Process Failure (`PROCESS_FAILURE`)**: Interrupted execution process, unhandled runner termination, partial wave execution abort, or runner restart during active component work.

### 5 Failure Severity Levels
| Severity | Definition & Scope | Immediate Operational Action | Gating / Impact |
|:---|:---|:---|:---|
| `INFO` | Informational diagnostic or benign telemetry event | Log event to report / change log | Execution continues uninterrupted |
| `WARNING` | Non-fatal divergence, fallback mechanism used | Record warning; flag in telemetry | Execution continues; flag in audit |
| `MAJOR` | Single isolated component failure | Route component to remediation stage | Component blocked; independent components continue |
| `CRITICAL` | Transitive failure affecting dependency subtree | Propagate `BLOCKED_UPSTREAM` down DAG | Subtree blocked; requires remediation or human gate |
| `GLOBAL_BLOCK`| Safety rule violation, state corruption, path overlap | Halt all agent execution immediately (`global_block: true`)| Pipeline paused; requires developer remediation |

---

## 13. Deterministic Retry Policy & Recovery Boundaries

### Retry Policy Invariants
1. **Maximum Retries**: Configured via `max_retries` in `migration.config.yml` (default: 3 attempts per component per stage).
2. **Retry Tracking**: Every retry increments `attempt_number` in `agent_result` and `component_states.<id>.attempts`.
3. **Stage-Aware Re-entry**: Retries do NOT restart the entire migration; they re-enter at the designated remediation stage.
4. **Terminal Failure**: Upon exceeding `max_retries`, the component transitions from `FAILED_RETRYABLE` to `BLOCKED` and triggers mandatory human escalation.
5. **Precondition Preservation**: A retry must **NEVER** bypass Preflight, Human Decision Gates, Safety Gates, or Dependency Invariants.
6. **Idempotency Guarantee**: The framework guarantees *safe resume and idempotent re-entry where the underlying operation supports idempotency*.

### Recovery Boundaries
- **Recoverable**: Transient CLI timeout, temporary memory exhaustion, retryable agent syntax error.
- **Remediable**: Missing configuration setting, missing upstream module, human-requested architectural adjustment.
- **Non-Recoverable Without Human Intervention**: Corrupted authoritative state, source modification attempt, security violation.
- **Rollback Boundary**: The factory does *NOT* claim automatic rollback of arbitrary Drupal database or code mutations. Rollback is governed by inspecting the append-only `logs/file-change-log/` audit trail and performing controlled file-reversion or snapshot restoration.

---

## 14. Partial Wave Failure & Interruption Reconciliation

### Partial Wave Failure Handling
When components in an active dynamic execution wave complete with mixed results:
$$\text{Wave } N: \quad [A \rightarrow \text{COMPLETE}, \quad B \rightarrow \text{FAILED}, \quad C \rightarrow \text{COMPLETE}, \quad D \rightarrow \text{READY}]$$
1. Completed components ($A, C$) remain `COMPLETE` and are never blindly re-executed.
2. Failed component ($B$) enters `FAILED_RETRYABLE` (if attempts remain) or `BLOCKED`.
3. Direct and transitive dependents of $B$ are marked `BLOCKED_UPSTREAM`.
4. Independent components ($D$) proceed to execution if all upstream dependencies are satisfied.
5. Orchestrator recalculates DAG readiness dynamically.

### Interruption Reconciliation Matrix
If execution is interrupted (e.g. SIGINT, crash, runner timeout):
- **Before agent begins**: Component status remains `READY`; dispatched on resume.
- **During agent execution**: Component was left in `IN_PROGRESS`. On resume, Orchestrator inspects disk against `logs/file-change-log/` and reconciles status to `READY` or `FAILED_RETRYABLE`.
- **After target writes but before `agent_result`**: Uncommitted changes are verified against file logs; incomplete modifications are reverted or scheduled for re-execution.
- **After `agent_result` written but before state commit**: Orchestrator detects persisted result artifact, executes validation gate, and commits authoritative state.
- **After state commit but before next wave dispatch**: Orchestrator reloads state, computes next topological wave, and continues execution.

---

## 15. State Corruption Fail-Safe Protocol

If `state/migration-state.yml` is missing, unparseable, incomplete, or internally contradictory:
1. **Fail-Safe Halt**: Trigger immediate `GLOBAL_BLOCK` (`global_block: true`, `execution_health: CORRUPTED_STATE`).
2. **Preserve Evidence**: Copy corrupted state file to `logs/state-corruption-<TIMESTAMP>.yml` for diagnosis.
3. **No Blind Overwrite**: The framework will **NEVER** silently overwrite or guess state without verification.
4. **Human Escalation**: Request developer inspection.
5. **Reconciliation**: State is reconstructed deterministically by scanning:
   - `state/migration-manifest.yml` (Scope & Inventory)
   - `reports/` (Completed milestone reports)
   - `logs/file-change-log/` (Verified file modifications)
6. **Resume After Validation**: Pipeline resumes only after reconstructed state passes full schema validation.

---

## 16. Deterministic Safe Resume Algorithm

When `/orchestrate` is executed on an existing migration workspace, it executes the following deterministic 9-step algorithm:

```text
Step 1: Load and parse migration.config.yml
Step 2: Validate state file (state/migration-state.yml) schema and integrity
Step 3: Verify required artifacts (reports, manifest, DAG) and check freshness
Step 4: Verify global safety conditions (D7 read-only check, path overlap check, global_block == false)
Step 5: Reconcile incomplete components (reconcile IN_PROGRESS to READY / FAILED_RETRYABLE)
Step 6: Load canonical dependency DAG and evaluate upstream statuses
Step 7: Verify human decision gates (ensure zero PENDING gates in candidate wave)
Step 8: Calculate executable topological wave (in-degree 0 among uncompleted, unblocked components)
Step 9: Dispatch only eligible, verified components to specialist agents
```

---

## 17. Production Safety Checklist

### Phase 1: Pre-Execution Gate
- [ ] Preflight status is `PASS` with zero blocking errors.
- [ ] Source path (`source.path`) and target path (`target.path`) are strictly non-overlapping.
- [ ] Source Drupal 7 codebase is verified read-only and unmounted from write permissions.
- [ ] No API keys, passwords, or tokens are present in configuration or reports.
- [ ] Migration scope is finalized in `state/migration-manifest.yml`.
- [ ] Dependency DAG is acyclic and verified.

### Phase 2: Runtime Wave Execution Gate
- [ ] Orchestrator remains the sole authoritative writer of `migration-state.yml`.
- [ ] Write permissions strictly match individual agent authorized scopes.
- [ ] Shared file modifications are serialized to prevent race conditions.
- [ ] All file mutations are recorded in `logs/file-change-log/` prior to disk write.
- [ ] Failed components are isolated; downstream dependents marked `BLOCKED_UPSTREAM`.
- [ ] Retry counters are enforced with strict thresholds (`max_retries`).

### Phase 3: Post-Interruption Recovery Gate
- [ ] State file integrity verified against schema and file change logs.
- [ ] Unfinished components reconciled from `IN_PROGRESS`.
- [ ] Stale artifacts identified and marked for regeneration.
- [ ] Human decision gates re-checked before dispatching next wave.
- [ ] Dynamic wave scheduler computes lowest incomplete wave without repeating completed work.

### Phase 4: Final Sign-Off Gate
- [ ] Zero active `GLOBAL_BLOCK` or safety violations.
- [ ] Zero unresolved component blockers (`BLOCKED` or `BLOCKED_UPSTREAM`).
- [ ] 100% of in-scope manifest components resolved to `COMPLETE` or approved `SKIPPED`.
- [ ] Automated tests executed with verified `TEST_PASSED` results.
- [ ] 12-dimensional behavioral validation completed with zero unhandled discrepancies.
- [ ] Final audit report signed off and archived.
