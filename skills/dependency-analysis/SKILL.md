---
name: dependency-analysis
description: Dependency Graph Solver & Wave Scheduling Playbook. Analyzes inter-module couplings, custom PHP class instantiations, .inc function call trees, constructs migration DAGs, detects cycles, and generates dynamic execution waves.
version: 1.2.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Dependency Analysis & Wave Scheduling Skill

## Overview
This skill provides the procedural playbook and algorithms for discovering code, schema, lifecycle, custom PHP class instantiations, and legacy `.inc` function couplings across legacy Drupal 7 components. It constructs a Directed Acyclic Graph (DAG), detects circular dependencies, and organizes components into executable topological waves.

---

## Technical References
- [Drupal 7 Core APIs Reference](../../references/drupal-7/apis.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)

---

## 5-Dimensional Coupling Detection Heuristics

To establish an accurate DAG, inspect source assets across 5 distinct coupling vectors:

### 1. Declared Dependencies
- Parse `dependencies[]` declarations in source `.info` files (`[OBSERVED FACT]`).
- Distinguish core module dependencies (`dependencies[] = taxonomy`) from contrib/custom dependencies.

### 2. Implicit Hook, Function & Class Couplings
- Search for inter-module function calls, class instantiations, and hook invocations across `.module`, `.php`, and `.inc` files:
  - `module_invoke('{target_module}', ...)`
  - `module_invoke_all('{hook}')`
  - `drupal_alter('{hook}', ...)`
  - Direct calls to functions defined in another custom module's `.inc` or `.module` files.
  - Cross-module class instantiations (`new OtherModuleClass()`, `new \Namespace\OtherClass()`) and static calls (`OtherModuleClass::method()`).
  - Trace whether the called function/class represents a public service candidate or an internal private helper to avoid creating false dependency edges.

### 3. Database & Schema Couplings
- Inspect `hook_schema()` declarations, table ownership, and queries across all module source files:
  - Module-to-table and cross-module table dependencies: trace `module -> table`, `class -> table`, `service -> table`, `form -> table`, `controller -> table`, `queue -> table`, `cron -> table`, `Drush -> table`.
  - Foreign keys pointing to tables owned by other custom or core modules.
  - Cross-module joins and queries (`db_query`, `db_select`, `db_insert`, `db_update`, `db_delete`) where module A mutates or queries tables defined by module B.
  - Shared junction tables and entity reference columns (`uid`, `nid`, `tid`, `fid`, `entity_id`).

### 4. Presentation & Theme Couplings
- Identify custom theme templates (`.tpl.php`) or preprocess functions invoking custom module APIs.
- Custom modules that provide default themes or template suggestions via `hook_theme()`.

### 5. Data Migration Hierarchy & Database Ordering Couplings
- Relational entity and custom table hierarchies where dependent data cannot be migrated before parent entities:
  - Roles & Permissions $\rightarrow$ Users
  - Users $\rightarrow$ Taxonomy Vocabularies $\rightarrow$ Taxonomy Terms
  - Files / Managed Media $\rightarrow$ Content Types & Custom Entities
  - Custom Entities $\rightarrow$ Relationship Junction Tables
  - Entities $\rightarrow$ Custom Dependent Database Records $\rightarrow$ Serialized Payloads $\rightarrow$ Revisions & Comments
- Circular database dependencies must be detected, flagged, and mapped to two-pass migration pipelines (stubbing references in pass 1, populating relations in pass 2).

---

## Directed Acyclic Graph (DAG) Construction & Cycle Resolution

### Topological Sort Algorithm
1. Compute in-degrees for all components in the manifest based on real architectural dependencies.
2. Identify root leaf nodes (in-degree = 0, no custom dependencies).
3. Sequentially resolve dependencies, assigning components to progressive execution waves.

### Circular Dependency Resolution Strategy
When a cycle is detected ($A \to B \to A$):
1. **Analyze Interface Coupling**: Determine if the cycle is caused by an implicit hook alter, utility function, or circular class instantiation.
2. **Refactor / Extract Shared Service**: Propose extracting the shared functionality into a standalone Wave 0 utility service.
3. **Escalate Blocker**: If the cycle cannot be decoupled without modifying source code, raise a `BLOCKED-DEP-CYCLIC-<MODULES>.md` ticket.

---

## Execution Wave Formation Model

Components are scheduled into ordered execution waves:

| Wave | Category | Description | Criteria |
| :---: | :--- | :--- | :--- |
| **Wave 0** | **Foundation** | Core configuration entities, base utility services, independent schemas. | 0 custom dependencies. |
| **Wave 1** | **Leaf Modules** | Custom modules with zero custom dependencies (depend only on core or ready contrib). | All dependencies satisfied in Wave 0. |
| **Wave 2** | **Intermediate Modules** | Custom modules that depend strictly on Wave 1 modules. | All upstream custom modules completed. |
| **Wave 3** | **Data Pipelines** | Migration API configurations transferring entities into established D10 schemas. | Target entities & fields exist in D10. |
| **Wave 4** | **Complex Integrations** | Webhooks, third-party sync, cross-module business workflows. | Core module services operational. |
| **Wave 5** | **Presentation Layer** | Themes, Twig templates, UI asset libraries. | Final entity render structures finalized. |
