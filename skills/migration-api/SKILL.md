---
name: migration-api
description: Drupal Core Migration API Architect & ETL Pipeline Playbook. Configures source, process, and destination plugins, relational dependencies, entity/field/revision/translation pipelines, and data integrity verification.
version: 1.1.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Drupal Core Migration API Architect Skill

## Overview
This skill provides the architectural guidelines, plugin pipeline configurations, relational sequencing workflows, and zero-omission accounting for constructing robust, reproducible data migrations from Drupal 7 to modern Drupal 10 and Drupal 11 using the core Migration API (`migrate`, `migrate_drupal`, `migrate_plus`).

---

## Technical References
- [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)

---

## Relational Pipeline Sequencing

To avoid foreign key constraint violations, circular dependencies, and orphaned references, migrations must execute in strict dependency order:

```text
1. Languages & Multilingual Config (d7_language)
   ↓
2. User Roles & Permissions (d7_user_role)
   ↓
3. User Accounts (d7_user)
   ↓
4. Taxonomy Vocabularies (d7_taxonomy_vocabulary)
   ↓
5. Taxonomy Terms (d7_taxonomy_term)
   ↓
6. Managed Files & Media (d7_file)
   ↓
7. Custom Config Entities & Lookup Tables
   ↓
8. Custom Content Entities (Base & Fieldable)
   ↓
9. Nodes & Content Types (d7_node)
   ↓
10. Entity Revisions & Historical Moderation (d7_node_revision, custom revisions)
   ↓
11. Entity Translations & Multilingual Fields (d7_entity_translation, content_translation)
   ↓
12. Entity References, Comments & Menu Links (d7_menu_links, d7_comment)
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

For custom entities, extend `Drupal\migrate\Plugin\migrate\source\SqlBase`:
- Define `query()` selecting base, data, revision, and field tables.
- Define `fields()` declaring all source schema columns and computed properties.
- Define `getIds()` declaring the unique source identifier schema.

### 2. Process Plugin Pipeline
Transforms incoming source fields into target entity properties using chainable plugins:
- `migration_lookup`: Looks up destination IDs based on prior migration runs (essential for `entity_reference`).
- `sub_process`: Iterates over complex multi-property fields (e.g. image, link, paragraph items).
- `static_map`: Translates discrete status values, formats, or vocabularies.
- `default_value`: Sets defaults when source fields are NULL.
- `callback`: Invokes safe helper functions for data normalization.
- `d7_field_formatter`: Normalizes legacy field deltas and language keys.

### 3. Destination Plugin Definition
Persists mapped data into Drupal 10/11 entities:

```yaml
destination:
  plugin: 'entity:node'
  default_bundle: article
  translations: true # For translation migrations
