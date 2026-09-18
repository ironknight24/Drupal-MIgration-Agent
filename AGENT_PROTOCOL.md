# Agent Communication & Operational Protocol

## 1. Zero-Memory Artifact Handoff

Agents in this framework operate without reliance on shared conversational memory or implicit context. Every inter-agent handoff is governed by an **Explicit Artifact Contract**.

An agent must never assume another agent has run unless the expected filesystem artifact exists, is parseable, and satisfies the defined preconditions.

### Standard Handoff Contract Format

Every agent specification in `agents/*/agent.md` defines:

1. **Preconditions**: Environmental conditions that must evaluate to `TRUE` before execution begins.
2. **Inputs**: Specific markdown, YAML, or code artifacts consumed as input.
3. **Outputs**: Specific structured reports, code files, or state updates produced.
4. **Postconditions**: Invariants that must be verified before the agent marks its task complete.
5. **Failure / Blocked Conditions**: Explicit triggers for halting execution or raising a `BLOCKED-XXX` ticket.

---

## 2. Evidence Taxonomy & Anti-Hallucination Standards

To eliminate speculative or ungrounded assertions, every migration report, plan, and validation artifact must explicitly classify claims using the following 6-level **Evidence Taxonomy**:

| Tag | Level | Definition | Verification Requirement |
|:---|:---|:---|:---|
| `[OBSERVED FACT]` | High Confidence | Direct, empirical observation of existing code, schema, config, or directory structure. | Must cite exact file path, line number, or command output. |
| `[INFERENCE]` | Medium-High | Logical deduction derived from multiple observed facts. | Must document the observed premises and deduction chain. |
| `[PROPOSAL]` | Advisory | Recommended architectural design, target pattern, or replacement candidate. | Must state rationale, advantages, and alternative options. |
| `[ASSUMPTION]` | Unverified Baseline | Condition accepted as true without immediate proof to enable planning. | Must state the risk, impact, and verification criteria. |
| `[VERIFIED RESULT]` | Empirical Proof | Action executed with demonstrable, verifiable success. | Must provide terminal output, exit code 0, or clean diff. |
| `[UNVERIFIED RESULT]`| Pending Proof | Action performed or claimed without independent verification. | Strictly temporary; cannot be used for `PASS` verdicts. |

### Strict Prohibitions

1. **No Phantom Elements**: Never claim a D7 hook, function, schema, or variable exists without viewing the actual file or schema definition.
2. **No Assumed Compatibility**: Never claim a contributed module or library is D10-compatible without citing Packagist release data, Drupal.org documentation, or a verified codebase inspection.
3. **No Unearned Completion**: Never mark a component `completed` in `migration-manifest.yml` without generating an implementation report, test results, and validation matrix.
4. **No Synthetic Test Passage**: Never claim tests passed unless a test command was executed and produced an exit code of 0.
5. **No Data Assumptions**: Never claim records migrated successfully without verifying source vs. destination counts and field values.

---

## 3. Blocked Work Escalation Protocol

When an agent encounters an unresolvable issue, it must never silently abort or guess a dangerous workaround. It categorizes the issue into one of two tiers:

```
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
| 2. Write BLOCKED-000    |                       | 2. Set status: blocked  |
| 3. Set global_block: true                       | 3. Find non-dependent   |
| 4. Await human fix      |                       |    tasks and continue   |
+-------------------------+                       +-------------------------+
```

### Tier 1: Component Blocked
- **Trigger**: A specific custom module contains untangled dependencies, a missing contrib equivalent, or ambiguous legacy business rules.
- **Action**:
  1. Generate `reports/blocked/BLOCKED-<COMPONENT>-<NUM>.md` using `templates/blocked-item.md`.
  2. Mark the component `status: blocked` in `state/migration-manifest.yml`.
  3. Mark downstream dependent components as `blocked_upstream`.
  4. Query the Dependency Agent for independent components with zero unmet dependencies and continue execution.

### Tier 2: Global Migration Blocked
- **Trigger**: 
  - Detection of path overlap between `source.path` and `target.path`.
  - Attempted write operation targeting `source.path`.
  - Corrupted or unparseable `migration-state.yml` or `migration-manifest.yml`.
  - Failure of fundamental database connectivity or broken target web root.
- **Action**:
  1. Immediately halt all agent execution.
  2. Generate `reports/blocked/BLOCKED-000-GLOBAL.md`.
  3. Set `global_block: true` in `state/migration-state.yml`.
  4. Emit a high-priority alert for human developer intervention.

---

## 4. File Change Tracking Protocol

Git commits are disabled by default (`allow_commits: false`). Therefore, the framework enforces an append-only audit trail for every file operation in `target.path`.

Before an agent writes, modifies, or deletes any file:
1. Validate destination path is strictly within `target.path`.
2. Reject if destination matches or resides within `source.path`.
3. Perform the file modification.
4. Record the entry in `logs/file-change-log/LOG-<TIMESTAMP>.md` using `templates/file-change-log.md`.

Required Entry Schema:
- **Timestamp**: ISO 8601 UTC timestamp.
- **Agent**: Responsible agent identifier.
- **Action**: `CREATED` | `MODIFIED` | `DELETED` | `RENAMED`.
- **Target File**: Relative path within `target.path`.
- **Source D7 Reference**: Originating D7 file(s).
- **Rationale**: Clear explanation of the architectural change.
- **Diff / Summary**: Unified diff or structural summary of changes.
