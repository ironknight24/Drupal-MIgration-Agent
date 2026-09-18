# Drupal Migration Agent (`drupal-migration-agent`)

An AI-assisted, distributable Claude Code plugin package designed to orchestrate the migration of Drupal 7 projects to Drupal 10 (with Drupal 11-ready architecture).

---

## Overview

Migrating from Drupal 7 to Drupal 10 is not a mechanical syntax translation; it is an architectural replatforming. Procedural hook implementations, global variables, and unstructured arrays must transition into object-oriented services, plugins, dependency injection, and Twig templating.

This repository serves as a **distributable Claude Code plugin package** that decouples **generic migration intelligence** from **project-specific configuration**. It provides:
- **13 Specialized Autonomous Agents** managing discrete migration phases.
- **Modular Migration Skills** adhering to the Agent Skills standard (`agentskills.io`).
- **Deep Technical References** for legacy D7 and modern D10/D11 architectures.
- **Interactive Slash Commands** for streamlined user execution.
- **Strict Non-Destructive Guardrails** treating Drupal 7 source code as strictly read-only.

---

## Claude Code Installation & Usage

### 1. Local Development / Testing
To test or use this package locally in Claude Code:
```bash
claude --plugin-dir /path/to/Drupal-MIgration-Agent
```
Within your active Claude Code session, reload plugins with:
```text
/reload-plugins
```

### 2. Direct GitHub Installation
Install the package directly from GitHub:
```text
/plugin install ironknight24/Drupal-MIgration-Agent
```

### 3. Marketplace Installation (Optional)
If registering as a marketplace catalog:
```text
/plugin marketplace add ironknight24/Drupal-MIgration-Agent
/plugin install drupal-migration-agent@drupal-migration-marketplace
```

---

## User Experience & Slash Commands

Users do not need to invoke 13 individual subagents manually. Use the provided slash commands:

| Command | Full Plugin Namespace | Purpose |
|:---|:---|:---|
| `/orchestrate` | `/drupal-migration-agent:orchestrate` | Guides setup and initiates the full end-to-end migration lifecycle. |
| `/discover` | `/drupal-migration-agent:discover` | Runs a standalone, read-only baseline audit on D7/D10 environments. |
| `/status` | `/drupal-migration-agent:status` | Displays real-time phase progress, manifest statistics, and blockers. |

*Advanced Mode*: Individual agents can still be directly invoked by advanced users (e.g. `drupal-migration:custom-module`).

---

## Architecture & Directory Structure