```

---
## Custom Database & Data-Model Migration Strategies (Step 13)

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

## Step 16 Entity & Field Target Architecture Taxonomy

Every discovered D7 entity, field, revision, translation, or reference artifact must map to one or more of the 26 target architecture classifications:

| Target Architecture | Description | Implementation Artifact |
| :--- | :--- | :--- |
| `CONTENT_ENTITY` | Full fieldable/revisionable/translatable content entity | `src/Entity/<CustomEntity>.php` (`@ContentEntityType`) |
| `CONFIG_ENTITY` | Schema-backed exportable configuration entity | `src/Entity/<CustomConfig>.php` (`@ConfigEntityType`) |
| `ENTITY_TYPE` | Entity type declaration and interface | `src/Entity/<CustomEntity>Interface.php` |
| `BUNDLE` | Entity sub-type or bundle plugin definition | CMI YAML or Bundle Plugin class |
| `ENTITY_STORAGE` | Custom entity storage handler | `src/Storage/<CustomEntity>Storage.php` |
| `ENTITY_ACCESS_HANDLER` | Entity access control handler | `src/Access/<CustomEntity>AccessControlHandler.php` |
| `ENTITY_QUERY` | Modernized EntityQuery usage | `\Drupal::entityTypeManager()->getStorage()->getQuery()` |
| `FIELD_STORAGE` | Field storage configuration | `config/sync/field.storage.<entity>.<field>.yml` |
| `FIELD_CONFIG` | Bundle-specific field instance config | `config/sync/field.field.<entity>.<bundle>.<field>.yml` |
| `FIELD_TYPE` | Custom FieldType plugin | `src/Plugin/Field/FieldType/<FieldType>.php` (`@FieldType`) |
| `FIELD_WIDGET` | Custom FieldWidget plugin | `src/Plugin/Field/FieldWidget/<Widget>.php` (`@FieldWidget`) |
| `FIELD_FORMATTER` | Custom FieldFormatter plugin | `src/Plugin/Field/FieldFormatter/<Formatter>.php` (`@FieldFormatter`) |
| `ENTITY_REFERENCE` | Typed entity reference field/target | `core.base_field_override` or `field.storage` (`entity_reference`) |
| `REVISIONABLE_ENTITY` | Entity supporting revision history | Implements `RevisionableInterface` with `revision_table` |
| `TRANSLATABLE_ENTITY` | Entity supporting Content Translation | Implements `TranslatableInterface` with `data_table` |
| `TRANSLATION_HANDLER` | Content translation UI handler | `Drupal\content_translation\ContentTranslationHandler` |
| `PLUGIN` | Re-engineered as a typed Drupal Plugin | `src/Plugin/<PluginType>/<Class>.php` |
| `SERVICE` | Re-engineered as an injected Symfony service | `src/Service/<Service>.php` |
| `REPOSITORY` | Custom relational data access repository | `src/Repository/<Repository>.php` |
| `CUSTOM_STORAGE` | Custom backend storage engine | `src/Storage/CustomStorageHandler.php` |
| `CONFIGURATION` | Static settings in CMI YAML | `config/sync/<module>.settings.yml` |
| `STATE` | Ephemeral runtime key/value state | `\Drupal::state()` |
| `EXTERNAL_SYSTEM` | Offloaded to external 3rd-party API/system | Client service / webhook |
| `OBSOLETE` | Documented legacy dead code/field/entity | Deprecated and excluded |
| `HUMAN_DECISION_REQUIRED` | Ambiguous semantic or structural pattern | Architectural decision record required |
| `UNVERIFIED` | Runtime inspection required | Staging validation gate required |

---

## Step 16 Standardized Entity & Field Migration Strategies

Apply one of the 16 explicit strategies to every discovered entity and field item:

1. **`DIRECT_ENTITY_MIGRATION`**: Direct migration into a corresponding D10 entity type using a dedicated Migrate source and destination plugin.
2. **`TRANSFORMED_ENTITY_MIGRATION`**: Source rows undergo schema normalization, bundle merging/splitting, or complex field restructuring during migration.
3. **`ENTITY_TYPE_REBUILD`**: Architectural re-engineering of legacy procedural entity definitions into OOP `@ContentEntityType` or `@ConfigEntityType`.
4. **`BUNDLE_REBUILD`**: Re-engineering legacy node types or custom bundles into D10 CMI bundle definitions or bundle plugins.
5. **`FIELD_REBUILD`**: Re-engineering legacy D7 field definitions into D10 `field.storage.*` and `field.field.*` CMI configurations or base fields.
6. **`FIELD_TRANSFORMATION`**: Modernizing legacy field types into modern equivalents (e.g., `text_with_summary` → `text_with_summary`, custom field → typed data plugin).
7. **`REFERENCE_REMAP`**: Remapping legacy entity/node/user/term references via `migration_lookup` process plugins to new D10 entity IDs.
8. **`REVISION_MIGRATION`**: Dedicated secondary migration pipeline transferring complete revision history, log messages, and timestamps.
9. **`TRANSLATION_MIGRATION`**: Dedicated multilingual migration pipeline migrating field translations into D10 entity translation records.
10. **`CONFIG_ENTITY_MIGRATION`**: Migrating D7 exported arrays or database records into modern D10 Config Entities.
11. **`CUSTOM_STORAGE_MIGRATION`**: Migrating data stored in custom storage engines or external backends.
12. **`CONTENT_MIGRATION`**: Migrating raw table records into standard Drupal content entities.
13. **`REPLACED`**: Legacy custom entity/field functionality replaced by modern Core (Media, Workflows, Layout Builder) or standard Contrib.
14. **`OBSOLETE`**: Documented legacy dead entities, orphan field tables, or deprecated structures excluded with reasons.
15. **`HUMAN_DECISION_REQUIRED`**: Unresolved entity architecture, data integrity ambiguity, or manual mapping sign-off needed.
16. **`UNVERIFIED`**: Dynamic or unverified entity/field structures requiring runtime verification.


---

## Revision & Multilingual Migration Guidelines

### Revision Migration Pipeline
- When entities have active revision tables (`{node_revision}`, `{custom_entity_revision}`):
  - Configure two migration definitions:
    1. Base entity migration (`d7_custom_entity`) creating the initial entities.
    2. Revision migration (`d7_custom_entity_revision`) mapped to destination `plugin: 'entity_revision:<entity_type>'`.
  - Process plugins must map `vid` (revision ID), `revision_timestamp`, `revision_uid`, and `revision_log`.

### Multilingual & Translation Pipeline
- Map legacy `LANGUAGE_NONE` (`und`) to target default language (`en`, site default, or `und`/`zxx` for language-neutral items).
- For sites using Entity Translation / Content Translation:
  - Base migration imports the default translation.
  - Secondary translation migration (`d7_custom_entity_translation`) uses `destination: plugin: 'entity:<entity_type>', translations: true`.
  - Map `langcode` property in source and destination to associate translations with existing entity IDs (`migration_lookup`).

---

## Form & AJAX Target Architecture Taxonomy & Migration Strategies

### 19 Form & AJAX Target Architecture Classifications
1. **`FORM_BASE`**: Standard interactive form extending `FormBase` (`src/Form/`).
2. **`CONFIG_FORM_BASE`**: Administrative configuration form extending `ConfigFormBase` with CMI integration.
3. **`CONFIRM_FORM_BASE`**: Interactive confirmation dialog form extending `ConfirmFormBase`.
4. **`ENTITY_FORM`**: Generic entity CRUD form handler.
5. **`CONTENT_ENTITY_FORM`**: Fieldable content entity form extending `ContentEntityForm`.
6. **`CONFIG_ENTITY_FORM`**: Configuration entity form extending `ConfigEntityForm`.
7. **`PLUGIN_FORM`**: Reusable plugin configuration sub-form implementing `PluginFormInterface`.
8. **`ROUTED_FORM`**: Standalone form rendered directly via route entry in `<module>.routing.yml`.
9. **`AJAX_FORM`**: Interactive form with asynchronous element rebuilds or sub-element updates.
10. **`AJAX_CALLBACK`**: Controller or Form class method returning an `AjaxResponse`.
11. **`AJAX_COMMAND`**: OOP command implementing `CommandInterface` (`ReplaceCommand`, `HtmlCommand`, etc.).
12. **`FORM_ALTER`**: Form alteration implementation via `hook_form_alter()` or EventSubscriber.
13. **`FORM_VALIDATOR`**: Dedicated form or element validation handler / Constraint Validator.
14. **`FORM_SUBMIT_HANDLER`**: Dedicated form submit callback or injected service handler.
15. **`SERVICE_BACKED_FORM`**: Form class delegating complex processing to injected services.
16. **`MULTISTEP_FORM`**: Multi-page or step-based wizard form utilizing `FormStateInterface` storage.
17. **`FILE_UPLOAD_FORM`**: Form handling managed file uploads with `#type => managed_file`.
18. **`OBSOLETE`**: Deprecated or superseded legacy form structures.
19. **`HUMAN_DECISION_REQUIRED` / `UNVERIFIED`**: Unresolved dynamic form constructions or unverified callbacks.

