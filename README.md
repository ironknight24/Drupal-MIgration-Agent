# Drupal Migration Agent (`drupal-migration-agent`)

A generic, recursive, evidence-driven, stateful Claude Code plugin package designed to orchestrate and execute the architectural modernization and migration of Drupal 7 codebases to Drupal 10 (with Drupal 11-ready architecture). The generic migration-agent factory capability operates 100% generically against arbitrary Drupal 7 source without project-specific assumptions.

---

## What Is This?

The **Drupal Migration Agent** is an autonomous pair-programming assistant for Drupal replatforming. It bridges the architectural gap between legacy Drupal 7 procedural code and modern Drupal 10/11 object-oriented Symfony architectures using specialized agents, modular skills, and forensic completeness auditing.

---

## What It Does

Migrating from Drupal 7 to Drupal 10/11 is an architectural transformation. The agent:
- **Discovers legacy assets**: Recursively inventories hooks, classes, `.inc` files, database schemas, entities, forms, frontend assets, and external APIs.
- **Resolves dependencies recursively**: Automatically builds dependency graphs and migrates upstream custom module dependencies in topological order.
- **Executes modular modernization**: Dispatches 13 specialist agents to convert legacy code into modern PSR-4 classes, Twig templates, CMI configuration, and constructor dependency injection.
- **Audits completeness with evidence**: Verifies that 100% of discovered functionality is accounted for across 10 canonical item statuses.
- **Remediates safe gaps automatically**: Iteratively fixes missing routes, services, and form methods within bounded retry limits.
- **Pauses for human decisions**: Halts cleanly on ambiguous business logic or GDPR policies without inventing behavior.

---

## Key Features

- **Preflight Environment Validation**: Guarantees path safety and configuration validity before modifying files.
- **Targeted Single-Module Migration**: Run isolated migrations on individual modules (`/orchestrate <MODULE_NAME>` or `/migrate-module <MODULE_NAME>`).
- **Architectural Replacement Detection & Behavioral Mapping**: Recognizes when source functionality is represented by a different target architecture and maps underlying behavior rather than performing blind API translation.
- **External Drupal-Integrated Code Discovery & Remediation**: Discovers, classifies, and remediates custom standalone PHP scripts, endpoints, CLI tools, and integration gateways residing outside standard module directories based on multi-vector empirical evidence.
- **Recursive Dependency Resolution**: Automatically resolves ancestor sub-DAGs with cycle detection.
- **3-Path Remediation Engine**: Distinguishes auto-fixable gaps from human decision gates and runtime-unverified items.
- **Evidence-First Completion Contract**: "Implemented" ≠ "migrated completely". Tasks complete only with empirical proof.
- **Dual-Audience Reports**: Outputs human-readable forensic analyses and structured `## LLM REMEDIATION INPUT` for chat workflows.
- **Strict Safety Guarantees**: D7 source is 100% read-only; writes are isolated strictly to assigned target module directories.
- **State Persistence & Resumption**: Safe recovery from interruptions with single-writer YAML state management.

---

## Quick Start

```text
Install Plugin
      │
      ▼
Configure (migration.config.yml)
      │
      ▼
   /preflight       ──► Verify paths & environment safety
      │
      ▼
   /discover        ──► Inventory legacy D7 & target D10 assets
      │
      ▼
 /orchestrate       ──► Run targeted (/orchestrate <MODULE>) or global migration
      │
      ▼
    /status         ──► Inspect progress, reports, and blocker states
```

---

## Consumer Onboarding & Installation

### Step 1: Install the Plugin
```bash
# Install via Claude Code Marketplace
/plugin install drupal-migration-agent

# Or load directly from local checkout:
claude --plugin-dir /path/to/Drupal-MIgration-Agent
```
> For complete packaging and distribution details, see the [Claude Code Packaging Guide](CLAUDE_CODE_PACKAGING.md).

### Step 2: Initialize Configuration
Copy `migration.config.example.yml` to the repository root:
```bash
cp migration.config.example.yml migration.config.yml
```

