# Drupal 7 to Drupal 10/11 Field Type & Data Migration Mapping Reference

This reference details the canonical mapping between Drupal 7 field types and modern Drupal 10/11 field types, widgets, formatters, and Migration API process pipelines.

---

## 1. Field Type Canonical Mapping Table

| Drupal 7 Field Type | Target Drupal 10/11 Field Type | Target Storage Module | D10/D11 Default Widget | D10/D11 Default Formatter | Notes / Schema Conversion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `text` | `string` or `text` | Core `text` | `string_textfield` | `string` | Short text (<=255 chars) maps to `string`. Formatted text maps to `text`. |
| `text_long` | `text_long` | Core `text` | `text_textarea` | `text_default` | Long formatted body without summary. |
| `text_with_summary` | `text_with_summary`| Core `text` | `text_textarea_with_summary` | `text_default` | Standard node body field. |
| `number_integer` | `integer` | Core | `number` | `number_integer` | Whole numbers. |
| `number_decimal` | `decimal` | Core | `number` | `number_decimal` | Precision and scale configured in field storage settings. |
| `number_float` | `float` | Core | `number` | `number_unformatted` | Floating point numbers. |
| `list_boolean` | `boolean` | Core `options` | `boolean_checkbox` | `boolean` | On/Off flag. |
| `list_text` | `list_string` | Core `options` | `options_select` | `list_default` | Allowed key/value pairs defined in storage schema. |
| `image` | `image` | Core `image` | `image_image` | `image` | References `file` entity + metadata (alt, title, width, height). |
| `file` | `file` | Core `file` | `file_generic` | `file_default` | References `file` entity + description and display boolean. |
| `taxonomy_term_reference` | `entity_reference` | Core | `entity_reference_autocomplete`| `entity_reference_label` | Target type configured as `taxonomy_term`. |
| `entityreference` | `entity_reference` | Core | `entity_reference_autocomplete`| `entity_reference_label` | Contrib in D7; core in D10/D11 (`target_type: node`, etc.). |
| `link_field` | `link` | Core `link` | `link_default` | `link` | Contrib in D7; core in D10/D11. Properties: `uri`, `title`, `options`. |
| `email` | `email` | Core | `email_default` | `email_mailto` | Contrib in D7; core in D10/D11. Validated email strings. |
| `telephone` | `telephone` | Core `telephone` | `telephone_default` | `telephone_link` | Contrib in D7; core in D10/D11. |
| `date` / `datestamp` | `datetime` or `timestamp` | Core `datetime` | `datetime_default` | `datetime_default` | D7 dates stored as ISO or timestamps map to `datetime` storage type. |

---

## 2. Migration API Process Pipeline Recipes

### A. Entity Reference with `migration_lookup`

Preserves relationships when target entity IDs have changed during migration.

```yaml
destination:
  plugin: 'entity:node'
process:
  # Map taxonomy term reference
  field_tags:
    plugin: migration_lookup
    migration: d7_taxonomy_term
    source: field_tags_tid
    no_stub: true

  # Map node author UID
  uid:
    plugin: migration_lookup
    migration: d7_user
    source: node_uid
    default_value: 1
```

### B. Image Field with Sub-Process

Handles multi-property image fields (target file ID, alt text, title text).

```yaml
process:
  field_header_image:
    plugin: sub_process
    source: field_image
    process:
      target_id:
        plugin: migration_lookup
        migration: d7_file
        source: fid
      alt: alt
      title: title
      width: width
      height: height
```

### C. Formatted Text & Text Format Mapping

Translates legacy D7 filter formats (`filtered_html`, `full_html`) into modern D10/D11 formats (`basic_html`, `full_html`).

```yaml
process:
  'body/value': 'body/0/value'
  'body/summary': 'body/0/summary'
  'body/format':
    plugin: static_map
    source: 'body/0/format'
    map:
      'filtered_html': 'basic_html'
      'full_html': 'full_html'
      'plain_text': 'plain_text'
    default_value: 'basic_html'
```

### D. Link Field URI Normalization

Drupal 10/11 requires URIs to have an explicit scheme (e.g. `internal:/path` or `https://`).

```yaml
process:
  'field_link/title': 'field_link/0/title'
  'field_link/uri':
    plugin: callback
    callable: '\Drupal\custom_migrate\Utility\MigrateHelper::normalizeUri'
    source: 'field_link/0/url'
```

---

## 3. Storage Schema Definitions (`config/sync/`)

Every migrated field requires two CMI configuration entities:

### 1. Storage Configuration (`field.storage.<entity_type>.<field_name>.yml`)
Defines database column storage shared across bundles.

```yaml
langcode: en
status: true
dependencies:
  module:
    - node
id: node.field_external_reference
field_name: field_external_reference
entity_type: node
type: string
settings:
  max_length: 255
  case_sensitive: false
  is_ascii: false
module: core
locked: false
cardinality: 1
translatable: true
indexes: {}
persist_with_no_fields: false
custom_storage: false
```

### 2. Bundle Field Configuration (`field.field.<entity_type>.<bundle>.<field_name>.yml`)
Attaches the field storage to a specific bundle with label, description, and validation.

```yaml
langcode: en
status: true
dependencies:
  config:
    - field.storage.node.field_external_reference
    - node.type.article
id: node.article.field_external_reference
field_name: field_external_reference
entity_type: node
bundle: article
label: 'External Reference ID'
description: 'Identifier linking this article to upstream system'
required: false
translatable: true
default_value: {}
default_value_callback: ''
settings: {}
field_type: string
```