### 15 Form & AJAX Migration Strategies
1. **`DIRECT_MODERNIZATION`**: Direct 1:1 conversion of standard Form API array to modern `FormBase` methods.
2. **`FORM_API_REWRITE`**: Complete restructuring of legacy element tree into modern render array and typed data elements.
3. **`FORMBASE_REWRITE`**: Re-engineering procedural form builders into OOP `FormBase` classes.
4. **`CONFIG_FORM_REWRITE`**: Re-engineering `system_settings_form()` into `ConfigFormBase` with CMI schema.
5. **`ENTITY_FORM_REWRITE`**: Re-engineering procedural entity edit forms into `ContentEntityForm` handlers.
6. **`AJAX_REWRITE`**: Converting procedural `ajax_render()` and `#ajax` callbacks to `AjaxResponse` with `CommandInterface` objects.
7. **`CONTROLLER_PLUS_FORM`**: Decoupling complex page callback forms into dedicated Controller + Form combinations.
8. **`SERVICE_BACKED_REWRITE`**: Extracting procedural business logic from submit/validate callbacks into injectable services.
9. **`MULTISTEP_REWRITE`**: Converting `$form_state['storage']` wizards into modern `FormStateInterface` step managers.
10. **`CALLBACK_REFACTOR`**: Modernizing custom validation/element callbacks into class methods or plugins.
11. **`REPLACED`**: Legacy custom form replaced by modern Core (Views exposed forms, Media, Workflows) or Contrib.
12. **`OBSOLETE`**: Obsolete administrative or dead forms excluded with documented justification.
13. **`EXCLUDED_WITH_REASON`**: Deliberately excluded forms with explicit rationale.
14. **`HUMAN_DECISION_REQUIRED`**: Dynamic form IDs or ambiguous security flows requiring human review.
15. **`UNVERIFIED`**: Dynamic or unverified form structures requiring runtime validation.