### Step 3: Minimal `migration.config.yml`
```yaml
version: "1.0"
source:
  path: "./community/drupal/drupal7"
  core_version: "7.x"
target:
  path: "./community/drupal"
  web_root: "./community/drupal/web"
  core_version: "10.3"
  custom_modules_path: "modules/custom"
  custom_themes_path: "themes/custom"
```
> For full configuration options, retry budgets, and safety flags, see [migration.config.example.yml](migration.config.example.yml).

---

## Commands

| Command | Purpose | Read-Only? | Scope Support | Detailed Reference |
| :--- | :--- | :---: | :---: | :--- |
| [`/preflight`](commands/preflight.md) | Validates environment, directories, core markers, secret isolation | Yes | Global | [commands/preflight.md](commands/preflight.md) |
| [`/discover`](commands/discover.md) | Recursively inventories files, hooks, classes, entities, variables, routes | Yes | Global / Target | [commands/discover.md](commands/discover.md) |
| [`/orchestrate`](commands/orchestrate.md) | Master recursive migration engine (Targeted or Global) | No | Both | [commands/orchestrate.md](commands/orchestrate.md) |
| [`/migrate-module`](commands/migrate-module.md) | Targeted recursive single-module migration alias (`/migrate-module <MODULE_NAME>`) | No | Targeted Only | [commands/migrate-module.md](commands/migrate-module.md) |
| [`/status`](commands/status.md) | Displays migration lifecycle, wave progress, and blockers | Yes | Global / Target | [commands/status.md](commands/status.md) |

---

## Recommended Workflow

```text
   USER INITIATION
         │
         ▼
    /preflight           ──(Fails)──► Fix paths/permissions & Re-run
         │ (Passes)
         ▼
    /discover            ──► Populates state/migration-manifest.yml
         │
         ▼
/orchestrate <MODULE>    ──► Build sub-DAG, detect cycles, resolve upstream
         │
         ▼
Forensic Baseline & Plan ──► Scaffold & Re-engineer D10 PSR-4 classes
         │
         ▼
Completeness Audit       ──► Classify 100% of items into 10 canonical statuses
         │
         ├──[Fixable from Evidence]────► Auto-Remediate ──► Re-Audit (Loops 1..3)
         │
         ├──[Requires Human Decision]──► HUMAN_INTERVENTION_REQUIRED ──► PAUSE
         │                                       │ (Human supplies decision)
         │                                       ▼
         │                                    RESUME
         │
         └──[Runtime Unavailable]──────► Tag RUNTIME_UNVERIFIED ──► Proceed static
         │
         ▼
Evidence Sign-Off        ──► COMPLETED (or PARTIAL/BLOCKED) in state/migration-state.yml
         │
         ▼
      /status            ──► Verify final outcomes & LLM remediation tasks
```

---

## Recursive Orchestration

When a targeted module is orchestrated (e.g. `/orchestrate custom_booking`):
1. **Sub-DAG Construction**: The orchestrator extracts $\text{Ancestors}(M) \cup \{M\}$.
2. **Cycle Detection**: Traverses dependency edges. If a circular dependency is detected ($A \to B \to A$), execution halts with a blocker ticket (`BLOCKED-<MODULE>-001-CYCLE.md`).
3. **Bottom-Up Dependency Processing**: Unmigrated upstream custom dependencies are migrated and validated before the parent module begins.
4. **Task-Level Recursion**: Missing components (routes, services, form classes, JS behaviors) discovered during post-implementation audits are converted into discrete remediation sub-tasks.
5. **Loop Prevention Guardrails**:
   - `max_remediation_iterations: 3`: Maximum number of remediation cycles per module.
   - `max_retries_per_component: 2`: Maximum attempts to fix a single failing component.

> For deep architectural details, state machines, and communication contracts, see [System Architecture](ARCHITECTURE.md) and [Migration Lifecycle](MIGRATION_LIFECYCLE.md).

---

## Report Status Model

