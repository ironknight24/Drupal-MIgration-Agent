---
name: testing
description: Automated test execution, validation standards, and quality gating across Drupal 7 and modern Drupal 10/11 architectures.
version: 1.11.0
user-invocable: false
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Automated Testing & Quality Assurance Playbook Skill

## Overview
This skill provides the procedural guidelines and runner configurations for establishing automated testing pipelines, static code analysis, custom PHP class testing, procedural hook replacement testing, event subscriber assertions, configuration schema validation, state API assertions, entity CRUD / revision / translation testing, entity access control verification, form validation & submission testing, AJAX response command verification, frontend assets, Views definitions, custom Views plugins, themes, Twig templates, preprocess hooks, dynamic runtime probe testing, and coding standards compliance across migrated Drupal 10 and Drupal 11 custom modules and themes.

---

## Technical References
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)

---

## Test Expectations for Modernized Code, Entities, Forms, Views, Themes & Dynamic Dependencies (Step 21)

When testing modernized custom OOP classes, services, procedural hook replacements, configuration/state artifacts, custom entities, Form API classes, Views/custom plugins, themes/Twig templates, and dynamic runtime dependencies, configure tests appropriate to their architectural responsibility:

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
5. **Entity Architecture & Field Validation (Step 16)**:
   - **Entity CRUD & Storage**: Test create, load, update, and delete operations via `EntityTypeManager` and custom storage handlers.
   - **Base & Config Field Definitions**: Assert all `baseFieldDefinitions()` return correct field types, default values, cardinalities, and constraints.
   - **Entity Access Control**: Assert that `EntityAccessControlHandler` returns expected `AccessResult::allowed()`, `AccessResult::forbidden()`, or `AccessResult::neutral()` across `view`, `update`, `delete`, and `create` operations for different user roles and ownership.
   - **Revision Management**: Assert that saving entities with `$entity->setNewRevision(TRUE)` creates valid revision records, preserves revision logs, timestamps, and authors, and supports loading specific revision IDs.
   - **Content Translation**: Assert that adding and updating translations (`$entity->addTranslation('es', ...)->save()`) persists translatable field values while leaving untranslatable fields synchronized.
   - **Entity Queries**: Test that Entity Queries correctly filter by base fields, bundle, language, access conditions, and reference targets.
6. **Form & AJAX Validation (Step 17)**:
   - **Form Build & Render**: Assert `buildForm()` generates expected form element render array with required properties and `#attached` libraries.
   - **Form Validation Handlers**: Assert `validateForm()` flags invalid inputs via `$form_state->setErrorByName()` and rejects malicious/corrupt input.
   - **Form Submission Handlers**: Assert `submitForm()` executes expected database/entity/config mutations and sets expected redirects (`$form_state->setRedirect()`).
   - **AJAX Response & Commands**: Assert AJAX callbacks return valid `AjaxResponse` objects containing expected `CommandInterface` instances (`ReplaceCommand`, `HtmlCommand`, `InvokeCommand`, `MessageCommand`).
   - **Multistep Rebuild State**: Assert multi-step forms correctly transition across steps using `$form_state->setRebuild(TRUE)` and persist state across rebuild requests.
   - **CSRF & Access Checks**: Assert forms validate CSRF tokens on submission and enforce route/entity permission constraints.
7. **Frontend JavaScript, CSS & Library Validation (Step 18)**:
   - **Library Parsing & SMACSS**: Assert `<module>.libraries.yml` parses cleanly, specifies valid SMACSS categories (`base`, `layout`, `component`, `state`, `theme`), and declares required core dependencies (`core/drupal`, `core/drupalSettings`, `core/once`, `core/jquery`).
   - **`once()` Idempotency**: Assert JavaScript behaviors utilize `once()` to guarantee idempotent execution across multiple AJAX reattachments.
   - **`drupalSettings` Injection**: Assert PHP attachment pipelines correctly inject settings under `$form['#attached']['drupalSettings']` and scripts read them without errors.
   - **Accessibility & Focus**: Assert dynamic DOM updates update ARIA attributes (`aria-live`, `aria-expanded`) and manage focus correctly.
