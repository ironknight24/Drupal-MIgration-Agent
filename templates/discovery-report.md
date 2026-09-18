---
report_id: "DISCOVERY-{{ DATE }}"
category: "discovery"
agent: "discovery"
created_at: "{{ TIMESTAMP }}"
source_path: "{{ SOURCE_PATH }}"
target_path: "{{ TARGET_PATH }}"
status: "completed"
evidence_summary:
  observed_facts: 0
  inferences: 0
  proposals: 0
  assumptions: 0
  verified_results: 0
---

# Drupal Project Discovery & Baseline Audit Report

## 1. Executive Summary
- **Source Drupal Version**: {{ D7_VERSION }}
- **Source PHP Version Compatibility**: {{ PHP_VERSION }}
- **Target Drupal Version**: {{ D10_VERSION }}
- **Total Custom Modules**: {{ CUSTOM_MODULES_COUNT }}
- **Total Discovered Custom PHP Files**: {{ PHP_FILES_COUNT }}
- **Total Discovered Custom Classes**: {{ CLASSES_COUNT }}
- **Total Discovered .inc Files**: {{ INC_FILES_COUNT }}
- **Total Discovered Custom Entity Types**: {{ CUSTOM_ENTITIES_COUNT }}
- **Total Discovered Fields & Instances**: {{ FIELDS_COUNT }}
- **Total Discovered Revision Tables**: {{ REVISION_TABLES_COUNT }}
- **Total Discovered Multilingual/Translation Artifacts**: {{ TRANSLATIONS_COUNT }}
- **Total Contributed Modules**: {{ CONTRIB_MODULES_COUNT }}
- **Total Custom Themes**: {{ CUSTOM_THEMES_COUNT }}
- **Total Custom Database Tables**: {{ CUSTOM_TABLES_COUNT }}

---

## 2. Environment & Architecture Overview
- **Core Status**: [OBSERVED FACT]
- **File System Layout**: [OBSERVED FACT]
- **Composer / Dependency Management**: [OBSERVED FACT]

---

## 3. Custom Modules & Source File Inventory

| Module Name | Path | Discovered Source Files (.module, .inc, .install, .php) | Lines of Code | Hooks Implemented | Custom Schema | Status |
|---|---|---|---|---|---|---|
| `example_module` | `modules/custom/example` | `example.module`, `lib/ExampleProcessor.php`, `includes/admin.inc` | 420 | `hook_menu`, `hook_form_alter` | Yes | `not_started` |

---

## 4. Custom PHP Classes & Source Files Inventory

| Module | Source File Path | Class / Interface / Trait Name | Constructor Type (`__construct` / `ClassName` / `none`) | Constructor Dependencies & Globals | Autoloading Mechanism (`files[]`, `include`, `custom`) | Architectural Classification | Target D10 Class / Service |
|---|---|---|---|---|---|---|---|
| `example_module` | `lib/ExampleProcessor.php` | `ExampleProcessor` | `ExampleProcessor($db)` | `$db`, `global $user` | `files[] = lib/ExampleProcessor.php` | `SERVICE_BUSINESS_LOGIC` | `src/Service/ExampleProcessor.php` |
| `example_module` | `src/ExampleHelper.php` | `ExampleHelper` | `none` | None | `spl_autoload_register` | `UTILITY_HELPER` | `src/Utility/ExampleHelper.php` |

---

## 5. Legacy .inc File & Inclusion Graph Inventory

| Module | Relative Path | Inclusion Mechanism (`include`, `module_load_include`, `hook_menu`) | Extracted Functions & Callables | Functional Classification | Drush Commands |
|---|---|---|---|---|---|
| `example_module` | `includes/admin.inc` | `module_load_include('inc', 'example_module', 'includes/admin')` | `example_admin_settings_form()`, `example_admin_validate()` | `FORM` | None |
| `example_module` | `includes/drush.inc` | `hook_drush_command()` | `drush_example_sync()` | `DRUSH_COMMAND` | `example-sync` |

---

## 6. Procedural Hook Implementations & Custom Hooks Inventory

| Module | Hook Name | Hook Type (9 Types) | Source File:Line | Signature / Arguments | Callers / Invocations (`module_invoke_all`) | Target D10 Architecture (23 Targets) | Target Artifacts |
|---|---|---|---|---|---|---|---|
| `example_module` | `example_module_menu` | `CORE_HOOK` | `example_module.module:12` | `()` | Core Menu Router | `ROUTE`, `CONTROLLER`, `FORM_CLASS` | `example_module.routing.yml`, `src/Controller/ExampleController.php` |
| `example_module` | `example_module_form_alter` | `ALTER_HOOK` | `example_module.module:48` | `(&$form, &$form_state, $form_id)` | `drupal_alter('form', ...)` | `SERVICE` | `src/Service/ExampleFormAlterService.php` |
| `example_module` | `example_module_custom_event` | `CUSTOM_HOOK` | `includes/events.inc:15` | `($data, $account)` | `module_invoke_all('example_module_custom_event', ...)` | `EVENT_SUBSCRIBER` | `src/Event/CustomEvent.php`, `src/EventSubscriber/CustomSubscriber.php` |

