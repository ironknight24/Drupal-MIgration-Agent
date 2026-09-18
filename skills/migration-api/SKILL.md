---
name: migration-api
description: Drupal Core Migration API Architect & ETL Pipeline Playbook. Configures source, process, and destination plugins, relational dependencies, and data integrity verification.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Drupal Core Migration API Architect Skill

## Overview
This skill provides the architectural guidelines, plugin pipeline configurations, and relational sequencing workflows for constructing robust, reproducible data migrations from Drupal 7 to modern Drupal 10 and Drupal 11 using the core Migration API (`migrate`, `migrate_drupal`, `migrate_plus`).

---

## Technical References
- [Field Type & Data Migration Mapping Reference](file:///Users/deepak/Desktop/Projects/drupal-migration/references/migration-patterns/field-mapping.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-10/plugin-types.md)

---

## Relational Pipeline Sequencing

To avoid foreign key constraint violations and orphaned references, migrations must execute in strict dependency order:

```text
1. User Roles (d7_user_role)
   ↓
2. User Accounts (d7_user)
   ↓
3. Taxonomy Vocabularies (d7_taxonomy_vocabulary)
   ↓
4. Taxonomy Terms (d7_taxonomy_term)
   ↓
5. Managed Files & Media (d7_file)
   ↓
6. Custom SQL Tables & Independent Entities
   ↓
7. Nodes & Base Content (d7_node)
   ↓
8. Node Revisions & Historical Moderation (d7_node_revision)
   ↓
9. Entity References, Comments & Menu Links (d7_menu_links, d7_comment)
```

---

## Migration Architecture: Source, Process & Destination

### 1. Source Plugin Definition
Connects to the legacy D7 database (read-only) via the `$databases['migrate']` connection:

```yaml
source:
  plugin: d7_node
  node_type: article
```

### 2. Process Plugin Pipeline
Transforms incoming source fields into target entity properties using chainable plugins:
- `migration_lookup`: Looks up destination IDs based on prior migration runs.
- `sub_process`: Iterates over complex multi-property fields (e.g. image, link).
- `static_map`: Translates discrete status values or format names.
- `default_value`: Sets defaults when source fields are NULL.
- `callback`: Invokes safe helper functions for data normalization.

### 3. Destination Plugin Definition
Persists mapped data into Drupal 10/11 entities:

```yaml
destination:
  plugin: 'entity:node'
  default_bundle: article
```

---

## Data Integrity Verification & Checksums

Before certifying a data migration pipeline as complete:
1. **Count Reconciliation**: Run comparison queries to verify that total source records match total destination records:
   $$\text{Source Count} = \text{Destination Count} + \text{Documented Excluded Count}$$
2. **Entity Reference Integrity**: Verify that no `migration_lookup` returned empty or stub IDs where valid parent records existed.
3. **Character Encoding Verification**: Confirm UTF-8 integrity; verify zero truncated multibyte strings.
4. **Rollback Verification**: Validate that migration configurations support clean rollback (`drush migrate:rollback <migration_id>`) without database corruption.
