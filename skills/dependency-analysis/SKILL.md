---
name: dependency-analysis
description: Dependency Graph Solver & Wave Scheduling Playbook. Analyzes inter-module couplings, constructs migration DAGs, detects cycles, and generates dynamic execution waves.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Dependency Analysis & Wave Scheduling Skill

## Overview
This skill provides the procedural playbook and algorithms for discovering code, schema, and lifecycle couplings across legacy Drupal 7 components. It constructs a Directed Acyclic Graph (DAG), detects circular dependencies, and organizes components into executable topological waves.

---

## Technical References
- [Drupal 7 Core APIs Reference](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-7/apis.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-7/hooks.md)

---

## 5-Dimensional Coupling Detection Heuristics

To establish an accurate DAG, inspect source assets across 5 distinct coupling vectors:

### 1. Declared Dependencies
- Parse `dependencies[]` declarations in source `.info` files (`[OBSERVED FACT]`).
- Distinguish core module dependencies (`dependencies[] = taxonomy`) from contrib/custom dependencies.

### 2. Implicit Hook & Function Couplings
- Search for inter-module function calls and hook invocations:
  - `module_invoke('{target_module}', ...)`
  - `module_invoke_all('{hook}')`
  - `drupal_alter('{hook}', ...)`
  - Direct calls to functions defined in another custom module's namespace.

### 3. Database & Schema Couplings
- Inspect `hook_schema()` declarations in `.install` files:
  - Foreign keys pointing to tables owned by other modules.
  - Direct queries (`db_query`, `db_select`) joining or updating tables belonging to external modules.

### 4. Presentation & Theme Couplings
- Identify custom theme templates (`.tpl.php`) or preprocess functions invoking custom module APIs.
- Custom modules that provide default themes or template suggestions via `hook_theme()`.

### 5. Data Migration Hierarchy Couplings
- Relational entity hierarchies where dependent data cannot be migrated before parent entities:
  - Roles & Permissions -> Users
  - Users -> Content Authors
  - Taxonomy Vocabularies -> Taxonomy Terms
  - Terms / Content Types -> Entity Reference Fields
  - Nodes -> Node Revisions & Comments

---

## Directed Acyclic Graph (DAG) Construction & Cycle Resolution

### Topological Sort Algorithm
1. Compute in-degrees for all components in the manifest.
2. Identify root leaf nodes (in-degree = 0, no custom dependencies).
3. Sequentially resolve dependencies, assigning components to progressive execution waves.

### Circular Dependency Resolution Strategy
When a cycle is detected ($A \to B \to A$):
1. **Analyze Interface Coupling**: Determine if the cycle is caused by an implicit hook alter or utility function.
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