---

## 7. hook_menu() Decomposition Inventory

| Module | Path | Page / Form Callback | Access Callback / Arguments | Title | Menu Type (`MENU_NORMAL_ITEM`, `MENU_LOCAL_TASK`, etc.) | D10 Route Name | D10 Target Class / YAML |
|---|---|---|---|---|---|---|---|
| `example_module` | `admin/config/example` | `drupal_get_form('example_admin_form')` | `user_access('administer example')` | Example Settings | `MENU_NORMAL_ITEM` | `example_module.admin_settings` | `src/Form/ExampleAdminForm.php`, `.links.menu.yml` |
| `example_module` | `example/%/view` | `example_view_page` | `example_access_callback` | View Record | `MENU_CALLBACK` | `example_module.record_view` | `src/Controller/ExampleController.php`, `src/Access/RecordAccessCheck.php` |

---

## 8. Configuration, State & Persistent Variables Inventory

| Module | Config / Variable Key | Taxonomy Type (20 Types) | Source File:Line | Default Value & Type | Lifecycle (`CREATE->READ->MODIFY->DELETE`) | Security Sensitivity | Target D10 Architecture | Migration Strategy | Status |
|---|---|---|---|---|---|---|---|---|---|
| `example_module` | `example_api_key` | `D7_ENVIRONMENT_VALUE` | `includes/admin.inc:24` | `""` (string) | `ADMIN_FORM -> RUNTIME_READ` | `SECRET_CREDENTIAL` | `SETTINGS_API` | `SETTINGS_MIGRATION` | `MIGRATED` |
| `example_module` | `example_last_sync` | `D7_PERSISTENT_STATE` | `example.module:110` | `0` (int) | `CRON_WRITE -> RUNTIME_READ` | `INTERNAL` | `STATE_API` | `STATE_MIGRATION` | `MIGRATED` |
| `example_module` | `example_settings` | `D7_ADMIN_SETTING` | `includes/admin.inc:45` | `{"timeout": 30}` (array) | `INSTALL -> ADMIN_FORM -> READ` | `PUBLIC` | `CONFIG_OBJECT` | `DIRECT_CONFIG_MIGRATION` | `MIGRATED` |

---

## 9. Custom Entities, Bundles, Fields, Revisions & Translations Inventory (Step 16)

| Module | Entity Type | Bundle | Field Name | Artifact Type | Field Type | Cardinality | Translatable | Revisionable | References / Target | Target Architecture (26 Types) | Migration Strategy (16 Strategies) | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `example_module` | `custom_record` | `custom_record` | N/A | `CUSTOM_ENTITY` | N/A | 1 | Yes | Yes | N/A | `CONTENT_ENTITY` | `ENTITY_TYPE_REBUILD` | `MIGRATED` |
| `example_module` | `custom_record` | `custom_record` | `field_reference_target` | `FIELD_INSTANCE` | `entityreference` | -1 | No | Yes | `node:article` | `ENTITY_REFERENCE` | `FIELD_REBUILD` | `MIGRATED` |

---

## 10. Forms, Form Alters & AJAX Inventory (Step 17)

| Module | Form ID | Builder / Callback | Item Type (8 Types) | Invocation | Validation & Submit | AJAX Commands | Rebuild & Multistep | Target Architecture (19 Types) | Migration Strategy (15 Strategies) | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `example_module` | `example_filter_form` | `example_filter_form` | `FORM_DEFINITION` | `drupal_get_form` | V: `_validate`, S: `_submit` | `ReplaceCommand` | Rebuild on filter change | `FORM_BASE` | `FORMBASE_REWRITE` | `MIGRATED` |
| `example_module` | `user_profile_form` | `example_form_user_profile_form_alter` | `FORM_ALTER` | `hook_form_FORM_ID_alter` | Custom validation attached | N/A | No rebuild | `FORM_ALTER` | `DIRECT_MODERNIZATION` | `MIGRATED` |

---

## 11. Frontend Assets, JavaScript Behaviors, CSS & Libraries Inventory (Step 18)

