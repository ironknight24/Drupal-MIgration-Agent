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

## Legacy Custom PHP File, OOP Class & `.inc` Re-engineering Architecture

The factory recursively analyzes `.inc` files within Drupal 7 custom modules and recursively analyzes custom PHP files, OOP classes, constructors, interfaces, traits, and functions to migrate the functionality they contain into appropriate Drupal 10/11 architecture.

- **Recursive Discovery Without Naming Assumptions**: Scans all custom module roots and nested subdirectories (`includes/`, `lib/`, `classes/`, `src/`, `admin/`, `forms/`, `pages/`, `commands/`, etc.) discovering all `*.php`, `*.inc`, `*.module`, `*.install`, `*.profile`, and `*.drush.inc` files.
- **Custom OOP PHP Class & Constructor Discovery**: Extracts classes, abstract classes, interfaces, traits, parent classes, used traits, constants, properties, and methods. Analyzes constructors (modern `__construct()` and legacy PHP4/D7 `ClassName()` constructors), parameter dependencies, global state usage (`$user`, `$language`, `variable_get()`), direct SQL queries, and side effects.
- **Include, Require & Autoloading Analysis**: Analyzes how custom classes become available in D7 (direct `require`, `module_load_include()`, `.info` `files[]`, custom autoloaders) and modernizes them into PSR-4 compliant autoloading without preserving legacy manual includes.
- **Caller & Reference Analysis**: Traces callers, class instantiations (`new ClassName()`), and static method calls across the owning module and other custom modules.
- **22-Class Architectural Taxonomy**: Classifies every functional piece into standard categories (`SERVICE_BUSINESS_LOGIC`, `CONTROLLER`, `FORM`, `PLUGIN`, `EVENT_SUBSCRIBER`, `ACCESS_CHECKER`, `ENTITY_LOGIC`, `FIELD_LOGIC`, `QUEUE_WORKER`, `BATCH_PROCESSOR`, `CRON_HANDLER`, `DRUSH_COMMAND`, `CONFIGURATION_HANDLER`, `INTEGRATION_CLIENT`, `DATA_ACCESS`, `VALUE_OBJECT`, `DOMAIN_OBJECT`, `UTILITY_HELPER`, `TEST_SUPPORT`, `LIBRARY_EXTERNAL_DEPENDENCY`, `LEGACY_OBSOLETE`, `HUMAN_DECISION_REQUIRED` / `UNVERIFIED`).
- **Constructor Dependency Injection Modernization**: Refactors legacy constructors to modern `__construct(...)` with explicit typehints and constructor-injected services (`database`, `entity_type.manager`, `config.factory`, `current_user`) avoiding service proliferation.
- **Non-1:1 Architectural Re-engineering (1-to-Many & Many-to-One)**:
  - Custom PHP files and `.inc` files are not copied blindly.
  - One legacy PHP file may produce multiple modern PSR-4 classes (e.g. `src/Service/`, `src/Form/`, `src/Controller/`), and multiple legacy files may merge into one modern service.