Every legacy item is classified into one of these 10 unambiguous statuses in [REPORTING_STANDARD.md](REPORTING_STANDARD.md):

| Status | Definition | Next Action |
| :--- | :--- | :--- |
| `COMPLETE` | Fully modernized into D10/D11 architecture and verified. | Done. |
| `PARTIAL` | Re-engineered but missing methods, parameters, or edge cases. | Auto-Remediate |
| `MISSING` | Discovered in D7 but not yet implemented in D10. | Auto-Remediate |
| `BLOCKED` | Cannot proceed due to missing upstream dependency or fatal syntax error. | Blocker Ticket |
| `HUMAN_INTERVENTION_REQUIRED` | Business requirement ambiguous, GDPR policy needed, or architecture decision required. | Human Gate |
| `RUNTIME_UNVERIFIED` | Modernized statically, but runtime behavior requires live Drupal execution. | Defer Dynamic |
| `SUPERSEDED` | Replaced by Drupal core, contrib module, or modern platform capability. | Documented |
| `REPLACED` | Re-engineered under a modern architecture (e.g. `hook_menu` $\to$ Symfony route). | Documented |
| `OBSOLETE` | Dead/commented legacy D7 code intentionally not migrated. | Documented |
| `EXCLUDED` | Intentionally excluded with documented evidence (e.g. D7-only migration utility). | Documented |

---

## Architecture & Re-engineering Capabilities Overview

The factory recursively discovers, accounts for, and modernizes all Drupal 7 architectural surfaces:
- **Legacy `.inc` File Re-engineering**: The factory recursively analyzes `.inc` files within Drupal 7 custom modules (`includes/`, `lib/`, `admin/`, `forms/`, `*.inc`), dissecting procedural functions into modern PSR-4 classes.
- **Legacy Custom PHP File & OOP Class Re-engineering**: Converts custom PHP classes, legacy constructors (`ClassName()` and `__construct()`), and globals into modern constructor Dependency Injection.
- **Legacy Custom Database, Schema & Data Model Accounting**: Modernizes Legacy Custom Database tables in `hook_schema()`, indexes, foreign keys, and procedural queries (`db_query`, `db_select`, `db_insert`, `db_update`, `db_delete`, `db_merge`, `db_transaction`) into secure Entity / Repository architectures.
- **Procedural Hooks & `hook_menu()` Re-engineering**: Re-engineers procedural hooks (`hook_menu`, `hook_form_alter`, `hook_node_*`, alter hooks) into routes (`.routing.yml`), Controllers, Forms, and Event Subscribers.
- **Configuration, State, Variables Accounting**: Re-engineers `variable_get/set/del`, `system_settings_form`, and `$conf` into CMI configuration YAML (`config/install/`, `config/schema/`) and State API keys with strict secret protection.
- **Custom Entities, Bundles, Fields, Revisions, Translations**: Decomposes custom entities (`hook_entity_info`) into modern `@ContentEntityType` classes, base fields, and CMI field configs.
- **Forms, Form Alters, AJAX Modernization**: Re-engineers Form API arrays, validation callbacks, and AJAX commands into `FormBase`, `ConfigFormBase`, `ConfirmFormBase`, and `AjaxResponse` OOP command classes.
- **Frontend JavaScript, CSS, Libraries**: Modernizes `Drupal.behaviors` and jQuery `.once()` into `@drupal/once` iterating natively with `forEach()`, maps `Drupal.settings` to `drupalSettings`, and generates SMACSS libraries in `<module>.libraries.yml`.
- **Views, Displays, Custom Handlers & Plugins**: Migrates default views into CMI configuration (`views.view.*.yml`) and modernizes custom Views handlers into annotated plugins in `src/Plugin/views/`.
- **Themes, Templates, Preprocess**: Converts PHPTemplate `.tpl.php` files into clean Twig templates, modernizes `hook_theme` into render elements, and refactors preprocess/process hooks.
- **Dynamic, Runtime & Data-Driven Dependencies**: Detects variable functions, dynamic class instantiations (`new $class()`), and dynamic hooks, resolving them statically or documenting explicit runtime boundaries.
- **External Integrations, APIs & Webhooks**: Re-engineers outbound HTTP (`drupal_http_request`, cURL), REST endpoints, OAuth, and webhooks into Guzzle Gateway Services and Symfony Webhook Controllers with exponential backoff retries.
- **Cache, Session, Security & Runtime Behavior**: Modernizes caching to bubbleable metadata (`tags`, `contexts`, `max-age`), session handling to `SessionInterface`, CSRF tokens, and lifecycle hooks (`hook_boot/init`) to HttpKernel events.

