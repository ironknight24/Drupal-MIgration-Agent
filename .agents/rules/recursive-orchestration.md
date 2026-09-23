# Rule: Recursive Orchestration & Dependency DAG

## 1. Global Workspace Orchestration (`/orchestrate`)
- Dynamically schedules execution batches (`wave_0`, `wave_1`, ... `wave_N`) derived from dependency in-degrees.
- Components with in-degree 0 (no unmigrated custom dependencies) are dispatched in parallel where file sets are disjoint.
- **Specialist Dispatch & Inline Fallback**: When delegating tasks to specialist roles (`discovery`, `custom-module`, `testing`, `validation`), the Orchestrator uses subagent workers if supported, or executes the specialist protocol inline if subagent delegation is unavailable.
- Shared file mutations (`.services.yml`, `.routing.yml`) and schema alterations are strictly serialized.
- Advances waves iteratively until all workspace components reach terminal states (`COMPLETED`, `BLOCKED`, `SKIPPED`).

## 2. Targeted Recursive Module Orchestration (`/orchestrate <MODULE>` or `/migrate-module <MODULE>`)
When a specific module `<MODULE>` is targeted:
1. **Target Validation**: Verify `<MODULE>` exists in `state/migration-manifest.yml`.
2. **Sub-DAG Construction**: Construct the recursive ancestor sub-DAG:
   $$\text{Ancestors}(M) \cup \{M\}$$
   including coupled external Drupal-integrated code items.
3. **Cycle Detection**: Run DFS cycle detection. If circular dependencies occur (e.g. $A \to B \to A$), emit `BLOCKED-CYCLE-XXX.md` and pause.
4. **Bottom-Up Topological Execution**:
   - For every unmigrated upstream dependency $D$, recursively execute migration and validation before initiating $<MODULE>$.
   - If $D$ is blocked, mark $<MODULE>$ as `BLOCKED_UPSTREAM` and halt cleanly.
5. **Scoped Migration**: When all dependencies are satisfied, migrate $<MODULE>$ within its isolated target directory.
6. **Iterative Remediation**: Run comparative completeness audit across 12 dimensions, remediating fixable gaps iteratively.

## 3. Idempotency & Resumption Protocol
- Running an orchestration workflow repeatedly must be idempotent: existing valid target code is preserved and reconciled rather than blindly overwritten.
- Interrupted runs resume from the last recorded state in `state/migration-state.yml`.

## 4. Reference
- Detailed specifications: [MIGRATION_LIFECYCLE.md](../../MIGRATION_LIFECYCLE.md) and [skills/dependency-analysis/SKILL.md](../../skills/dependency-analysis/SKILL.md)
