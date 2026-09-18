---
name: testing
description: Test Strategy & Automated Quality Assurance Playbook. Configures and validates PHPUnit test suites, custom class autoloading, constructor DI verification, hook replacement testing, event subscriber assertions, config schema validation, state persistence testing, PHPStan static analysis, and PHPCS coding standards.
version: 1.3.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Automated Testing & Quality Assurance Playbook Skill

## Overview
This skill provides the procedural guidelines and runner configurations for establishing automated testing pipelines, static code analysis, custom PHP class testing, procedural hook replacement testing, event subscriber assertions, configuration schema validation, state API assertions, and coding standards compliance across migrated Drupal 10 and Drupal 11 custom modules and themes.

---

## Technical References
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)

---

## Test Expectations for Migrated Custom PHP Classes, Services, Hooks & Configuration

When testing modernized custom OOP classes, services, procedural hook replacements, and configuration/state artifacts, configure tests appropriate to their architectural responsibility:
1. **Class Autoloading & Container Construction**:
   - Verify class is discoverable via Composer PSR-4 without manual includes.
   - Verify service builds from `<module>.services.yml` container definition without container exceptions.
2. **Constructor & Dependency Injection Validation**:
   - Test constructor parameter handling, type assertions, and default values.
   - Assert all required services are properly injected rather than accessed statically.
3. **Hook Replacement & Event Subscriber Validation**:
   - Assert that event subscribers properly handle dispatched custom events with expected arguments.
   - Assert that modernized form alter handlers (`hook_form_alter` delegating to service) attach expected elements, validation callbacks, and submit handlers.
   - Assert that modernized route controllers, form classes, and custom access check services return expected `AccessResult` and HTTP responses.
4. **Configuration Schema, ConfigFormBase & State API Validation**:
   - Assert default configuration installs cleanly from `config/install/<module>.settings.yml`.
   - Validate configuration against `config/schema/<module>.schema.yml` using `SchemaCheckTestTrait`.
   - Assert `ConfigFormBase` builds, validates, and persists configuration correctly into CMI.
   - Assert State API persistence (`\Drupal::state()`) stores, retrieves, and deletes runtime state flags and timestamps correctly.
   - Assert Secret Isolation (Rule 10): verify zero credentials/API keys exist in exported CMI YAML files.
5. **Public API & Business Logic Parity**:
   - Author PHPUnit Unit tests targeting domain calculations, validation algorithms, and state transitions.
6. **Integration, Custom Database & Repository Operations**:
   - Author PHPUnit Kernel tests targeting custom entity CRUD, custom database table repository queries, dynamic SQL filters, and configuration schema adherence.
   - Verify transaction rollback semantics: ensure failed operations rollback completely without leaving orphaned records.
7. **Data Migration ETL Pipeline Tests**:
   - Author Kernel migration tests verifying source-to-destination mappings, serialized payload transformations, entity reference lookups, and rollback behavior.
8. **Error Handling & Edge Cases**:
   - Assert exception throwing on invalid inputs, missing dependencies, database constraint violations, or failed external requests.

---

## Supported Test Suites & Methodologies

### 1. PHPUnit Unit Tests (`tests/src/Unit/`)
- **Scope**: Isolated testing of service classes, plugins, calculations, and pure business logic.
- **Execution**: No database or Drupal bootstrap required. Dependencies are mocked using PHPUnit mock builder or Prophecy.
- **Execution Command**:
  ```bash
  vendor/bin/phpunit -c web/core/phpunit.xml web/modules/custom/<MODULE>/tests/src/Unit/
  ```

### 2. PHPUnit Kernel Tests (`tests/src/Kernel/`)
- **Scope**: Integration testing with a minimal, in-memory virtual Drupal bootstrap.
- **Usage**: Tests database queries, service container integration, Entity API operations, and CMI schema adherence.
- **Execution Command**:
  ```bash
  vendor/bin/phpunit -c web/core/phpunit.xml web/modules/custom/<MODULE>/tests/src/Kernel/
  ```

### 3. Static Analysis (PHPStan)
- **Scope**: Detects deprecated API calls, type mismatches, missing return types, and dead code paths.
- **Configuration**: Level 2 baseline (escalating to Level 6+ for modern D11 readiness).
- **Execution Command**:
  ```bash
  vendor/bin/phpstan analyze --memory-limit=1G web/modules/custom/<MODULE>
  ```

### 4. Drupal Coding Standards (PHPCS)
- **Scope**: Enforces official Drupal and DrupalPractice standards.
- **Execution Command**:
  ```bash
  vendor/bin/phpcs --standard=Drupal,DrupalPractice web/modules/custom/<MODULE>
  ```

### 5. Configuration Schema Validation
- **Scope**: Verifies that all exported YAML configurations in `config/sync/` or `config/install/` have complete, valid type definitions matching `config/schema/*.schema.yml`.

---

## Anti-Hallucination & Empirical Evidence Rules (Rule 5)

```text
Under Rule 5 of SAFETY_RULES.md, an agent must NEVER claim a test passed,
a module conforms to standards, or code is error-free without executing
the CLI command and capturing verifiable output.
```

Every recorded test run must document:
1. Exact command string executed.
2. Current working directory.
3. Execution timestamp and duration.
4. Process exit code (`0` for PASS, non-zero for FAIL).
5. Raw stdout/stderr terminal output snippet.
