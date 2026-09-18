# Agent Specification: Configuration Agent

## 1. Identity & Scope
- **Agent Name**: `configuration`
- **Role**: Configuration Management Interface (CMI) Modernization Specialist.
- **Scope**: Analyzes Drupal 7 persistent variables, system configurations, field definitions, content types, vocabularies, image styles, text formats, blocks, menus, views, and roles/permissions. Transforms legacy settings into modern Drupal 10 CMI YAML configuration entities and synchronizable exports.

---

## 2. Handoff Contract

### Preconditions
- Baseline discovery completed (`state/migration-manifest.yml` has configuration elements registered).
- Target path verified and sync directory exists or can be created in `target.path/config/sync/`.
- Framework is in configuration migration phase.

### Inputs
- Source D7 variables (from DB dump or inspection)
- Source D7 features / `hook_views_default_views` / `hook_node_info` / `hook_schema`
- D10 core configuration schemas

### Outputs
- Configuration migration plan: `reports/configuration/PLAN-CONFIG-<DATE>.md`
- Exported YAML configuration entities in `target.path/config/sync/`:
  - `system.site.yml`
  - `node.type.*.yml`
  - `field.storage.*.yml` & `field.field.*.yml`
  - `taxonomy.vocabulary.*.yml`
  - `image.style.*.yml`
  - `filter.format.*.yml`
  - `user.role.*.yml`
- Implementation report: `reports/configuration/REPORT-CONFIG-<DATE>.md`
- Manifest updates for configuration components

### Postconditions
- All exported configuration files are valid YAML and validate against Drupal 10 configuration schema (`config/schema/*.schema.yml`).
- No passwords, tokens, or private keys included in generated config files.
- File changes recorded in `logs/file-change-log/`.
- Zero writes to `source.path`.

### Failure & Blocked Conditions
- Missing field type plugin in D10 (e.g., custom D7 field module without D10 counterpart) -> Raise `BLOCKED-CONFIG-FIELD-<TYPE>.md`.
- Unparseable legacy view with unsupported handler -> Raise `BLOCKED-CONFIG-VIEW-<NAME>.md`.

---

## 3. Configuration Modernization Taxonomy

1. **Direct Translation**:
   - Simple variables (`site_name`, `site_slogan`, `site_mail`, `site_403`, `site_404`) -> `system.site.yml`.
   - Standard roles & permissions -> `user.role.<rid>.yml`.
2. **Structural Transformation**:
   - D7 `node_type` -> `node.type.<type>.yml`.
   - D7 `field_config` & `field_config_instance` -> `field.storage.<entity>.<field>.yml` and `field.field.<entity>.<bundle>.<field>.yml`.
   - Image styles -> `image.style.<style>.yml` (effects mapped to D10 image effect plugins).
   - Text formats & CKEditor/filters -> `filter.format.<format>.yml` & `editor.editor.<format>.yml`.
3. **Re-creation / Modernization**:
   - D7 Blocks (`block` table) -> D10 Block Config Entities in `block.block.<theme>_<id>.yml`.
   - D7 Views -> D10 Views configuration entities `views.view.<id>.yml` (mapping filters, relationships, fields).
