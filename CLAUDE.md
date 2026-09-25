# CLAUDE.md - Drupal Migration Agent Framework Directives

> **CRITICAL RUNTIME DIRECTIVE FOR CLAUDE CODE**:
> You are operating inside the `drupal-migration-agent` framework. All operations MUST strictly adhere to this file, `SAFETY_RULES.md`, and `AGENT_PROTOCOL.md`.

---

## 1. MANDATORY ZERO-SEARCH CONFIG CONFINEMENT (CARDINAL RULE 18)

1. **Config-First Path Computation**:
   - ALWAYS read `migration.config.yml` in the project root before performing any file lookup, search, or module operation.
   - For any custom module `<MODULE_NAME>`, programmatically construct the exact paths:
     - `SOURCE_MODULE_PATH = os.path.join(source.path, source.custom_modules_path, MODULE_NAME)`
     - `TARGET_MODULE_PATH = os.path.join(target.path, target_custom_modules_path, MODULE_NAME)`
2. **Absolute Zero-Search Prohibition**:
   - **DO NOT** search additional working directories, parent directories (`..`), sibling repositories, or the workspace root using `glob`, `grep`, `find`, `FileSearch`, or directory walking.
   - **DO NOT** look for similarly named modules in adjacent folders or unrelated repositories.
   - Open and inspect **ONLY** `SOURCE_MODULE_PATH` and `TARGET_MODULE_PATH`.
3. **Existence & Containment Gate**:
   - Directly inspect if `SOURCE_MODULE_PATH` exists on disk at that exact path.
   - If `SOURCE_MODULE_PATH` does NOT exist: **HALT IMMEDIATELY** with an error:
     ```text
     [ERROR] Source module '<MODULE_NAME>' not found at configured path:
             <SOURCE_MODULE_PATH>
     Broad workspace/repository search is strictly prohibited (Rule 16 & Rule 18).
     Please verify 'source.path' and 'source.custom_modules_path' in migration.config.yml.
     ```
   - Never search outside `SOURCE_MODULE_PATH`.

---

## 2. CARDINAL SAFETY RULES (NON-NEGOTIABLE)

- **RULE 1 (Source Protection)**: Never delete or unlink files in `source.path`.
- **RULE 2 (Source Immutability)**: `source.path` is strictly **READ-ONLY**. Never edit, format, or mutate D7 files.
- **RULE 3 (Mutation Logging)**: Log every target file modification into `logs/file-change-log/`.
- **RULE 4 (Evidence Requirement)**: Never declare a component migrated without forensic test/audit evidence.
- **RULE 9 (No Git Operations)**: Never execute git commits or branch operations automatically.
- **RULE 10 (Secret Isolation)**: Never expose API keys, passwords, or credentials in reports.
- **RULE 16 (Strict Path Confinement)**: Confine all operations strictly to configured `source.path` and `target.path`. Prohibit adjacent directory searching.
- **RULE 17 (Pure D10 Standards for New Modules)**: If module does not exist in `target.path`, scaffold from scratch with 100% pure modern D10 OOP standards (PSR-4, Dependency Injection, CMI YAML, Twig) preserving all business behavior.
- **RULE 18 (Mandatory Step 0 Zero-Search Exact Path Derivation)**: Strictly compute exact paths from `migration.config.yml` and never search the wider repository.

---

## 3. COMMAND & AGENT ROUTING

When invoked with commands or natural language migration requests:
- `/migrate-module <MODULE_NAME>` or `/orchestrate <MODULE_NAME>`:
  - Read `commands/migrate-module.md`.
  - Activate `agents/custom-module/agent.md` with `skills/custom-module-migration/SKILL.md`.
  - Introspect `<target.path>/composer.json` and `<target.path>/web/modules/contrib/` to auto-resolve dependencies before raising blockers.
  - Confine target writes strictly to `<target.path>/<target_custom_modules_path>/<MODULE_NAME>/**/*`.
- `/discover`:
  - Read `commands/discover.md`.
  - Activate `agents/discovery/agent.md` in strictly read-only mode.
- `/orchestrate`:
  - Read `commands/orchestrate.md`.
  - Activate `agents/orchestrator/agent.md`.
- `/preflight`:
  - Read `commands/preflight.md` and execute checks PRE-01 through PRE-09.
- `/status`:
  - Read `commands/status.md`.
