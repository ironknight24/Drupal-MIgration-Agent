---
name: dependency-analysis
description: Exhaustive dependency graph analysis, coupling detection, execution wave computation, and topological sorting across Drupal 7 and modern Drupal 10/11 architectures.
version: 1.12.0
user-invocable: false
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Dependency Analysis & Wave Scheduling Skill

## Overview
This skill provides the procedural playbook and algorithms for discovering code, schema, lifecycle, configuration, state, procedural hook execution ordering, module weights (`{system}.weight`), alter sequencing (`hook_module_implements_alter`), custom PHP class instantiations, entity reference graphs, revision/translation hierarchies, form builders, form alters, AJAX callbacks, legacy `.inc` function couplings, Views / custom plugin dependencies, theme / presentation layer inheritance, and dynamic runtime dependencies across legacy Drupal 7 components. It constructs a Directed Acyclic Graph (DAG) with explicit edge types (STATIC vs DYNAMIC vs RUNTIME_ONLY vs UNRESOLVED), detects circular dependencies, resolves dynamic fan-out, and organizes components into executable topological waves.

---

## Technical References
- [Drupal 7 Core APIs Reference](../../references/drupal-7/apis.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)

---

## 11-Dimensional Coupling Detection Heuristics

To establish an accurate DAG, inspect source assets across 11 distinct coupling vectors:

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
  - Trace hook execution order dependencies based on module weight (`{system}.weight`), `hook_module_implements_alter()`, and entity lifecycle sequencing (`presave` $\rightarrow$ `insert`/`update` $\rightarrow$ `postsave`).

### 3. Database & Schema Couplings
- Inspect `hook_schema()` declarations, table ownership, and queries across all module source files:
  - Module-to-table and cross-module table dependencies: trace `module -> table`, `class -> table`, `service -> table`, `form -> table`, `controller -> table`, `queue -> table`, `cron -> table`, `Drush -> table`.
  - Foreign keys pointing to tables owned by other custom or core modules.
  - Cross-module joins and queries (`db_query`, `db_select`, `db_insert`, `db_update`, `db_delete`) where module A mutates or queries tables defined by module B.
  - Shared junction tables and entity reference columns (`uid`, `nid`, `tid`, `fid`, `entity_id`).

### 4. Configuration, State & Variable Couplings
- Trace configuration and state read/write/delete relationships across custom modules:
  - `CONFIG -> SERVICE -> HOOK`: Service loads configuration to execute hook logic.
  - `FORM -> CONFIG WRITE`: Administration form persists settings used by controllers and services.
  - `CONFIG -> CONTROLLER`: Controller reads settings to determine view presentation or response parameters.
  - `STATE -> CRON`: Cron handler reads and updates runtime state (`last_run` timestamp).
  - `CONFIG -> ENTITY`: Entity type configuration or bundle settings referenced across modules.
  - `CONFIG -> EXTERNAL API`: Integration client service dependent on endpoint configuration.
  - Cross-module variable access: Module A reading or mutating variables (`variable_get`/`variable_set`) owned or initialized by Module B.

### 5. Entity Reference & Relationship Topologies (Step 16)
- Map entity reference hierarchies and relational dependencies across custom and core entities:
  - `SOURCE ENTITY -> TARGET ENTITY`: Source entity bundles referencing target entity IDs via `entityreference`, `taxonomy_term_reference`, `user_reference`, or `node_reference`.
  - `BASE ENTITY -> REVISION TABLE`: Base entity creation must precede historical revision ingestion.
  - `BASE ENTITY -> TRANSLATION RECORDS`: Default language records must precede translated field attachments.
  - `PARENT ENTITY -> CHILD/PARAGRAPH ENTITY`: Container entities depend on nested item definitions.
  - `COMPUTED FIELD -> SOURCE FIELD`: Derived field calculations depend on referenced entity properties.

### 6. Form, Form Alter & AJAX Couplings (Step 17)
- Map form-level dependencies and interaction call graphs:
  - `MODULE A (Form Builder) -> MODULE B (hook_form_FORM_ID_alter)`: Form alterations dependent on upstream form definitions and module weight execution order.
  - `FORM -> VALIDATION / SUBMIT CALLBACKS`: Custom validation and submit callbacks invoking cross-module services, database writes, or entity mutations.
  - `FORM -> AJAX ENDPOINT -> CONTROLLER / SERVICE`: Form `#ajax` callbacks invoking asynchronous response handlers.
  - `FORM -> ATTACHED ASSET LIBRARIES`: Forms declaring `#attached` dependencies on core or custom CSS/JS asset libraries.

### 7. Frontend Asset & Library Dependencies (Step 18)
- Map client-side script and stylesheet dependencies:
  - `MODULE LIBRARY -> CORE LIBRARY DEPENDENCIES`: Custom libraries declaring dependencies on `core/drupal`, `core/drupalSettings`, `core/once`, `core/jquery`, `core/drupal.ajax`, or other module libraries.
  - `DRUPAL BEHAVIOR -> DRUPAL SETTINGS`: Client-side JavaScript reading PHP runtime settings populated via render array attachments (`#attached['drupalSettings']`).
  - `JS EVENT HANDLER -> FORM / AJAX WRAPPER`: Client-side JavaScript bound to DOM selectors generated by Form API or AJAX response commands.
  - `CSS STYLESHEET -> THEME / TEMPLATE SELECTORS`: Stylesheets dependent on markup classes rendered by custom Twig templates, field formatters, or view modes (Step 20 Handoff).
  - `EXTERNAL / THIRD-PARTY ASSET -> CDN / VENDOR ASSET`: Module libraries dependent on external CDN resources or vendor assets.

### 8. Views, Plugins & Query Alteration Dependencies (Step 19)
- Map Views-specific dependencies across entities, queries, handlers, and displays:
  - `VIEW CONFIG -> BASE ENTITY / TABLE`: View definitions dependent on underlying Content Entities or custom database tables.
  - `VIEW CONFIG -> CUSTOM HANDLER / PLUGIN`: Views referencing custom field, filter, contextual filter, sort, area, or style plugins.
  - `VIEW CONFIG -> RELATIONSHIP CHAINS`: Views traversing multiple entity reference relationships (`node -> author -> custom_profile`).
  - `VIEW CONFIG -> HOOK_VIEWS_QUERY_ALTER`: Views whose query execution is modified by procedural query alteration hooks.
  - `VIEW EXPOSED FORM -> VIEW / FORM API EXPOSED WRAPPER`: Views exposed filter forms interacting with server-side Form API builder and validation callbacks.
  - `VIEW AJAX PAGINATION / FILTER -> VIEW / AJAX FRONTEND REFRESH`: Views with AJAX enabled communicating with client-side Drupal.ajax behaviors and response commands.
  - `VIEW TEMPLATE OVERRIDE -> THEME PRESENTATION`: Views template overrides (views-view.html.twig) owned by the theme layer (Step 20 Handoff).
  - `PROGRAMMATIC VIEW CALLER -> VIEW DEFINITION`: Controllers, blocks, or services dispatching `views_get_view()` or `views_embed_view()`.

### 9. Presentation & Theme Couplings (Step 20)
- Map theme-level dependencies, inheritance hierarchies, and template couplings:
  - `SUB-THEME -> BASE THEME`: Sub-themes inheriting templates, regions, and asset libraries from parent themes.
  - `TWIG TEMPLATE -> PREPROCESS HOOKS`: Templates consuming variables computed in module or theme preprocess functions.
  - `TEMPLATE -> THEME HOOK / SUGGESTION`: Dynamic template suggestions depending on `hook_theme_suggestions_HOOK_alter()`.
  - `THEME -> ASSET LIBRARIES`: Theme library dependencies on core libraries (`core/drupal`, `core/once`) or Step 18 module libraries.
  - `THEME TEMPLATE -> ENTITY / FIELD / VIEW / FORM`: Theme templates overriding entity view modes (Step 16), field formatters, Views layouts (Step 19), and forms (Step 17).
  - `THEME SETTINGS -> CONFIGURATION SCHEMA`: Theme configuration forms dependent on typed CMI schemas (`config/schema/<theme>.schema.yml`).

### 10. Data Migration Hierarchy & Database Ordering Couplings
- Relational entity and custom table hierarchies where dependent data cannot be migrated before parent entities:
  - Roles & Permissions $\rightarrow$ Users
  - Users $\rightarrow$ Taxonomy Vocabularies $\rightarrow$ Taxonomy Terms
  - Files / Managed Media $\rightarrow$ Content Types & Custom Entities
  - Custom Entities $\rightarrow$ Relationship Junction Tables
  - Entities $\rightarrow$ Custom Dependent Database Records $\rightarrow$ Serialized Payloads $\rightarrow$ Revisions & Comments
- Circular database or entity dependencies must be detected, flagged, and mapped to two-pass migration pipelines (stubbing references in pass 1, populating relations in pass 2).

### 11. Dynamic, Runtime & Data-Driven Dependency DAG Edge Modeling (Step 21)
- Explicitly integrate dynamic dependencies into the DAG:
  - **Edge Classification**:
    - `STATIC EDGE`: Deterministic, compile-time/static coupling verified by code analysis.
    - `DYNAMIC EDGE`: Statically bounded candidate set (e.g. switch/lookup table) linking producer to potential consumers.
    - `RUNTIME_ONLY EDGE`: Runtime-dependent coupling (e.g. database-stored callable, State API flag) requiring probe resolution.
    - `UNRESOLVED EDGE`: Open-ended dynamic dependency flagged for human architectural decision.
  - **Dynamic Fan-Out & Cycle Breaking**:
    - Where dynamic callables or plugins produce many possible consumer edges, create an intermediate abstraction node (Plugin Manager / Service Container / Event Dispatcher) to prevent artificial DAG cycles.
    - Unresolved dynamic dependencies do NOT halt DAG creation; they are scheduled with `RUNTIME_DISCOVERY_REQUIRED` or `HUMAN_DECISION_REQUIRED` gates.

### 12. External System Integration DAG Edge Modeling (Step 22)
- Explicitly model external dependencies and integration flows in the DAG:
  - **Integration Edge Types**:
    - `OUTBOUND_INTEGRATION_EDGE`: Custom Drupal code triggering external API/HTTP client or cloud service.
    - `INBOUND_WEBHOOK_EDGE`: External systems posting payloads to Drupal routes/webhooks.
    - `AUTH_CREDENTIAL_EDGE`: Integrations dependent on Key module / Environment variables / CMI configuration.
    - `DATA_FLOW_PIPELINE_EDGE`: Entity / DB state transformed to external payloads and vice-versa.
    - `FAILURE_RETRY_CASCADE_EDGE`: Dead-letter queue / Exponential backoff dependency flows.
  - **Cross-System Dependency & Cascade Mitigation**:
    - External system failures must not block internal dependency resolution; wrap external integrations in resilient Gateway Services or Queue Workers.
    - Schedule external integrations and complex webhook pipelines into **Wave 4** (Complex Integrations & AJAX Endpoints).

### 13. Cache, Session, Security & Runtime Lifecycle Couplings (Step 23)
- Trace runtime dependencies across caching, session state, access control, concurrency locks, and execution lifecycles:
  - `CACHE_INVALIDATION_EDGE`: Invalidation cascades where entity or config changes invalidate downstream render caches or custom cache tags (`node:123`, `node_list`, `config:system.site`).
  - `SESSION_STATE_EDGE`: State pipelines where multi-step forms, wizards, or temporary cart stores depend on session isolation and `PrivateTempStore`.
  - `SECURITY_ACCESS_EDGE`: Authorization decision trees where routes and controllers depend on custom `AccessCheckInterface` services, permissions, and node grants.
  - `LIFECYCLE_ORDERING_EDGE`: Bootstrap, request initialization, and shutdown execution ordering mediated by Symfony HttpKernel event priority.
  - `CONCURRENCY_LOCK_EDGE`: Mutex and lock acquisition boundaries (`LockBackendInterface`) preventing race conditions across cron, queue workers, and batch tasks.

---

## Directed Acyclic Graph (DAG) Construction & Cycle Resolution

### Topological Sort Algorithm
1. Compute in-degrees for all components in the manifest based on real architectural dependencies.
2. Identify root leaf nodes (in-degree = 0, no custom dependencies).
3. Sequentially resolve dependencies, assigning components to progressive execution waves.

### Circular Dependency Resolution Strategy
When a cycle is detected ($A \to B \to A$):
1. **Analyze Interface Coupling**: Determine if the cycle is caused by an implicit hook alter, utility function, circular class instantiation, bi-directional entity references, or dynamic callback loops.
2. **Refactor / Extract Shared Service or Two-Pass Migration**: Propose extracting the shared functionality into a standalone Wave 0 utility service or configuring a two-pass migration process plugin.
3. **Escalate Blocker**: If the cycle cannot be decoupled without modifying source code, raise a `BLOCKED-DEP-CYCLIC-<MODULES>.md` ticket.

---

## Execution Wave Formation Model

Components are scheduled into ordered execution waves:

| Wave | Category | Description | Criteria |
| :---: | :--- | :--- | :--- |
| **Wave 0** | **Foundation** | Core configuration entities, base utility services, independent schemas, base entity interfaces. | 0 custom dependencies. |
| **Wave 1** | **Leaf Modules & Base Entities** | Custom modules and base entity types with zero custom dependencies. | All dependencies satisfied in Wave 0. |
| **Wave 2** | **Intermediate Modules, Bundles & Forms** | Custom modules, bundles, dependent entity types, and interactive Form API classes. | All upstream custom modules completed. |
| **Wave 3** | **Data Pipelines & Content Migration** | Migration API configurations transferring base entities, revisions, and translations. | Target entities & fields exist in D10. |
| **Wave 4** | **Complex Integrations & AJAX Endpoints** | Webhooks, third-party sync, bi-directional entity reference resolution, complex AJAX forms. | Core module services & entities operational. |
| **Wave 5** | **Presentation Layer & Entity View Builders** | Themes, Twig templates, UI asset libraries, custom formatters/widgets. | Final entity render structures finalized. |
| **Wave 6** | **Dynamic Runtime Probes & Re-engineering** | Modernized plugin managers, dynamic callable services, runtime probe verification. | Target components operational. |
| **Wave 7** | **Runtime Lifecycle & Security Orchestration** | Cache invalidation subscribers, access checks, session managers, lock handlers. | Core services, themes, and plugins in place. |

---

## Architectural Replacement Dependency Discovery

When an architectural replacement is detected for a source module or subsystem:
1. **Target Subsystem Dependency Resolution**: Identify target module and service dependencies introduced by the replacement architecture (e.g. target core/contrib modules or existing custom services required by the modern implementation).
2. **Recursive Sub-DAG Expansion**: If the target replacement architecture relies on unmigrated upstream custom modules or services, expand the dependency sub-DAG to include those upstream components.
3. **Cycle Guard**: Run standard DFS cycle detection over the combined dependency graph. If the replacement creates a dependency loop, emit a `BLOCKED-CYCLE` ticket and pause for human architectural resolution.
4. **Topological Precedence**: Upstream dependencies of the target replacement architecture must be validated and completed before the dependent replacement behaviors are remediated.