- **Drush Command Modernization**: Discovered Drush commands in `.inc` and `.php` files are cataloged and re-engineered into modern Drush 12+ command classes and services (`drush.services.yml`).
- **Zero-Omission Accounting**: Every custom PHP file, class, constructor, method, and `.inc` file must end in an approved state: `MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, or `UNVERIFIED`. The states `UNACCOUNTED`, `UNKNOWN_WITHOUT_REASON`, and `SILENTLY_OMITTED` are strictly forbidden and trigger validation failure.
- **Human Decision Gates & Verifiable Boundaries**: Where business intent or dynamic behavior cannot be established statically, human decisions are required (`reports/blocked/`) rather than making assumptions.

---

## Consumer Onboarding & First-Run Guide

Follow these steps to initialize and run a migration against your Drupal projects:

### 1. Obtain & Install the Package

**Direct GitHub Installation (Claude Code):**
```text
/plugin install ironknight24/Drupal-MIgration-Agent
```

**Local Development / Testing Mode:**
```bash
claude --plugin-dir /path/to/Drupal-MIgration-Agent
```
*(Within your Claude Code session, reload plugins with `/reload-plugins`)*

---

### 2. Configure Your Migration Workspace

1. In your workspace root, create your configuration from the canonical factory template:
   ```bash
   cp migration.config.example.yml migration.config.yml
   ```
2. Edit `migration.config.yml` to specify your project locations:
   ```yaml
   source:
     drupal_version: "7"
     path: "/path/to/your/drupal7_source"
     custom_modules_path: "sites/all/modules/custom"
     custom_themes_path: "sites/all/themes"

   target:
     drupal_version: "10" # or "11"
     path: "/path/to/your/drupal10_target"
     web_root: "web"
     custom_modules_path: "web/modules/custom"
     custom_themes_path: "web/themes/custom"
     config_sync_directory: "config/sync"
   ```
   > [!IMPORTANT]
   > Do NOT commit passwords or credentials to `migration.config.yml`. Passwords should be supplied via environment variables or local drush aliases.

---

### 3. Run Preflight Environment Validation

Before scanning or modifying any code, execute the non-destructive preflight gate:
```text
/preflight
```
The preflight command evaluates:
- Configuration validity and secret isolation (`PRE-01`, `PRE-09`).
- `source.path` and `target.path` existence and non-overlap (`PRE-02` through `PRE-04`).
- Drupal 7 structural markers (`includes/bootstrap.inc`, `modules/system/system.module`) (`PRE-05`).
- Drupal 10/11 target markers (`core/lib/Drupal.php`, `composer.json`) (`PRE-06`).
- Target version consistency and target directory write permissions (`PRE-07`, `PRE-08`).

Inspect the generated report at `reports/preflight/PREFLIGHT-REPORT-<DATE>.md`. If any critical check fails, resolve the blockers before continuing.

---

### 4. Execute Discovery Baseline Audit

Once Preflight reports `PASS`, run a comprehensive read-only audit:
```text
/discover
```
This inventories all D7 custom modules, contrib modules, themes, hooks, database tables, and external integrations, generating `reports/discovery/DISCOVERY-AUDIT-<DATE>.md` and populating `state/migration-manifest.yml`.

---

### 5. Orchestrate End-to-End Migration

To initiate or resume the full, dynamic wave-by-wave migration workflow:
```text
/orchestrate
```
To check progress, active wave, component statuses, and blockers at any time:
```text
/status
```

---

## User Experience & Slash Commands

| Command | Full Plugin Namespace | Purpose |
|:---|:---|:---|
| `/preflight` | `/drupal-migration-agent:preflight` | Non-destructive validation of configuration, paths, permissions, and Drupal markers. |
| `/discover` | `/drupal-migration-agent:discover` | Runs a standalone, read-only baseline audit on D7/D10 environments. |
| `/orchestrate` | `/drupal-migration-agent:orchestrate` | Gated by Preflight; guides setup and initiates the full end-to-end migration lifecycle. |
| `/status` | `/drupal-migration-agent:status` | Displays real-time phase progress, manifest statistics, and blockers. |

*Advanced Mode*: Individual specialist agents can still be directly invoked by advanced users (e.g. `drupal-migration:custom-module`).

---

## Factory vs. Consumer Artifact Ownership

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ARTIFACT OWNERSHIP MATRIX                        │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ CLASSIFICATION        │ REPOSITORY PATHS / PURPOSE                          │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Factory-Owned         │ • .claude-plugin/plugin.json, marketplace.json      │
│ (Immutable Template)  │ • agents/*/agent.md (13 specialist contracts)       │
│                       │ • skills/*/SKILL.md (12 migration skills)           │
│                       │ • references/**/*.md (7 technical references)       │
│                       │ • templates/*.md (report templates)                 │
│                       │ • tests/validate_factory.py, tests/schemas/*.json   │
│                       │ • migration.config.example.yml                      │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Consumer-Owned        │ • migration.config.yml (consumer workspace settings)│
│ (Project-Specific)    │ • External D7 Source Codebase (source.path)         │
│                       │ • External D10/11 Target Codebase (target.path)     │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Runtime-Generated     │ • state/migration-state.yml (mutable runtime state) │
│ (State & Inventory)   │ • state/migration-manifest.yml (static scope)       │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Persistent Evidence   │ • reports/preflight/PREFLIGHT-REPORT-*.md           │
│ (Audit Trail)         │ • reports/discovery/DISCOVERY-AUDIT-*.md            │
│                       │ • reports/migration-plan/MIGRATION-PLAN-*.md        │
│                       │ • reports/validation/VALIDATION-REPORT-*.md         │
│                       │ • reports/final-audit/FINAL-MIGRATION-AUDIT-*.md     │
│                       │ • logs/file-change-log/*.md                         │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

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
│   ├── preflight.md                 # /preflight non-destructive validation gate
│   ├── orchestrate.md               # /orchestrate entry point (preflight gated)
│   ├── discover.md                  # /discover baseline audit (preflight gated)
│   └── status.md                    # /status dashboard
│
├── agents/                          # 13 Specialized Migration Workers
│   ├── orchestrator.md              # Master orchestration, preflight gate & wave sequencing
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
│   ├── d7-analysis/SKILL.md         # Read-only D7 code/AST inspection heuristics
│   ├── d7-to-d10-mapping/SKILL.md   # Procedural-to-OOP architectural translation rules
│   ├── d10-architecture/SKILL.md    # Modern D10/D11 standards (PHP 8 attributes, DI)
│   ├── custom-module-migration/SKILL.md # 12-step module modernization playbook
│   ├── dependency-analysis/SKILL.md # 5-dimension coupling detection & DAG wave scheduler
│   ├── contrib-evaluation/SKILL.md  # 8-point contrib evaluation & D11 core removal rules
│   ├── theme-modernization/SKILL.md # PHPTemplate to Twig, libraries.yml, modern CSS/JS
│   ├── configuration-migration/SKILL.md # Variables to CMI YAML & configuration schemas
│   ├── migration-api/SKILL.md       # Core Migration API pipeline architect & ETL integrity
│   ├── testing/SKILL.md             # PHPUnit, PHPStan, PHPCS test runner playbooks
│   ├── behavioral-validation/SKILL.md # 12-point comparative behavioral validation matrix
│   └── integration-modernization/SKILL.md # External APIs, Guzzle clients, webhooks, QueueWorkers
│
├── references/                      # Deep Technical Knowledge Bases
│   ├── drupal-7/
│   │   ├── apis.md                  # D7 core APIs, database calls, globals, variables
│   │   └── hooks.md                 # D7 hooks to modern architecture catalog
│   ├── drupal-10/
│   │   ├── architecture.md          # D10/D11 services, plugins, CMI, routing
│   │   ├── plugin-types.md          # Plugin types & PHP 8 Attributes vs Annotations
│   │   └── twig-filters.md          # PHPTemplate functions to Twig syntax dictionary
│   └── migration-patterns/
│       ├── common-conversions.md    # Canonical before/after conversion patterns
│       └── field-mapping.md         # Field type & Migrate API process pipeline mappings
│
├── templates/                       # Standardized report & ticket templates
│   ├── preflight-report.md          # Preflight environment & configuration audit template
│   ├── discovery-report.md          # Discovery baseline audit report template
│   ├── dependency-report.md         # Dependency graph & wave schedule template
│   ├── migration-plan.md            # Component migration plan template
│   ├── blocked-item.md              # Standardized blocker ticket template
│   ├── validation-report.md         # Behavioral & data validation template
│   ├── final-audit.md               # Final migration sign-off report template
│   └── file-change-log.md           # Granular file modification audit template
│
├── reports/                         # Deterministic report output directories
├── tests/                           # Factory self-validation suite & JSON schemas
├── state/                           # Dual state management templates (state & manifest)
├── logs/                            # Audit logs (file change tracking)
│
├── migration.config.example.yml     # Canonical configuration template for consumer onboarding
├── LICENSE                          # Open-source MIT License
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
  - Factory Step 1: Claude Code Package & Architecture Transformation [COMPLETE]
  - Factory Step 2: Migration Skills & Knowledge Codification [COMPLETE]
  - Factory Step 3: Workflow Orchestration & Agent Coordination [COMPLETE]
  - Factory Step 4: Agent Operationalization & Execution Contracts [COMPLETE]
  - Factory Step 5: Self-Validation, Contract Testing & Runtime Readiness [COMPLETE]
  - Factory Step 6: Consumer Onboarding, Configuration Boundary & Preflight [COMPLETE]
  - Factory Step 7: Runtime Execution & Integration Hardening [COMPLETE]
  - Factory Step 8: End-to-End Workflow Validation [COMPLETE]

- **Migration Execution Lifecycle (When running against a real project)**:
  - Migration Step 0: Setup & Path Verification (Preflight Gate)
  - Migration Step 1: Project Discovery & Baseline Audit
  - Migration Step 2: Dependency Graph & Wave Scheduling
  - Migration Step 3: Contrib Compatibility Strategy
  - Migration Step 4: Component Migration Planning
  - Migration Step 5: Execution & Modernization (Modules, Themes, Config, Data)
  - Migration Step 6: Automated Testing & Static Analysis
  - Migration Step 7: Behavioral Validation
  - Migration Step 8: Final Audit & Sign-off

---

## Runtime Execution Hardening & Operational Model

Step 7 hardens the factory for execution against real consumer projects while preserving strict static/runtime boundaries:

### 1. Single-Writer State Authority & Command Routing
Commands (`/preflight`, `/discover`, `/orchestrate`, `/status`) act as entry points that dispatch work to the master `orchestrator` and specialist agents. All state mutations to `state/migration-state.yml` are serialized through the Orchestrator, which validates `agent_result` (v1.0) payloads before committing transitions.

### 2. Artifact Freshness & Metadata Lifecycle
Every generated report and plan contains metadata tracking its freshness state:
- `CURRENT`: Verified fresh; downstream agents may consume.
- `STALE`: Upstream configuration or source changed; re-evaluation scheduled.
- `INVALID`: Schema failure or corrupted output; rejected.
- `SUPERSEDED`: Replaced by a newer execution attempt.

### 3. Human Decision Gates
The framework distinguishes system recommendations from authoritative human approvals. Gates for custom module architecture, contrib replacements, and schema changes remain in `PENDING` status until explicitly approved by an engineering lead, preventing unapproved code mutations.

### 4. Recovery & Idempotent Resumption
- **Case A (Component Retry)**: Re-runs only the failed stage within `max_retries`.
- **Case B (Blocked Upstream)**: Pauses dependents until upstream component completes.
- **Case C (Global Blocker)**: Halts immediately on safety/isolation violations.
- **Case D (Interrupted Process)**: Reconciles state against on-disk change logs.
- **Case E (Resume)**: Automatically resumes from the lowest incomplete wave.
- **Case F (Stale Artifact)**: Re-runs producing agent upon input hash changes.

### 5. Runtime Capability Status
All static structures, schemas, and contracts are verified. Claude Code live execution and live subagent sandboxing remain explicitly marked:
`[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]`.

---

## End-to-End Workflow Validation (Step 8)

Step 8 executes an automated, deterministic **Factory Workflow Simulation** validating the complete migration chain from consumer configuration to final audit:
- **Configuration & Preflight**: Validates path non-overlap, secret exclusion, and Drupal markers.
- **Preflight Gating**: Ensures Discovery and Orchestration halt on preflight failure.
- **Manifest & State Decoupling**: Confirms static inventory is isolated from mutable state.
- **Dynamic Wave Topological Scheduling**: Simulates dependency DAG resolution and cyclic deadlock detection.
- **Human Decision Gating**: Enforces execution halts during `PENDING` plan reviews.
- **Agent Result Validation Gate**: Confirms Orchestrator validates schema and evidence before state mutation.
- **Failure Recovery Simulation**: Verifies Cases A through F recovery paths.
- **Final Audit Gate Evaluation**: Validates 8 acceptance gates for complete component accounting.

---

## Failure, Recovery & Production Hardening (Step 9)

Step 9 hardens the factory for edge cases, failures, unexpected interruptions, state corruption, and operational resilience:

### 1. Canonical Failure Taxonomy & Severity Model
- **8 Failure Classes**: `AGENT_FAILURE`, `TOOL_FAILURE`, `DEPENDENCY_FAILURE`, `CONFIG_FAILURE`, `SAFETY_FAILURE`, `ARTIFACT_FAILURE`, `HUMAN_GATE_FAILURE`, `PROCESS_FAILURE`.
- **5 Severity Levels**: `INFO`, `WARNING`, `MAJOR` (component remediation), `CRITICAL` (`BLOCKED_UPSTREAM` propagation), `GLOBAL_BLOCK` (immediate pipeline halt).

### 2. Deterministic Retry Policy & Recovery Boundaries
- Configurable `max_retries` (default: 3). Failed components enter `FAILED_RETRYABLE` up to the threshold, after which they transition to `BLOCKED` with human escalation.
- Retries re-enter at the designated remediation stage without re-running completed phases.
- The factory guarantees *safe resume and idempotent re-entry where the underlying operation supports idempotency*.
- Automatic arbitrary rollback is not claimed; rollbacks rely on the append-only `logs/file-change-log/` audit trail.

### 3. Partial Wave & Interruption Handling
- In dynamic waves with mixed results, completed components remain completed while failed components are isolated and downstream dependents are marked `BLOCKED_UPSTREAM`.
- On unexpected process termination, the Orchestrator reconciles uncommitted components in `IN_PROGRESS` back to `READY` or `FAILED_RETRYABLE` based on verified on-disk logs.

### 4. State Corruption Fail-Safe Protocol
- If `state/migration-state.yml` is corrupt or missing, the system triggers `GLOBAL_BLOCK` and halts. It preserves diagnostic evidence and refuses silent destructive overwriting.

### 5. Safe Resume Algorithm (9 Steps)
1. Load consumer configuration.
2. Validate state file schema and integrity.
3. Verify required artifacts and check freshness (`CURRENT`).
4. Verify global safety conditions (`global_block == false`, source read-only).
5. Reconcile incomplete components.
6. Evaluate dependency DAG.
7. Verify human decision gates.
8. Calculate executable topological wave.
9. Dispatch eligible work to specialist agents.

### 6. Production Safety Checklist
A 4-phase operational checklist covers Pre-Execution, Runtime Execution, Post-Interruption Recovery, and Final Sign-Off gates.

### 7. Runtime Status Boundary
All static structures, contracts, and simulation models are verified. Claude Code live execution and live Drupal environment testing remain explicitly marked:
`[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]`.

---

## Final Release Readiness & Distribution Audit (Step 10)

Step 10 performs the comprehensive final release audit verifying that the factory is structurally, contractually, and operationally ready for external distribution:
- **Repository Inventory**: 10 essential directories, 13 specialist agents, 12 migration skills, 7 technical references, 4 slash commands, and 8 report/plan templates.
- **Packaging & Metadata**: Validated v1.0.0 package metadata alignment across `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and `migration.config.example.yml`.
- **Open Source Licensing**: Standard MIT License file included matching manifest metadata.
- **Consumer Usability**: Verified self-contained onboarding walkthrough from zero knowledge to final audit.
- **Git Hygiene**: Strict `.gitignore` exclusions for OS, IDE, secret, and temporary scratch files.
- **Final Safety Matrix**: 15 cardinal safety rules, single-writer state authority, D7 source protection, and fail-safe recovery verified.
- **Release Status**: `RELEASE_READY_WITH_DECISIONS` (Static, contract, and simulation verification complete; external runtime verification and license confirmation remain final release decisions).
