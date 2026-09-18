# Agent Communication & Operational Protocol

## 1. Zero-Memory Artifact Handoff & Contract Schema

Agents in this framework operate without reliance on shared conversational memory or implicit context. Every inter-agent handoff is governed by an **Explicit Artifact Contract**.

An agent must never assume another agent has run unless the expected filesystem artifact exists, is parseable, and satisfies the defined preconditions.

### Standardized 7-Part Agent Handoff Contract

Every agent specification in `agents/*/agent.md` defines:

1. **Preconditions**: Environmental conditions, file existence checks, and upstream phase requirements that must evaluate to `TRUE` before execution begins.
2. **Inputs**: Specific markdown reports, YAML manifests, code files, or configuration artifacts consumed.
3. **Outputs**: Concrete structured reports, code files, or state updates produced.
4. **State Updates**: Explicit fields and records modified in `state/migration-state.yml` (runtime status) and `state/migration-manifest.yml` (scope metadata).
5. **Downstream Handoff**: Next specialized agent(s) or workflow dispatch targets receiving the generated artifacts.
6. **Blockers & Escalation Criteria**: Explicit triggers for halting execution or raising a `BLOCKED-XXX` ticket.
7. **Evidence Requirements**: Mandatory empirical proofs (`[OBSERVED FACT]`, `[VERIFIED RESULT]`, terminal logs, count queries) required before claiming completion.

---

## 2. Source of Truth Hierarchy

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