### 21 Frontend Target Architecture Classifications
1. **`DRUPAL_LIBRARY`**: Standard asset package registered in `<module>.libraries.yml`.
2. **`JS_BEHAVIOR`**: Modular client-side script implementing `Drupal.behaviors.<name>`.
3. **`JS_ONCE_BEHAVIOR`**: JavaScript behavior utilizing `@drupal/once` for idempotent DOM attachment.
4. **`AJAX_FRONTEND_BEHAVIOR`**: Client-side script responding to asynchronous form/page updates.
5. **`DRUPAL_SETTINGS_CONSUMER`**: Client-side script consuming PHP runtime parameters via `drupalSettings`.
6. **`CSS_LIBRARY`**: SMACSS structured stylesheet asset registered under base/layout/component/state/theme.
7. **`INLINE_JS`**: Legacy inline `<script>` or `drupal_add_js(..., 'inline')` requiring refactoring.
8. **`INLINE_CSS`**: Legacy inline `<style>` or `drupal_add_css(..., 'inline')` requiring refactoring.
9. **`EXTERNAL_LIBRARY`**: Remote CDN stylesheet or script declared in `*.libraries.yml` with `type: external`.
10. **`THIRD_PARTY_LIBRARY`**: Vendor or third-party JavaScript/CSS plugin package.
11. **`THEME_LIBRARY`**: Presentation-only stylesheet or behavior owned by custom/contrib theme.
12. **`MODULE_LIBRARY`**: Functional module-level stylesheet or behavior package.
13. **`PREPROCESS_ATTACHMENT`**: Asset attached dynamically via `hook_preprocess_*()` or `hook_page_attachments()`.
14. **`RENDER_ARRAY_ATTACHMENT`**: Asset attached to element render arrays via `#attached['library']`.
15. **`AJAX_ATTACHMENT`**: Asset injected dynamically during AJAX response delivery.
16. **`CUSTOM_AJAX_COMMAND_CLIENT`**: Client-side prototype handler extending `Drupal.AjaxCommands`.
17. **`TEMPLATE_SCRIPT`**: Script directly embedded in legacy template or Twig template.
18. **`TEMPLATE_STYLE`**: Style directly embedded in legacy template or Twig template.
19. **`OBSOLETE`**: Deprecated frontend asset superseded by modern core features.
20. **`HUMAN_DECISION_REQUIRED`**: External library or dynamic script requiring architectural decision.
21. **`UNVERIFIED`**: Unresolved dynamic asset path or runtime-dependent frontend behavior.

### 17 Frontend Migration Strategies
1. **`LIBRARY_YML_REWRITE`**: Converting `.info` scripts/stylesheets and `drupal_add_*` to `<module>.libraries.yml`.
2. **`BEHAVIOR_REWRITE`**: Refactoring procedural JS / DOM ready into strict `Drupal.behaviors` syntax.
3. **`ONCE_API_REWRITE`**: Converting `jQuery.once()` to modern `@drupal/once` / `once()` iterating with `forEach()`.
4. **`DRUPAL_SETTINGS_REWRITE`**: Modernizing `Drupal.settings` to `#attached['drupalSettings']` and `drupalSettings` parameter.
5. **`AJAX_CLIENT_REWRITE`**: Modernizing custom AJAX event bindings and `Drupal.ajax` commands.
6. **`CSS_LIBRARY_REWRITE`**: Restructuring legacy CSS into modern SMACSS categories in `*.libraries.yml`.
7. **`INLINE_TO_LIBRARY`**: Extracting inline scripts/styles into dedicated library asset files.
8. **`INLINE_TO_BEHAVIOR`**: Converting inline PHP script blocks into parametrized `drupalSettings` behaviors.
9. **`PREPROCESS_ATTACHMENT_REWRITE`**: Modernizing `drupal_add_js/css` in preprocess to `hook_page_attachments()`.
10. **`THIRD_PARTY_LIBRARY_REPLACEMENT`**: Replacing legacy jQuery plugins with modern npm/Composer or native JS.
11. **`EXTERNAL_ASSET_REVIEW`**: Auditing external CDN scripts for security and declaring with `type: external`.
12. **`THEME_ASSET_HANDOFF`**: Transferring presentation-only stylesheets to Step 20 theme architecture.
13. **`OBSOLETE`**: Deprecating obsolete frontend assets (e.g. polyfills, deprecated jQuery UI).
14. **`REPLACED`**: Legacy custom widget replaced by Drupal 10/11 core UI components (e.g. core Dialog, Media).
15. **`EXCLUDED_WITH_REASON`**: Deliberately excluded frontend assets with documented justification.
16. **`HUMAN_DECISION_REQUIRED`**: Unresolved third-party plugin or licensing decision requiring human review.
17. **`UNVERIFIED`**: Dynamic frontend script or unverified selector requiring browser validation.

---

## Step 19 Views, Displays & Custom Plugins Target Architecture Taxonomy

Every discovered D7 View, display, custom handler, plugin, or query alteration must map to one or more of the 30 target architecture classifications:

| Target Architecture | Description | Implementation Artifact |
| :--- | :--- | :--- |
| `VIEW_CONFIG` | Full exported View entity configuration | `config/install/views.view.<view_id>.yml` |
| `VIEW_DISPLAY_PAGE` | Routed page display with path and menu configuration | `display: page_1` in View YAML |
| `VIEW_DISPLAY_BLOCK` | Block display embeddable in layouts and theme regions | `display: block_1` in View YAML |
| `VIEW_DISPLAY_FEED` | RSS/Atom feed syndication display | `display: feed_1` in View YAML |
| `VIEW_DISPLAY_REST` | JSON/HAL/XML REST export display | `display: rest_export_1` in View YAML |
| `VIEW_DISPLAY_EXPORT` | CSV/Data export display via serializer | `display: data_export_1` in View YAML |
| `VIEW_DISPLAY_ATTACHMENT` | Secondary display attached before/after primary display | `display: attachment_1` in View YAML |
| `VIEW_DISPLAY_EMBED` | Programmatically embeddable display | `display: embed_1` in View YAML |
| `VIEW_FIELD_PLUGIN` | Custom field handler plugin | `src/Plugin/views/field/<Field>.php` (`@ViewsField`) |
| `VIEW_FILTER_PLUGIN` | Custom filter handler plugin | `src/Plugin/views/filter/<Filter>.php` (`@ViewsFilter`) |
| `VIEW_CONTEXTUAL_FILTER_PLUGIN` | Custom contextual filter / argument handler plugin | `src/Plugin/views/argument/<Argument>.php` (`@ViewsArgument`) |
| `VIEW_SORT_PLUGIN` | Custom sort handler plugin | `src/Plugin/views/sort/<Sort>.php` (`@ViewsSort`) |
| `VIEW_RELATIONSHIP_PLUGIN` | Custom table join/relationship handler plugin | `src/Plugin/views/relationship/<Rel>.php` (`@ViewsRelationship`) |
| `VIEW_AREA_PLUGIN` | Custom header, footer, or empty-text area handler | `src/Plugin/views/area/<Area>.php` (`@ViewsArea`) |
| `VIEW_PAGER_PLUGIN` | Custom pagination plugin | `src/Plugin/views/pager/<Pager>.php` (`@ViewsPager`) |
| `VIEW_ACCESS_PLUGIN` | Custom access control plugin | `src/Plugin/views/access/<Access>.php` (`@ViewsAccess`) |
| `VIEW_QUERY_PLUGIN` | Custom backend query plugin | `src/Plugin/views/query/<Query>.php` (`@ViewsQuery`) |
| `VIEW_STYLE_PLUGIN` | Custom format/style plugin | `src/Plugin/views/style/<Style>.php` (`@ViewsStyle`) |
| `VIEW_ROW_PLUGIN` | Custom row rendering plugin | `src/Plugin/views/row/<Row>.php` (`@ViewsRow`) |
| `VIEW_DISPLAY_PLUGIN` | Custom display plugin extending DisplayPluginBase | `src/Plugin/views/display/<Display>.php` (`@ViewsDisplay`) |
| `VIEW_CACHE_PLUGIN` | Custom cache management plugin | `src/Plugin/views/cache/<Cache>.php` (`@ViewsCache`) |
| `VIEW_EXPOSED_FORM_PLUGIN` | Custom exposed filter form plugin | `src/Plugin/views/exposed_form/<Form>.php` (`@ViewsExposedForm`) |
| `CUSTOM_VIEWS_PLUGIN` | Generic custom Views plugin class | `src/Plugin/views/<Type>/<Plugin>.php` |
| `VIEWS_DATA_DEFINITION` | Schema table integration metadata | `<module>.views.inc:hook_views_data()` |
| `VIEWS_QUERY_ALTER` | Procedural query alteration hook | `<module>.views_execution.inc:hook_views_query_alter()` |
| `VIEWS_RENDER_ALTER` | Pre/post render alteration hook | `<module>.module:hook_views_pre_render()` |
| `VIEWS_ACCESS_RULE` | Access check rule or permission configuration | `display_options: access: type: perm` |
| `OBSOLETE` | Deprecated Views handler/display excluded with reason | Deprecated legacy Views artifact |
| `HUMAN_DECISION_REQUIRED` | Complex SQL query or dynamic view needing architect review | Architectural decision record required |
| `UNVERIFIED` | Dynamic view dispatch requiring runtime validation | Runtime staging validation required |

---

## Step 19 Standardized Views & Custom Plugin Migration Strategies

Apply one of the 21 explicit strategies to every discovered Views item:

1. **`VIEW_CONFIG_REBUILD`**: Reconstructing D7 default Views or database export into modern `config/install/views.view.<view_id>.yml`.
2. **`VIEW_DISPLAY_REBUILD`**: Modernizing individual displays (paths, blocks, feeds, REST export) within the View configuration.
3. **`HANDLER_PLUGIN_REWRITE`**: Converting legacy procedural handlers (`views_handler_*`) to PSR-4 annotated plugin classes under `src/Plugin/views/`.
4. **`CUSTOM_PLUGIN_REWRITE`**: Modernizing custom Views plugins with constructor dependency injection (`ContainerFactoryPluginInterface`).
5. **`VIEWS_DATA_REWRITE`**: Re-engineering `hook_views_data()` and `hook_views_data_alter()` in `<module>.views.inc`.
6. **`QUERY_PLUGIN_REWRITE`**: Modernizing non-SQL or specialized query backend plugins.
7. **`QUERY_ALTER_REWRITE`**: Converting procedural SQL alterations to `hook_views_query_alter()` operating on modern `Sql` query objects.
8. **`FILTER_REWRITE`**: Modernizing complex filter logic, grouped filters, or custom operator handling.
9. **`CONTEXTUAL_FILTER_REWRITE`**: Modernizing argument validators, default value plugins, and contextual argument handling.
10. **`RELATIONSHIP_REWRITE`**: Re-engineering table joins and entity reference relationship chains.
11. **`ACCESS_REWRITE`**: Modernizing access control to modern permissions, roles, or custom `@ViewsAccess` plugins.
12. **`CACHE_METADATA_REWRITE`**: Converting legacy time-based caching to modern cache tags, cache contexts, and cache max-age.
13. **`EXPOSED_FORM_REWRITE`**: Modernizing exposed filter forms with Step 17 Form API integration.
14. **`AJAX_VIEW_REWRITE`**: Modernizing AJAX pagination and filtering with Step 18 client-side event coordination.
15. **`PROGRAMMATIC_VIEW_REWRITE`**: Modernizing procedural `views_get_view()` / `views_embed_view()` to modern `\Drupal\views\Views` API.
16. **`THEME_HANDOFF`**: Delegating view row templates (`views-view-*.html.twig`) to Step 20 theme architecture.
17. **`REPLACED`**: Legacy custom View or handler replaced by core Drupal 10/11 features (Media, Layout Builder, JSON:API).
18. **`OBSOLETE`**: Deprecated or dead Views excluded with documented technical rationale.
19. **`EXCLUDED_WITH_REASON`**: Deliberately excluded Views items with explicit architectural justification.
20. **`HUMAN_DECISION_REQUIRED`**: Dynamic View IDs, unresolvable query alterations, or complex security rules needing architect review.
21. **`UNVERIFIED`**: Dynamic View dispatches or runtime-dependent query alterations requiring runtime testing.

---

## 30 Theme & Presentation Target Architecture Classifications (Step 20)

Every discovered theme artifact is categorized into one of 30 standard target architectures:
1. **`THEME`**: Root modern theme package declaration.
2. **`BASE_THEME`**: Parent theme providing inherited templates, styling, and regions.
3. **`SUB_THEME`**: Child theme extending base theme with overrides.
4. **`THEME_INFO`**: Theme metadata declaration (`<theme>.info.yml`).
5. **`THEME_REGION`**: Layout region definition in `info.yml` and `page.html.twig`.
6. **`TWIG_TEMPLATE`**: Standard Twig presentation template (`templates/**/*.html.twig`).
7. **`TWIG_TEMPLATE_OVERRIDE`**: Twig template overriding core, module, or base theme template.
8. **`THEME_HOOK`**: Registered presentation theme hook definition.
9. **`CUSTOM_THEME_HOOK`**: Module- or theme-defined custom theme hook implementation.
10. **`PREPROCESS_HOOK`**: Preprocess function (`<theme>_preprocess_HOOK`) in `<theme>.theme`.
11. **`PROCESS_HOOK`**: Process function refactored to modern preprocess implementation.
12. **`THEME_SUGGESTION`**: Static template suggestion based on route, bundle, or view mode.
13. **`DYNAMIC_THEME_SUGGESTION`**: Runtime-calculated template suggestion requiring alter hooks.
14. **`THEME_FUNCTION_REPLACEMENT`**: Procedural `theme_*()` function converted to Twig or render element.
15. **`RENDER_ARRAY`**: Structured renderable array produced by theme functions or preprocess.
16. **`RENDER_ELEMENT`**: Plugin-based render element (`#type`).
17. **`THEME_SERVICE`**: Injected helper service supporting complex presentation calculations.
18. **`THEME_CONFIGURATION`**: CMI theme configuration (`config/install/<theme>.settings.yml`).
19. **`THEME_LIBRARY`**: Modular asset library in `<theme>.libraries.yml`.
20. **`TEMPLATE_VARIABLE_PROVIDER`**: Preprocess hook computing presentation variables.
21. **`ENTITY_TEMPLATE`**: Entity-specific presentation template (`node.html.twig`, `user.html.twig`).
22. **`FIELD_TEMPLATE`**: Field-level template (`field.html.twig`, `field--<field_name>.html.twig`).
23. **`VIEW_TEMPLATE`**: Views presentation template override (`views-view.html.twig`).
24. **`FORM_TEMPLATE`**: Form-level wrapper or element template.
25. **`BLOCK_TEMPLATE`**: Block wrapper template (`block.html.twig`).
26. **`MENU_TEMPLATE`**: Menu navigation template (`menu.html.twig`).
27. **`PAGE_TEMPLATE`**: Global page layout template (`page.html.twig`).
28. **`OBSOLETE`**: Deprecated theme artifact with no modern equivalent.
29. **`HUMAN_DECISION_REQUIRED`**: Ambiguous presentation logic or dynamic suggestions flagged for human review.
30. **`UNVERIFIED`**: Presentation behavior dependent on unavailable runtime state.

---

## 22 Standardized Theme Migration Strategies (Step 20)