```
Drupal-MIgration-Agent/
│
├── .claude-plugin/                  # Plugin metadata & marketplace catalog
│   ├── plugin.json                  # Primary Claude Code plugin manifest
│   └── marketplace.json             # Optional marketplace catalog definition
│
├── commands/                        # User-facing slash commands
│   ├── orchestrate.md               # /orchestrate entry point
│   ├── discover.md                  # /discover baseline audit
│   └── status.md                    # /status dashboard
│
├── agents/                          # 13 Specialized Migration Workers
│   ├── orchestrator.md              # Master orchestration & dynamic sequencing
│   ├── discovery.md                 # Read-only environment & code auditing
│   ├── dependency.md                # Dependency DAG solver & execution wave sequencing
│   ├── contrib-module.md            # Contrib module compatibility & core merge analysis
│   ├── custom-module.md             # 12-step behavioral modernization engine
│   ├── custom-theme.md              # PHPTemplate to Twig, libraries.yml, modern CSS/JS
│   ├── configuration.md             # Variables, views, and settings to CMI YAML exporter
│   ├── data-migration.md            # Drupal Migration API pipeline architect
│   ├── api-modernization.md         # Dependency Injection first; forbids blind \Drupal::*
│   ├── integration.md               # REST/SOAP/API endpoints, webhooks, auth modernization
│   ├── testing.md                   # Configurable test strategies (PHPUnit, PHPStan, PHPCS)
│   ├── validation.md                # 12-dimensional comparative behavioral auditor
│   └── final-audit.md               # Gap analysis, security review, and final sign-off
│
├── skills/                          # Reusable Domain Capabilities (Agent Skills Standard)
│   ├── d7-analysis/SKILL.md         # [IMPLEMENTED] Read-only D7 code/AST inspection heuristics
│   ├── d7-to-d10-mapping/SKILL.md   # [IMPLEMENTED] Procedural-to-OOP transformation rules
│   ├── d10-architecture/SKILL.md    # [IMPLEMENTED] Modern D10/D11 standards (PHP 8 attributes, DI)
│   ├── custom-module-migration/SKILL.md # [IMPLEMENTED] 12-step module modernization playbook
│   └── ...                          # Other skills explicitly designated as PLANNED
│
├── references/                      # Deep Technical Knowledge Bases
│   ├── drupal-7/apis.md             # D7 core APIs, hooks, database, globals
│   ├── drupal-10/architecture.md    # D10/D11 services, plugins, CMI, routing
│   └── migration-patterns/common-conversions.md # Canonical conversion patterns
│
├── templates/                       # Standardized report & ticket templates
├── reports/                         # Deterministic report output directories
├── state/                           # Dual state management templates (state & manifest)
├── logs/                            # Audit logs (file change tracking)
│
├── migration.config.yml             # Master configuration template & defaults
├── README.md                        # Package documentation & usage guide
├── ARCHITECTURE.md                  # Factory vs Migration execution architecture
├── AGENT_PROTOCOL.md                # Inter-agent handoff contracts & evidence taxonomy
├── MIGRATION_LIFECYCLE.md           # Dynamic execution lifecycle & wave formation
├── SAFETY_RULES.md                  # 15 cardinal safety rules & path protection
├── REPORTING_STANDARD.md            # Deterministic report schemas & blocked tickets
└── CLAUDE_CODE_PACKAGING.md         # Authoritative Claude Code packaging manual
```

---

## Core Safety Guardrails

1. **Source Immutability**: The Drupal 7 source codebase (`source.path`) is treated as strictly **READ-ONLY**. The framework never alters, deletes, or writes to D7 files.
2. **Target Isolation**: Write operations are restricted strictly to the configured `target.path`. Any attempted write targeting D7 is immediately rejected.
3. **Path Overlap Prevention**: The framework verifies that `source.path` and `target.path` do not overlap; any collision aborts the migration immediately (`GLOBAL MIGRATION BLOCKED`).
4. **No Git Commits by Default**: `allow_commits: false` and `allow_branch_creation: false` ensure all changes are tracked via file change logs and explicit diffs.
5. **No Blind Syntax Translation**: Code is migrated through behavior extraction, OOP service design, and modern Drupal 10/11 conventions (constructor Dependency Injection).
6. **No PASS Without Evidence**: Agents are strictly forbidden from claiming a test passed, a feature works, or data migrated without citing empirical proof.

---

## Factory Development Lifecycle vs. Migration Execution Lifecycle

- **Factory Development Lifecycle (Building this Package)**:
  - Factory Step 0: Framework & Specification Definition [COMPLETE]
  - Factory Step 1: Claude Code Package & Architecture Transformation [CURRENT]
  - Factory Step 2: Migration Skills & Knowledge Codification [NEXT]
  - Factory Step 3: Agent Execution Logic Implementation [PLANNED]
  - Factory Step 4: End-to-End Package Testing & Verification [PLANNED]
  - Factory Step 5: Distribution & Release [PLANNED]

- **Migration Execution Lifecycle (When running against a real project)**:
  - Migration Step 0: Setup & Path Verification
  - Migration Step 1: Project Discovery & Baseline Audit
  - Migration Step 2: Dependency Graph & Wave Scheduling
  - Migration Step 3: Contrib Compatibility Strategy
  - Migration Step 4: Component Migration Planning
  - Migration Step 5: Execution & Modernization (Modules, Themes, Config, Data)
  - Migration Step 6: Automated Testing & Static Analysis
  - Migration Step 7: Behavioral Validation
  - Migration Step 8: Final Audit & Sign-off
