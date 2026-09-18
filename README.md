# AI-Assisted Drupal Migration Agent Framework

A modular, reusable, and deterministic AI-assisted agent framework designed to orchestrate the migration of Drupal 7 projects to Drupal 10, while establishing a modern, Drupal 11-ready software architecture.

---

## Overview

Migrating from Drupal 7 to Drupal 10 is not a mechanical syntax translation; it is an architectural replatforming. Procedural hook implementations, global variables, and unstructured arrays must transition into object-oriented services, plugins, dependency injection, and Twig templating.

This framework decouples **generic migration intelligence** from **project-specific configuration**. It orchestrates 13 specialized AI agents through structured lifecycle phases, strict evidence-backed validation, and non-destructive safety guardrails.

---

## Architecture & Directory Structure

```
drupal-migration/
│
├── migration.config.yml             # Project source/target paths, flags, and test commands
│
├── README.md                        # Framework overview and user guide
├── ARCHITECTURE.md                  # System architecture, agent responsibilities, D10/D11 patterns
├── AGENT_PROTOCOL.md                # Inter-agent handoff contracts and evidence taxonomy
├── MIGRATION_LIFECYCLE.md           # Default lifecycle, dynamic sequencing, resumption
├── SAFETY_RULES.md                  # 15 cardinal safety rules and path isolation mandates
├── REPORTING_STANDARD.md            # Deterministic report schemas and blocked item format
│
├── agents/                          # 13 Specialized Agent Specifications
│   ├── orchestrator/agent.md        # Master orchestration and dependency dispatch
│   ├── discovery/agent.md           # Read-only project inspection and baseline auditing
│   ├── dependency/agent.md          # Dependency DAG builder and dynamic sequence optimizer
│   ├── contrib-module/agent.md      # Contrib compatibility analysis and replacement strategy
│   ├── custom-module/agent.md       # 12-step custom module behavioral modernization
│   ├── custom-theme/agent.md        # PHPTemplate to Twig and asset library migration
│   ├── configuration/agent.md       # Variables, config entities, Views, and schema migration
│   ├── data-migration/agent.md      # Drupal Migration API pipelines and custom table ETL
│   ├── api-modernization/agent.md   # DI-first modernization; forbids blind \Drupal::* calls
│   ├── integration/agent.md         # External REST/SOAP/API endpoints and authentication
│   ├── testing/agent.md             # Configurable testing strategies (PHPUnit, PHPStan, PHPCS)
│   ├── validation/agent.md          # 12-category D7 vs D10 behavioral comparison matrix
│   └── final-audit/agent.md         # Post-migration gap analysis, security audit, sign-off
│
├── reports/                         # Deterministic markdown and YAML report outputs
│   ├── discovery/                   # D7 & D10 baseline audit reports
│   ├── dependencies/                # Dependency graphs and sequencing plans
│   ├── contrib/                     # Contrib module compatibility recommendations
│   ├── custom-modules/              # Per-module migration plans and implementation reports
│   ├── themes/                      # Theme migration and template audit reports
│   ├── configuration/               # CMI and variable export reports
│   ├── data/                        # Migration API pipeline definitions and logs
│   ├── api-modernization/           # API modernization diffs and service mappings
│   ├── testing/                     # Test execution outputs and static analysis reports
│   ├── validation/                  # Side-by-side behavioral validation matrices
│   ├── blocked/                     # BLOCKED-XXX tickets for unresolvable issues
│   └── final/                       # Comprehensive final audit and sign-off
│
├── state/                           # Dual State Management
│   ├── migration-state.yml          # "WHERE are we?" (phases, progress, active blockers)
│   └── migration-manifest.yml       # "WHAT are we migrating?" (component inventory & status)
│
├── logs/
│   └── file-change-log/             # Detailed audit trail of all modified/created files
│
└── templates/                       # Standardized report and ticket templates
    ├── discovery-report.md
    ├── dependency-report.md
    ├── migration-plan.md
    ├── file-change-log.md
    ├── validation-report.md
    ├── blocked-item.md
    └── final-audit.md
```

---

## The 13 Specialized Agents

| # | Agent | Primary Responsibility |
|---|---|---|
| 1 | **Orchestrator** | Master coordinator: reads config, schedules agents, monitors progress, handles blockers. |
| 2 | **Discovery** | Deep inspection of D7 and D10 environments; populates `migration-manifest.yml`. |
| 3 | **Dependency** | Builds dependency DAG; recommends dynamic execution order across all components. |
| 4 | **Contrib Module** | Evaluates D7 contrib against D10 core/ecosystem; proposes replacements or custom ports. |
| 5 | **Custom Module** | Executes 12-step behavioral modernization (Inventory -> Plan -> DI OOP -> Validation). |
| 6 | **Custom Theme** | Converts PHPTemplate to Twig, builds `libraries.yml`, ports CSS/JS and theme settings. |
| 7 | **Configuration** | Translates variables and system settings into D10 Configuration Management (CMI). |
| 8 | **Data Migration** | Designs Drupal Migration API pipelines; handles entity mapping and custom DB tables. |
| 9 | **API Modernization** | Refactors procedural APIs to modern OOP; enforces Dependency Injection first. |
| 10 | **Integration** | Modernizes external APIs, webhooks, authentication, and third-party services. |
| 11 | **Testing** | Defines test execution strategies; validates PHPUnit, PHPStan, and PHPCS. |
| 12 | **Validation** | Conducts D7 vs D10 behavioral comparison across 12 dimensions; requires proof. |
| 13 | **Final Audit** | Executes final code quality, security, deprecation scan, and generates sign-off. |

---

## Core Safety Guardrails

1. **Source Immutability**: The Drupal 7 source codebase (`source.path`) is treated as strictly **READ-ONLY**. The framework never alters, deletes, or writes to D7 files.
2. **Target Isolation**: Write operations are restricted strictly to the configured `target.path`. Any attempted write targeting D7 is immediately rejected.
3. **Path Overlap Prevention**: The framework verifies that `source.path` and `target.path` do not overlap; any collision aborts the migration immediately.
4. **No Git Commits by Default**: `allow_commits: false` and `allow_branch_creation: false` ensure all changes are tracked via file change logs and explicit diffs.
5. **No Blind Syntax Translation**: Code is migrated through behavior extraction, OOP service design, and modern Drupal 10/11 conventions.
6. **No PASS Without Evidence**: Agents are strictly forbidden from claiming a test passed, a feature works, or data migrated without citing empirical proof.

---

## Getting Started & Execution Workflow

### Step 0: Framework Setup (Current State)
The agent factory and specifications are authored. No project files are inspected or modified.

### Step 1: Project Discovery & Baseline Audit
Configure source and target paths in `migration.config.yml`:
```yaml
source:
  drupal_version: "7"
  path: "/path/to/drupal7"
target:
  drupal_version: "10"
  path: "/path/to/drupal10"
```
Run the Discovery Agent to inspect the environments and populate `state/migration-manifest.yml`.

### Step 2: Dependency Analysis & Execution Sequencing
The Dependency Agent evaluates components, resolves the DAG, and establishes the dynamic migration order.

### Step 3+: Phased Execution & Validation
The Orchestrator dispatches specialized agents according to the dependency graph, tracking progress in `state/migration-state.yml`.