1. **`DIRECT_TWIG_MIGRATION`**: Direct conversion of `.tpl.php` to `.html.twig` without logic refactoring.
2. **`TWIG_WITH_PREPROCESS`**: Twig conversion with extracted business/data logic moved to `.theme` preprocess functions.
3. **`THEME_FUNCTION_TO_TWIG`**: Procedural `theme_*()` converted to a standalone Twig template.
4. **`THEME_FUNCTION_TO_RENDER_ARRAY`**: Procedural `theme_*()` converted to structured render arrays.
5. **`THEME_FUNCTION_TO_SERVICE`**: Complex theme function extracted to an injectable service.
6. **`PREPROCESS_REFACTOR`**: Preprocess function modernized with typehinted `$variables` array access and bubbleable metadata.
7. **`PROCESS_TO_PREPROCESS`**: Legacy D7 process hook refactored into a modern preprocess hook.
8. **`TEMPLATE_SUGGESTION_REFACTOR`**: Modernized to `hook_theme_suggestions_HOOK_alter()`.
9. **`DYNAMIC_SUGGESTION_HUMAN_REVIEW`**: Non-deterministic runtime suggestions escalated for architecture review.
10. **`REGION_TO_THEME_REGION`**: D7 region definitions mapped to D10/D11 theme regions.
11. **`BASE_THEME_REFACTOR`**: Base theme declaration updated to Olivero, Claro, or custom starterkit.
12. **`SUB_THEME_MIGRATION`**: Sub-theme configuration and inheritance tree modernized.
13. **`THEME_SETTINGS_TO_CONFIG`**: Theme settings form converted to typed CMI configuration and schema.
14. **`LIBRARY_HANDOFF_TO_STEP18`**: Theme asset files packaged into `<theme>.libraries.yml` per Step 18 standards.
15. **`ENTITY_TEMPLATE_REFACTOR`**: Entity template modernized preserving Step 16 field structures.
16. **`FIELD_TEMPLATE_REFACTOR`**: Field template modernized with semantic attributes.
17. **`SECURITY_ESCAPING_REFACTOR`**: Unsafe print statements refactored to Twig auto-escaping and sanitized filters.
18. **`CACHE_METADATA_REFACTOR`**: Dynamic template logic annotated with cache tags, contexts, and max-age.
19. **`REPLACED`**: Legacy theme component replaced by modern Drupal core or contrib theme.
20. **`OBSOLETE`**: Deprecated theme helper, polyfill, or grid framework removed.
21. **`EXCLUDED_WITH_REASON`**: Explicitly excluded with documented rationale.
22. **`HUMAN_DECISION_REQUIRED`**: Complex template logic or custom design system refactor requiring human approval.

---

## 35 Dynamic, Runtime & Data-Driven Target Architecture Classifications (Step 21)

Every discovered dynamic dependency is categorized into one of 35 standard target architectures:
1. **`DYNAMIC_CALLABLE`**: General variable callback or variable function invocation.
2. **`DYNAMIC_FUNCTION`**: Variable procedural function call (`$func($arg)`).
3. **`DYNAMIC_METHOD`**: Dynamic method call on object or class (`$object->$method()`).
4. **`DYNAMIC_CLASS`**: Dynamic class resolution or variable instantiation (`new $class()`).
5. **`DYNAMIC_SERVICE`**: Dynamic service container identifier or variable service call.
6. **`DYNAMIC_PLUGIN`**: Dynamically determined plugin ID resolved via Plugin Manager.
7. **`DYNAMIC_HOOK`**: Dynamically constructed hook name invoked via `module_invoke()`.
8. **`DYNAMIC_EVENT`**: Runtime-constructed Symfony event name dispatched via EventDispatcher.
9. **`DYNAMIC_ENTITY`**: Dynamic entity type identifier resolved via `EntityTypeManager`.
10. **`DYNAMIC_BUNDLE`**: Runtime-determined bundle machine name.
11. **`DYNAMIC_FIELD`**: Runtime-determined field machine name or field property.
12. **`DYNAMIC_TEMPLATE`**: Dynamically resolved Twig template name or path.
13. **`DYNAMIC_THEME`**: Runtime-selected active theme or theme override.
14. **`DYNAMIC_VIEW`**: Runtime-selected View ID or embed call (`views_embed_view($dynamic_id)`).
15. **`DYNAMIC_FORM`**: Dynamically generated form ID or builder callback.
16. **`DYNAMIC_AJAX`**: Runtime-determined AJAX callback function or dynamic response command.
17. **`DYNAMIC_LIBRARY`**: Dynamically attached asset library name (`#attached['library']`).
18. **`DYNAMIC_FILE`**: Dynamically constructed file path for reading or writing.
19. **`DYNAMIC_INCLUDE`**: Dynamically constructed require/include path.
20. **`DYNAMIC_CONFIGURATION`**: Dynamically computed CMI configuration key or collection.
21. **`DYNAMIC_STATE`**: Dynamically constructed State API key.
22. **`DYNAMIC_VARIABLE`**: Legacy variable key computed dynamically at runtime.
23. **`DYNAMIC_DATABASE`**: Dynamically selected database target or connection key.
24. **`DYNAMIC_SQL`**: Dynamically assembled SQL string, table identifier, or query fragment.
25. **`SERIALIZED_DEPENDENCY`**: Serialized data structure containing embedded class or handler references.
26. **`JSON_DEPENDENCY`**: JSON payload containing embedded callbacks or configuration references.
27. **`ENVIRONMENT_DEPENDENCY`**: Logic branching on environment variables (`getenv()`) or server settings.
28. **`DATA_DRIVEN_DEPENDENCY`**: Logic determining code paths based on database rows or content values.
29. **`REFLECTION_DEPENDENCY`**: ReflectionClass/ReflectionMethod usage for dynamic introspection.
30. **`GENERATED_CODE`**: Dynamically evaluated or generated PHP code scripts.
31. **`EVAL_DEPENDENCY`**: `eval()` or `create_function()` dynamic code execution.
32. **`RUNTIME_PROBE`**: Explicit probe target requiring runtime CLI/environment verification.
33. **`OBSOLETE`**: Obsolete dynamic behavior removed during modernization.
34. **`HUMAN_DECISION_REQUIRED`**: Unresolvable dynamic pattern flagged for architect review.
35. **`UNVERIFIED`**: Dynamic dependency awaiting runtime staging verification.

