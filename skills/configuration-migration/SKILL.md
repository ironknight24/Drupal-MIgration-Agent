---
name: configuration-migration
description: Configuration Management Interface (CMI) Modernization Playbook. Translates D7 persistent variables, fields, content types, and settings into CMI YAML files.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Configuration Management Interface (CMI) Modernization Skill

## Overview
This skill provides the operational heuristics and taxonomy rules for translating legacy Drupal 7 persistent variables, system configurations, field definitions, and views into modern Drupal 10/11 Configuration Management Interface (CMI) YAML entities.

---

## Technical References
- [Drupal 10 Architecture Reference](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-10/architecture.md)
- [Common Migration & Modernization Patterns](file:///Users/deepak/Desktop/Projects/drupal-migration/references/migration-patterns/common-conversions.md)
- [Field Type & Data Migration Mapping Reference](file:///Users/deepak/Desktop/Projects/drupal-migration/references/migration-patterns/field-mapping.md)

---

## Configuration Taxonomy & Modernization Routing

Categorize legacy configuration items into their appropriate modern targets:

### 1. Simple Configuration Objects
Single-instance key/value configuration deployed across environments:
- Legacy: `variable_get('site_name', 'Drupal')` -> Target: `system.site.yml` (`name`).
- Legacy: Custom module settings `variable_get('mymodule_timeout', 30)` -> Target: `config/install/mymodule.settings.yml`.
- Schema: Must define type mappings in `config/schema/mymodule.schema.yml`.

### 2. Configuration Entities
Structured, exportable entities with UUIDs, labels, and administrative interfaces:
- **Content Types**: D7 `node_type` table -> `node.type.<bundle>.yml`.
- **Field Storage**: D7 `field_config` -> `field.storage.<entity>.<field>.yml`.
- **Field Instances**: D7 `field_config_instance` -> `field.field.<entity>.<bundle>.<field>.yml`.
- **Taxonomy Vocabularies**: D7 `taxonomy_vocabulary` -> `taxonomy.vocabulary.<vid>.yml`.
- **Roles & Permissions**: D7 `role` & `role_permission` -> `user.role.<rid>.yml`.
- **Image Styles**: D7 `image_styles` & effects -> `image.style.<style_name>.yml`.
- **Views**: D7 code or DB views -> `views.view.<view_id>.yml`.

### 3. State API (Non-Exportable Runtime Data)
Dynamic, environment-specific, non-synchronizable values:
- Synchronization timestamps, last cron run times, ephemeral API counters.
- Modern Target: `\Drupal::state()` or injected `StateInterface` (`$this->state->get(...)`).
- **Never** export dynamic runtime state into `config/sync/`.

---

## Security & Credential Protection Standards (Rule 10)
- **Zero Secrets Committed**: Passwords, API tokens, encryption keys, and private webhooks must **NEVER** be stored in CMI YAML files.
- **Environment Resolution**: Use `settings.php` overrides (`$config['mymodule.settings']['api_key'] = getenv('API_KEY');`) or the contributed `key` module for secret management.
