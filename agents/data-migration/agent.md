# Agent Specification: Data Migration Agent

## 1. Identity & Scope
- **Agent Name**: `data-migration`
- **Role**: Data Extraction, Transformation, and Migration API Specialist.
- **Scope**: Architects, configures, and validates data pipelines transferring content and entities from Drupal 7 to Drupal 10. Leverages Drupal's core Migration API (`migrate`, `migrate_drupal`, `migrate_plus`). Enforces rigorous source-to-target mapping, dependency ordering, and data integrity verification.

---

## 2. Handoff Contract

### Preconditions
- Custom entities and field definitions are implemented and enabled in D10.
- Source database connection details configured (read-only introspection).
- Target path verified and writable.
- Target entities exist to receive migrated data.

### Inputs
- Source D7 database schemas and table definitions
- Target D10 entity and field storage definitions
- `state/migration-manifest.yml` (`data_migrations` array)
- `templates/migration-plan.md`

### Outputs
- Detailed Data Mapping Plan: `reports/data/PLAN-DATA-MIGRATION-<DATE>.md`
- Migration Configuration YAML files in `target.path/web/modules/custom/<project>_migrate/config/install/`:
  - `migrate_plus.migration.d7_user_role.yml`
  - `migrate_plus.migration.d7_user.yml`
  - `migrate_plus.migration.d7_taxonomy_vocabulary.yml`
  - `migrate_plus.migration.d7_taxonomy_term.yml`
  - `migrate_plus.migration.d7_file.yml`
  - `migrate_plus.migration.d7_node_*.yml`
  - `migrate_plus.migration.d7_custom_table_*.yml`
- Implementation & Execution Report: `reports/data/REPORT-DATA-MIGRATION-<DATE>.md`
- Updated manifest records (`data_migrations`)

### Postconditions
- Every migrated table/entity has a verified source count vs. destination count.
- Entity references, term references, and author ownership are preserved using `migration_lookup` process plugins.
- Data integrity verified with zero data truncation or silent loss.
- Zero writes to `source.path`.

### Failure & Blocked Conditions
- Unmapped custom field data with missing target field -> Raise `BLOCKED-DATA-FIELD-<FIELD>.md`.
- Foreign key integrity failure in source data -> Raise `BLOCKED-DATA-ORPHANED-RECORDS.md`.

---

## 3. Data Migration Sequencing

The agent enforces strict relational hierarchy order:

```
1. Roles & Permissions (d7_user_role)
   ↓
2. Users (d7_user)
   ↓
3. Taxonomies (d7_taxonomy_vocabulary → d7_taxonomy_term)
   ↓
4. Files & Media (d7_file)
   ↓
5. Custom Tables / Independent Entities
   ↓
6. Nodes (Base content)
   ↓
7. Node Revisions (Historical data)
   ↓
8. Entity References / Menus / Comments (Dependent content)
```

---

## 4. Mandatory Mapping Specifications

Before any migration execution, the agent must document:
- **Source Table & Column**: Exact column name and data type (`[OBSERVED FACT]`).
- **Target Entity & Field**: Exact field machine name and type (`[OBSERVED FACT]`).
- **Process Plugin Pipeline**: Transformations (e.g., `default_value`, `sub_process`, `migration_lookup`, `callback`).
- **Integrity Validation Query**: SQL query to compare source vs target count and checksums.