---

## Case Study: Enterprise Modernization Lessons

The architecture of this factory directly reflects lessons learned during the migration of real-world enterprise modules:
- **Missing Controller Gaps**: Static syntax checkers reported no failures, but menu links referenced non-existent controllers; comparative completeness audits caught these missing classes and auto-remediated them.
- **GDPR Policy Gating**: Legacy purchase order retention rules were ambiguous; rather than inventing a retention period, the agent safely escalated to `HUMAN_INTERVENTION_REQUIRED`.
- **Superseded Integrations**: Legacy KeyVault encryption functions were recognized as `SUPERSEDED` by the modern D10 Key module.
- **Dead Code Elimination**: D7 utility functions with zero active call paths were classified as `OBSOLETE` with empirical evidence.

---

## Reports & LLM Remediation Input

All migration reports are generated under `reports/` following the [Reporting Standard](REPORTING_STANDARD.md):

| Report Location | Contents |
| :--- | :--- |
| `reports/preflight/` | Environment safety audit and path verification logs |
| `reports/discovery/` | Full codebase inventory and asset catalog |
| `reports/dependencies/` | Inter-module dependency graphs and wave sequencing |
| `reports/migration/<MODULE>/` | Forensic 8-artifact evidence suite for single-module workflows |
| `reports/human_decisions/` | Formal decision tickets when human input is required |
| `reports/blocked/` | Upstream dependency blockers and cycle detection tickets |
| `reports/final/` | Master executive summary and acceptance sign-off |

### LLM Remediation Input
Every report contains a dedicated `## LLM REMEDIATION INPUT` section with copy-pasteable YAML tasks for use in Claude or ChatGPT:
```yaml
- task_id: "BOOKING-SERVICE-004"
  status: "MISSING"
  priority: "HIGH"
  d7_behavior: "Procedural function in booking.admin.inc querying external SOAP endpoint."
  d10_current_state: "Service class missing in target src/Service/."
  evidence: "reports/migration/booking/booking_GAP_ANALYSIS.md#L45"
  required_change: "Create BookingSyncService in src/Service/ with method syncBookings()."
  dependencies: ["core/http_client"]
  human_decision_required: false
```

---

## Safety Model & Safety Guarantees

- **D7 Read-Only**: Source codebase is strictly immutable (0 source file mutations).
- **Target Sandboxing**: Single-module migrations write strictly to `<target_path>/web/modules/custom/<MODULE_NAME>/**/*`.
- **Zero Hallucinated Code**: Ambiguous requirements pause for human review rather than generating guessed code.
- **Secret Isolation**: Zero passwords, tokens, or API keys are committed to CMI YAML files.
- **Bounded Execution**: Loop prevention budgets (`max_remediation_iterations: 3`, `max_retries_per_component: 2`) prevent infinite retry loops.

> For the comprehensive 12-point safety matrix, see [Safety Rules](SAFETY_RULES.md).

---

## Troubleshooting & Runtime Boundaries

- **Preflight Fails (`PRE-01` / `PRE-04`)**: Ensure `source.path` and `target.path` exist and do not point to the same directory.
- **Module Blocked Upstream (`BLOCKED_UPSTREAM`)**: Run `/orchestrate <DEPENDENCY_MODULE>` to migrate upstream dependencies first.
- **Execution Paused on Human Gate**: Review `reports/human_decisions/`, provide input, and re-run `/orchestrate <MODULE_NAME>`.
- **Runtime Unverified Notices**: In environments without a live Drupal database or DDEV, dynamic features are explicitly documented as `[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]`.