---

## 19 Standardized Dynamic Migration Strategies (Step 21)

1. **`STATIC_RESOLUTION`**: Statically proven constant/literal value mapped directly to target artifact.
2. **`PARTIAL_STATIC_RESOLUTION`**: Statically bounded candidate set mapped with explicit conditional branching.
3. **`RUNTIME_DISCOVERY_REQUIRED`**: Dynamic dependency requiring controlled staging probe to discover values.
4. **`TEST_DRIVEN_RESOLUTION`**: Behavior verified and locked via automated PHPUnit / Kernel test suite.
5. **`DATA_FIXTURE_RESOLUTION`**: Resolution verified against representative legacy database fixtures.
6. **`CONFIGURATION_MAPPING`**: Dynamic keys mapped to structured CMI schema collections.
7. **`SERVICE_CONTAINER_MAPPING`**: Dynamic callables converted to tagged service collector pattern.
8. **`PLUGIN_MANAGER_MAPPING`**: Dynamic functions/classes converted to typed Drupal 10/11 Plugin Manager.
9. **`EVENT_DISPATCHER_MAPPING`**: Dynamic hooks converted to Symfony Event Dispatcher with custom Event objects.
10. **`ENTITY_API_MAPPING`**: Dynamic entity/field lookups modernized via `EntityTypeManagerInterface`.
11. **`TEMPLATE_MAPPING`**: Dynamic templates modernized to `hook_theme_suggestions_HOOK_alter()`.
12. **`VIEW_MAPPING`**: Dynamic Views converted to standard `\Drupal\views\Views` API calls with valid IDs.
13. **`FORM_MAPPING`**: Dynamic form IDs converted to parameterized `FormBase` classes.
14. **`FILE_DISCOVERY_MAPPING`**: Dynamic file includes replaced with PSR-4 autoloading or discovery services.
15. **`DATABASE_REFACTOR`**: Dynamic SQL queries refactored into parameterized Query Builders.
16. **`SERIALIZED_DATA_MIGRATION`**: Serialized payloads unpacked and migrated to typed schema fields.
17. **`HUMAN_DECISION_REQUIRED`**: Unconstrained dynamic behavior escalated for architect review.
18. **`UNVERIFIED`**: Dynamic dependency retained in unverified state pending runtime environment.
19. **`OBSOLETE`**: Deprecated dynamic behavior safely removed with documented rationale.

---

## Data Integrity Verification & Checksums

Before certifying a data migration pipeline as complete:
1. **Row Count & Semantic Cardinality Reconciliation**: Run comparison queries to verify that total source records match total destination records:
   $$\text{Source Row Count} = \text{Destination Row Count} + \text{Documented Excluded Count}$$
2. **Entity Reference Integrity**: Verify that no `migration_lookup` returned empty or stub IDs where valid parent records existed (`uid`, `nid`, `tid`, `fid`).
3. **Revision Count Integrity**: Compare source revision count against destination revision count for all revisionable entities.
4. **Translation Integrity**: Verify translation count matches across all supported language codes.
5. **Serialized Payload Verification**: Confirm serialized payloads are cleanly parsed and mapped without data truncation or corruption.
6. **Character Encoding Verification**: Confirm UTF-8 integrity; verify zero truncated multibyte strings.
7. **Rollback Verification**: Validate that migration configurations support clean rollback (`drush migrate:rollback <migration_id>`) without database corruption.
