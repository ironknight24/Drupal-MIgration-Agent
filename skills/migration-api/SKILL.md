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
- [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)

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

## Custom Database & Data-Model Migration Strategies

For every custom database table and stored data model discovered in legacy D7 custom modules, apply one of the 10 standardized migration strategies:

1. **`DIRECT_MIGRATION`**: Direct SQL transfer into a corresponding D10 custom repository table using a `SqlBase` source plugin.
2. **`TRANSFORMED_MIGRATION`**: Source rows undergo schema normalization, column renaming, or serialized payload decoding into destination schema.
3. **`ENTITY_MIGRATION`**: Custom table rows are migrated into a modern Drupal Content Entity type (`entity:<custom_entity>`) via `migration_lookup` for referenced entities.
4. **`CONFIG_MIGRATION`**: Custom table rows representing static module configuration or settings are transformed into CMI YAML configs (`config/sync/<module>.settings.yml`).
5. **`STATE_MIGRATION`**: Transient flags, sequence numbers, or timestamps are migrated into Drupal State API (`\Drupal::state()`).
6. **`CUSTOM_MIGRATION`**: Bespoke multi-step Migration plugins for complex many-to-one or one-to-many data models.
7. **`REPLACED`**: Data is migrated into an existing core or contrib entity (e.g., core `media` or `paragraphs`).
8. **`OBSOLETE`**: Table contains legacy temporary cache, obsolete logs, or abandoned data; documented and excluded.
9. **`HUMAN_DECISION_REQUIRED`**: Data semantics or entity associations cannot be proven automatically.
10. **`UNVERIFIED`**: Dynamic or encrypted table data requiring runtime human inspection.

### Serialized Data & Transformation Pipelines
- When source fields contain PHP serialized strings (`serialize()` / `unserialize()`), utilize a custom process plugin (`d7_unserialize` or `unserialize_to_json`) to safely parse payloads before saving to target properties.
- Guard against class-instantiation vulnerabilities during deserialization (`allowed_classes => false`).

---

## Data Integrity Verification & Checksums

Before certifying a data migration pipeline as complete:
1. **Row Count & Semantic Cardinality Reconciliation**: Run comparison queries to verify that total source records match total destination records:
   $$\text{Source Row Count} = \text{Destination Row Count} + \text{Documented Excluded Count}$$
   Where one-to-many or many-to-one transformations occur, verify semantic relationship cardinality.
2. **Entity Reference Integrity**: Verify that no `migration_lookup` returned empty or stub IDs where valid parent records existed (`uid`, `nid`, `tid`, `fid`).
3. **Serialized Payload Verification**: Confirm serialized payloads are cleanly parsed and mapped without data truncation or corruption.
4. **Character Encoding Verification**: Confirm UTF-8 integrity; verify zero truncated multibyte strings.
5. **Rollback Verification**: Validate that migration configurations support clean rollback (`drush migrate:rollback <migration_id>`) without database corruption.
