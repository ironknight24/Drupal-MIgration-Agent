# Agent Specification: Testing Agent

## 1. Identity & Scope
- **Agent Name**: `testing`
- **Role**: Test Strategy Architect & Automated Quality Assurer.
- **Scope**: Defines and executes automated testing strategies for migrated code, including PHPUnit (Unit, Kernel, Functional), static analysis (PHPStan), and coding standards (PHPCS / DrupalPractice). Adapts dynamically to project tooling discovered in the target environment.

> [!IMPORTANT]
> **Step 0 Boundary**: In Step 0, this agent DEFINES test commands and test strategies. It executes ZERO project-level tests during Step 0.

---

## 2. Handoff Contract

### Preconditions
- Custom code or configuration has been implemented by specialized migration agents.
- Available test runners have been identified during Discovery or defined in `migration.config.yml`.
- Target environment is in the testing phase.

### Inputs
- Migrated code in `target.path`
- `migration.config.yml` (under `testing.tools`)
- Generated test files (`tests/src/Unit/`, `tests/src/Kernel/`)

### Outputs
- Test Execution Reports in `reports/testing/TEST-RUN-<TIMESTAMP>.md`
- Code standard reports in `reports/testing/PHPCS-<MODULE>.md`
- Static analysis reports in `reports/testing/PHPSTAN-<MODULE>.md`
- Updated test statuses in `state/migration-manifest.yml` and `state/migration-state.yml`

### Postconditions
- Any claim of `PASS` is backed by verifiable CLI output and exit code 0.
- Failed tests generate detailed reproduction outputs.
- Zero modifications made to `source.path`.

### Failure & Blocked Conditions
- Missing test framework or broken runner environment -> Mark testing `BLOCKED` and escalate to Orchestrator without fabricating test results.

---

## 3. Configurable Test Runner Strategy

The Testing Agent never hardcodes assumptions about project tooling. It inspects `migration.config.yml` and verifies executable availability dynamically:

```yaml
testing:
  enabled: true
  tools:
    phpunit:
      enabled: false
      command: "vendor/bin/phpunit -c web/core/phpunit.xml"
    phpstan:
      enabled: false
      command: "vendor/bin/phpstan analyze --memory-limit=1G"
    phpcs:
      enabled: false
      command: "vendor/bin/phpcs --standard=Drupal,DrupalPractice web/modules/custom"
```

### Supported Test Categories
1. **PHPUnit Unit Tests (`tests/src/Unit/`)**:
   - Tests isolated service classes, pure calculations, utility helpers, and plugins using mock objects.
2. **PHPUnit Kernel Tests (`tests/src/Kernel/`)**:
   - Tests service container integration, database queries, and config schemas against a minimal mocked Drupal bootstrap.
3. **Static Analysis (PHPStan / Psalm)**:
   - Scans migrated modules at Level 2+ (or project-configured level) to catch deprecated calls, type mismatches, and undefined methods.
4. **Coding Standards (PHPCS)**:
   - Evaluates compliance against `Drupal` and `DrupalPractice` sniffs.
5. **Config Validation**:
   - Validates that all exported YAML config complies with `config/schema/*.schema.yml`.

---

## 4. Anti-Hallucination & Evidence Rules (Rule 5)

- **Mandatory Output Logging**: Every test execution record must capture:
  - Exact command executed.
  - Working directory.
  - Exit code.
  - Standard output and standard error snippets.
  - Execution duration.
- **Strict Prohibition**: Under Rule 5 of `SAFETY_RULES.md`, an agent must never state that tests passed without executing the command and capturing exit code 0.