8. **Views & Custom Plugins Validation (Step 19)**:
   - **Views Configuration Schema**: Assert all `config/install/views.view.*.yml` files conform to core views schema definitions without schema violations.
   - **Custom Plugin Execution**: Assert custom `@ViewsField`, `@ViewsFilter`, `@ViewsArgument`, `@ViewsSort`, `@ViewsRelationship`, and `@ViewsArea` plugins execute accurately, render expected output, and properly inject services via `ContainerFactoryPluginInterface`.
   - **Query Alterations**: Assert `hook_views_query_alter()` implementations correctly modify SQL conditions, joins, and sorting without syntax errors or injection vulnerabilities.
   - **Access Control & Cache Metadata**: Assert Views enforce access control permissions and bubble correct cache tags (`node_list`, `user:uid`), cache contexts (`user.roles`, `url.query_args`), and cache max-age.
9. **Themes, Twig Templates & Preprocess Validation (Step 20)**:
   - **Twig Template Syntax & Escaping**: Assert zero PHP tags exist in `.html.twig` templates; verify Twig auto-escaping and safe filter usage.
   - **Preprocess Variable Formatting**: Assert `<theme>_preprocess_HOOK()` functions compute expected variables and attach required bubbleable cache metadata.
   - **Theme Settings Schema Adherence**: Assert `<theme>.settings.yml` adheres to `config/schema/<theme>.schema.yml`.
   - **Accessibility & ARIA Structure**: Assert theme templates render semantic HTML5 landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`) and valid ARIA attributes.
   - **Asset Library Attachments**: Assert theme templates and preprocess hooks attach registered libraries via `{{ attach_library('theme/library') }}`.
10. **Dynamic Dependencies & Runtime Probe Validation (Step 21)**:
    - **Plugin Manager Discovery**: Assert custom Plugin Managers discover all registered `@Handler` or custom plugin classes without exceptions.
    - **Dynamic Callables & Factories**: Test factory services resolving dynamic handler strings to concrete typed service instances.
    - **Runtime Probe Safety**: Assert all runtime probe specifications are non-destructive and read-only; where runtime CLI is absent, verify explicit `[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]` status.
11. **External Integrations, APIs, Webhooks & Secret Testing (Step 22)**:
    - **Guzzle MockHandler & HTTP Client Testing**: Assert API client services handle 200 OK, 4xx client errors, 5xx server errors, network timeouts, and JSON serialization using Guzzle `MockHandler` and `HandlerStack`.
    - **Webhook Signature & Payload Verification**: Assert webhook controllers reject invalid HMAC signatures, validate CSRF tokens, and process incoming JSON/XML payloads safely.
    - **Secret Protection & Key Module Mocking**: Assert API keys and credentials are retrieved via `KeyRepositoryInterface` or environment variables with zero hardcoded secrets.
    - **Resilience & Idempotency Testing**: Assert exponential backoff retry loops, idempotency headers, and dead-letter queue routing execute correctly under simulated failure conditions.
12. **Public API & Business Logic Parity**:
    - Author PHPUnit Unit tests targeting domain calculations, validation algorithms, and state transitions.
13. **Integration, Custom Database & Repository Operations**:
    - Author PHPUnit Kernel tests targeting custom entity CRUD, custom database table repository queries, dynamic SQL filters, and configuration schema adherence.
    - Verify transaction rollback semantics: ensure failed operations rollback completely without leaving orphaned records.
14. **Data Migration ETL Pipeline Tests**:
    - Author Kernel migration tests verifying source-to-destination mappings, serialized payload transformations, entity reference lookups, revision transfers, translation mappings, and rollback behavior.
15. **Error Handling & Edge Cases**:
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
- **Usage**: Tests database queries, service container integration, Entity API operations, entity revisions, translations, and CMI schema adherence.
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