---

## Documentation Map

| Area | Topic | Authoritative Document |
| :--- | :--- | :--- |
| **Commands** | Interactive slash command contracts | [commands/preflight.md](commands/preflight.md), [commands/discover.md](commands/discover.md), [commands/orchestrate.md](commands/orchestrate.md), [commands/migrate-module.md](commands/migrate-module.md), [commands/status.md](commands/status.md) |
| **Architecture** | System architecture, layers & data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Lifecycle** | 10-phase lifecycle, sub-DAG scheduler, cycle detection | [MIGRATION_LIFECYCLE.md](MIGRATION_LIFECYCLE.md) |
| **Reporting** | 10 canonical statuses, 16-section reports & LLM schema | [REPORTING_STANDARD.md](REPORTING_STANDARD.md) |
| **Safety** | 12-point safety matrix & immutability rules | [SAFETY_RULES.md](SAFETY_RULES.md) |
| **Agent Protocol** | Communication contracts & Result Validation Gate | [AGENT_PROTOCOL.md](AGENT_PROTOCOL.md) |
| **Packaging** | Claude Code plugin manifest & marketplace distribution | [CLAUDE_CODE_PACKAGING.md](CLAUDE_CODE_PACKAGING.md) |
| **Specialist Agents** | 13 autonomous migration agents | [agents/orchestrator/agent.md](agents/orchestrator/agent.md), [agents/custom-module/agent.md](agents/custom-module/agent.md), [agents/](agents/) |
| **Skills** | 12 modular domain skills | [skills/custom-module-migration/SKILL.md](skills/custom-module-migration/SKILL.md), [skills/](skills/) |
| **References** | D7 & D10 API catalogs and conversion patterns | [references/](references/) |
| **History & Evidence**| Implementation report for recursive orchestration and validation | [reports/factory/RECURSIVE-ORCHESTRATION-IMPLEMENTATION-REPORT.md](reports/factory/RECURSIVE-ORCHESTRATION-IMPLEMENTATION-REPORT.md) |

---

## Project Structure

```text
Drupal-MIgration-Agent/
├── .claude-plugin/          <-- Plugin and marketplace manifests
├── commands/                <-- Slash command entry points
├── agents/                  <-- 13 autonomous specialist agents
├── skills/                  <-- Modular domain skills (agentskills.io)
├── references/              <-- Technical conversion guides and API catalogs
├── templates/               <-- Standard report and artifact templates
├── state/                   <-- Central state and scope manifests
├── reports/                 <-- Generated evidence, audits, and decisions
└── tests/                   <-- Automated self-validation test suite
```

---

## Frequently Asked Questions (FAQ)

### Can I migrate just one module without migrating the whole site?
Yes! Use `/orchestrate <MODULE_NAME>` or `/migrate-module <MODULE_NAME>`. The agent will isolate its writes strictly to that module and resolve any unmigrated custom dependencies automatically.

### Do I need a live DDEV or Drupal runtime?
No. Static re-engineering, PSR-4 class generation, CMI schema generation, and static validation work 100% autonomously. Dynamic database checks will simply be tagged as `RUNTIME_UNVERIFIED`.

### What happens if the agent encounters ambiguous business logic?
The agent will never guess or invent behavior. It transitions the task to `HUMAN_INTERVENTION_REQUIRED`, records a decision prompt in `reports/human_decisions/`, and pauses execution until you provide guidance.

### Can I feed generated reports into Claude or ChatGPT?
Yes! Every migration report contains a dedicated `## LLM REMEDIATION INPUT` YAML block with stable task IDs specifically formatted for copy-pasting into normal chat conversations.

### How do I resume an interrupted migration?
Simply re-run `/orchestrate` (or `/orchestrate <MODULE_NAME>`). The orchestrator reads `state/migration-state.yml`, skips already completed components, and resumes from the lowest incomplete step.