| Module | Asset Path | Asset Type (10 Types) | Library / Behavior Name | Selectors & Events | `once()` Pattern | `drupalSettings` Consumed | Target Architecture (21 Types) | Migration Strategy (17 Strategies) | Status |
|---|---|---|---|---|---|---|---|---|---|
| `example_module` | `js/example-widget.js` | `JAVASCRIPT` | `exampleModuleBehavior` | `.example-widget` (click) | `ONCE_JS` | `exampleModule.apiEndpoint` | `JS_ONCE_BEHAVIOR` | `ONCE_API_REWRITE` | `MIGRATED` |
| `example_module` | `css/example-style.css` | `STYLESHEET` | `example_module/widget_assets` | `.example-widget` | N/A | N/A | `CSS_LIBRARY` | `CSS_LIBRARY_REWRITE` | `MIGRATED` |

---

## 12. Views, Displays, Custom Handlers & Plugins Inventory (Step 19)

| Module | View ID | Display ID & Type | Base Table / Entity | Custom Handlers / Plugins | Contextual Filters & Sorts | Exposed Form & AJAX | Access & Caching | Target Architecture (30 Types) | Migration Strategy (21 Strategies) | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `example_module` | `example_content_listing` | `page_1` (Page) | `node` | Default handlers | Args: `uid`, Sort: `created DESC` | Exposed type filter, AJAX pager | Perm: `access content`, Tag cache | `VIEW_DISPLAY_PAGE` | `VIEW_CONFIG_REBUILD` | `MIGRATED` |
| `example_module` | `example_custom_report` | `block_1` (Block) | `custom_record` | `@ViewsField` (`custom_calc`) | Args: none, Sort: `id ASC` | None, No AJAX | Custom `@ViewsAccess`, Context cache | `VIEW_DISPLAY_BLOCK` | `HANDLER_PLUGIN_REWRITE` | `MIGRATED` |

---

## 13. Themes, Templates, Preprocess, Theme Hooks & Settings Inventory (Step 20)

| Theme / Module | Source Path | Artifact Type (11 Types) | Theme Hook / Template | Base Theme / Regions | Preprocess / Suggestion Logic | Consumed Variables / Render Arrays | Target Architecture (30 Types) | Migration Strategy (22 Strategies) | Status |
|---|---|---|---|---|---|---|---|---|---|
| `example_theme` | `templates/node--article.tpl.php` | `PHPTEMPLATE_FILE` | `node` | Regions: `content`, `sidebar_first` | `example_theme_preprocess_node` | `$title`, `$content`, `$submitted` | `TWIG_TEMPLATE` | `DIRECT_TWIG_MIGRATION` | `MIGRATED` |
| `example_theme` | `template.php` | `PREPROCESS_HOOK` | `page` | Base: `claro` | Adds `$custom_header_banner` | Render array `$page['header']` | `PREPROCESS_HOOK` | `PREPROCESS_REFACTOR` | `MIGRATED` |
| `example_theme` | `theme-settings.php` | `THEME_SETTINGS` | N/A | None | Settings form alters | `theme_get_setting('banner_color')` | `THEME_CONFIGURATION` | `THEME_SETTINGS_TO_CONFIG` | `MIGRATED` |

---

## 14. Contributed Modules Inventory

| Contrib Module | D7 Version | Core in D10? | D10 Available? | Community Replacement | Action Plan |
|---|---|---|---|---|---|
| `views` | 7.x-3.24 | Yes | Core | `drupal/core` | Core migration |
| `ctools` | 7.x-1.15 | Partial | Yes (4.x) | `drupal/ctools` | Composer require |

---

## 15. Custom Themes Summary

| Theme Name | Path | Base Theme | Template Files (.tpl.php) | Preprocess Functions | Theme Functions | Theme Settings |
|---|---|---|---|---|---|---|
| `example_theme` | `themes/custom/example` | None | 14 | 6 | 2 | Yes |

---

## 16. Custom Database Tables & Data-Model Inventory

| Module | Table Name | Schema Location (`hook_schema`) | Primary Key & Indexes | Entity References (`uid`, `nid`, etc.) | Data Semantics (17 Categories) | Serialization (`PHP_SERIALIZE`, `JSON`, etc.) | CRUD Callers (Create/Read/Update/Delete) | Target Architecture |
|---|---|---|---|---|---|---|---|---|
| `example_module` | `example_records` | `example.install:hook_schema` | PK: `record_id`, Idx: `uid` | `uid` (user) | `USER_DATA` | `PHP_SERIALIZE` | C: `example_save()`, R: `example_load()`, U: `example_update()`, D: `example_delete()` | `CONTENT_ENTITY` |

---

## 17. Entity & Data Architecture
- **Content Types**:
- **Taxonomy Vocabularies**:
- **Custom SQL Tables**:
- **User Roles & Permissions**:

---

## 18. Integrations, External Endpoints & Drush Commands
- **Webhooks & APIs**:
- **Authentication Protocols**:
- **Custom Drush Commands**:

---

## 19. Baseline Audit Findings & Risks
- **Risk Assessment**:
- **Recommended Sequence Overrides**:
