---
name: configuration-migration
description: Configuration Management Interface (CMI), State API & Settings Modernization Playbook. Translates D7 persistent variables, system configurations, admin forms, runtime state, and environment settings into modern Drupal 10/11 architecture.
version: 1.1.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Configuration Management Interface (CMI), State API & Settings Modernization Skill

## Overview
This skill provides the operational heuristics, taxonomy rules, architectural targets, and migration strategies for re-engineering legacy Drupal 7 persistent variables (`variable_get/set/del`), system settings, administrative forms (`system_settings_form`), runtime application state, serialized values, and environment configurations into modern Drupal 10/11 architecture.

---

## Technical References
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
- [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)

---

## Semantic Distinction: Config vs State vs Content vs Environment vs Cache

Every legacy value must be classified into its authoritative architectural domain:

| Domain | Semantic Intent | Examples | Modern Drupal 10/11 Architecture |
|---|---|---|---|
| **Configuration** | Administrator-managed settings intended to be synchronized across environments via deployment pipelines. | Module feature toggles, API endpoints, display thresholds, notification templates. | **Config API** (`config/install/*.yml`, `config/schema/*.schema.yml`, `ConfigFormBase`). |
| **State** | Machine/runtime application state specific to an environment; non-synchronizable and non-exportable. | Last cron run timestamp (`my_module_last_cron`), processing counters, batch progress flags, sync markers. | **State API** (`\Drupal::state()` or injected `StateInterface`). |
| **Content / Data** | Business entities, user-generated records, or domain datasets. | User submissions, transactional records, log items stored in custom tables. | **Content Entities** (`@ContentEntityType`) or Database API. |
| **Environment / Secrets** | Deployment-specific infrastructure values, credentials, tokens, and secrets. | Database passwords, payment gateway private keys, client secrets, local dev flags. | **Settings API** (`$settings`, `settings.php`), `getenv()`, or **Key** module. **NEVER** commit secrets to CMI. |
| **Cache** | Derived, disposable computations that can be safely invalidated or purged at any time. | Parsed remote feed trees, cached computation graphs. | **Cache API** (`CacheBackendInterface`, cache bins). |

---

## Configuration API Modernization & Typed Schema

Where D7 variables represent administrator-managed settings:

### 1. Default Configuration File
Create `config/install/<module>.settings.yml`:
```yaml
api_endpoint: "https://api.example.com/v1"
timeout_seconds: 30
enable_logging: true
allowed_modes:
  - "standard"
  - "accelerated"
```

### 2. Typed Configuration Schema
Define strict typed schema in `config/schema/<module>.schema.yml`:
```yaml
<module>.settings:
  type: config_object
  label: '<Module Name> settings'
  mapping:
    api_endpoint:
      type: uri
      label: 'API Endpoint URL'
    timeout_seconds:
      type: integer
      label: 'Request timeout in seconds'
    enable_logging:
      type: boolean
      label: 'Enable debug logging'
    allowed_modes:
      type: sequence
      label: 'Permitted operation modes'
      sequence:
        type: string
        label: 'Mode identifier'
```

### 3. ConfigFormBase Re-engineering
Convert procedural `system_settings_form()` into an OOP Form class extending `ConfigFormBase`:
- Inject `ConfigFactoryInterface` via `create(ContainerInterface $container)`.
- Implement `getEditableConfigNames()` returning `['<module>.settings']`.
- Implement `buildForm(array $form, FormStateInterface $form_state)`.
- Implement `validateForm(array &$form, FormStateInterface $form_state)` for validation constraints.
- Implement `submitForm(array &$form, FormStateInterface $form_state)` persisting via `$this->config('<module>.settings')->set(...)->save()`.
- Register route in `<module>.routing.yml` with `_form: '\Drupal\<module>\Form\SettingsForm'` and `_permission: 'administer <module>'`.
- Register administrative menu link in `<module>.links.menu.yml`.

---

## State API Modernization

Where D7 variables represent runtime flags, synchronization state, or counters:
- **Injection**: Inject `Drupal\Core\State\StateInterface` into services, controllers, or plugins.
- **Procedural fallback**: `\Drupal::state()->get('my_module.last_run', 0)` and `\Drupal::state()->set('my_module.last_run', \Drupal::time()->getRequestTime())`.
- **Cleanup**: In `<module>.install:hook_uninstall()`, clean up state keys via `\Drupal::state()->delete('my_module.last_run')` or `\Drupal::state()->deleteMultiple([...])`.

---

## Settings & Environment Modernization (Rule 10 — Secret Isolation)

- **Zero Secrets in CMI**: API keys, access tokens, client secrets, encryption keys, and credentials must **NEVER** be committed to `config/install/*.yml` or exported to `config/sync/*.yml`.
- **Environment Overrides**: Use `settings.php` configuration overrides:
  ```php
  $config['my_module.settings']['api_key'] = getenv('MY_MODULE_API_KEY') ?: '';
  ```
- **Key Module Integration**: For secure key management, integrate with `Drupal\key\KeyRepositoryInterface`.
- **Ambiguous Credentials**: Any variable whose security sensitivity is ambiguous must be assigned `HUMAN_DECISION_REQUIRED`.

---

## Serialized & Complex Value Modernization

- **Structured Arrays**: Map serialized PHP arrays stored in D7 variables to YAML nested mappings or sequences in typed configuration schemas.
- **JSON Values**: Map JSON payloads to structured CMI schemas or typed state storage.
- **Opaque PHP Objects**: Serialized PHP objects (`O:8:"stdClass"...`) or non-scalar serialized data must be marked as `UNVERIFIED` or `HUMAN_DECISION_REQUIRED` for manual schema modeling. Never silently discard or corrupt serialized structures.

---

## 14 Configuration Migration Strategies

1. `DIRECT_CONFIG_MIGRATION`: 1:1 migration of scalar D7 variable into CMI configuration key.
2. `TRANSFORMED_CONFIG_MIGRATION`: Structural transformation, rename, or type cast during CMI migration.
3. `CONFIG_ENTITY_MIGRATION`: Migration of multi-instance or bundle configuration into Config Entity.
4. `STATE_MIGRATION`: Migration of runtime/dynamic variable into Drupal 10/11 State API.
5. `SETTINGS_MIGRATION`: Mapping of deployment-specific configuration to `$settings` in `settings.php`.
6. `ENVIRONMENT_MIGRATION`: Mapping of infrastructure endpoints or secrets to environment variables (`getenv()`).
7. `KEY_VALUE_MIGRATION`: Migration of custom collection state to Drupal's `keyvalue` storage.
8. `CONTENT_MIGRATION`: Re-engineering of business data stored in variables to Content Entities.
9. `CACHE_REBUILD`: Ephemeral cache state discarded in favor of modern Cache Backend bins.
10. `CUSTOM_MIGRATION`: Complex bespoke migration plugin (`@MigrateProcessPlugin`).
11. `REPLACED`: Legacy variable superseded by core/contrib equivalent (e.g. core media, CKEditor).
12. `OBSOLETE`: Obsolete D7 feature variable safely deprecated and omitted.
13. `HUMAN_DECISION_REQUIRED`: Ambiguous lifecycle, security classification, or complex dependency requiring human intervention.
14. `UNVERIFIED`: Dynamic variable names, unresolvable default expressions, or opaque objects requiring runtime verification.

---

## Zero-Omission Configuration & State Invariant
Every discoverable configuration, variable, state, and setting artifact must have:
1. Complete read/write/delete lifecycle traced (`CREATE -> READ -> MODIFY -> DELETE`).
2. Default value and default type accounted for.
3. Explicit modern architectural target assigned.
4. Validated configuration schema or state contract defined.
5. Terminal status assigned (`MIGRATED`, `REPLACED`, `OBSOLETE`, `EXCLUDED_WITH_REASON`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`).
