---
report_id: "PLAN-{{ COMPONENT }}-{{ DATE }}"
component: "{{ COMPONENT }}"
category: "{{ CATEGORY }}" # custom_module | theme | data | config
agent: "{{ AGENT }}"
created_at: "{{ TIMESTAMP }}"
source_path: "{{ SOURCE_PATH }}"
target_path: "{{ TARGET_PATH }}"
status: "in_progress"
evidence_summary:
  observed_facts: 0
  inferences: 0
  proposals: 0
  assumptions: 0
  verified_results: 0
---

# Component Migration Plan: {{ COMPONENT }}

## 1. D7 Baseline Behavior & Source File Audit
- **Discovered Source Files**: [OBSERVED FACT] (`.module`, `.inc`, `.install`, `*.php`)
- **Discovered Custom Classes**: [OBSERVED FACT]
- **Constructors & Initializers**: [OBSERVED FACT]
- **Discovered Custom Database Tables & Schemas**: [OBSERVED FACT] (`hook_schema`, columns, primary keys, foreign keys)
- **Discovered Custom Entities & Bundles**: [OBSERVED FACT] (`hook_entity_info`, entity keys, revisions, translations)
- **Discovered Fields & Instances**: [OBSERVED FACT] (`hook_field_info`, `hook_field_instance_info`, widgets, formatters)
- **Hooks & Endpoints**: [OBSERVED FACT]
- **Business Logic Rules**: [OBSERVED FACT]
- **Autoloading / Include Tree**: [OBSERVED FACT]

---

## 2. Target Drupal 10 Architecture (D11-Ready)
- **Target Namespace**: `Drupal\{{ COMPONENT }}`
- **Custom Entity & Bundle Architecture**:
  - Content Entity: `Drupal\{{ COMPONENT }}\Entity\RecordEntity` (`@ContentEntityType`, implements `RecordEntityInterface`, `RevisionableInterface`, `TranslatableInterface`)
  - Config Entity: `Drupal\{{ COMPONENT }}\Entity\RecordType` (`@ConfigEntityType`)
  - Entity Access Handler: `Drupal\{{ COMPONENT }}\Access\RecordEntityAccessControlHandler`
  - Entity View Builder: `Drupal\{{ COMPONENT }}\Entity\RecordEntityViewBuilder`
  - Entity Storage Handler: `Drupal\{{ COMPONENT }}\Storage\RecordEntityStorage`
- **Services & Constructor Dependency Injection**:
  - `Drupal\{{ COMPONENT }}\Service\BusinessService` (injected with `Connection`, `EntityTypeManagerInterface`)
- **Database & Repository Architecture**:
  - Repository Service: `Drupal\{{ COMPONENT }}\Repository\RecordRepository` (injected with `Connection`)
- **Routing & Controllers**:
  - Route name: `{{ COMPONENT }}.main` -> `Drupal\{{ COMPONENT }}\Controller\MainController::index`
- **Plugins / Event Subscribers**:
- **Form Classes**: `Drupal\{{ COMPONENT }}\Form\SettingsForm` (`ConfigFormBase`), `Drupal\{{ COMPONENT }}\Form\RecordEntityForm`
- **Drush Commands**: `Drupal\{{ COMPONENT }}\Drush\Commands\{{ COMPONENT_CAMEL }}Commands`

---

## 3. File, Class, Hook, Database, Entity, Form & Configuration Accounting & D10 Architectural Mapping

| D7 Source File / Key / Schema / Entity / Form | Legacy Artifact / Hook / Table / Variable / Field / Form ID | Classification / Semantics | Target D10 Class / Storage Destination | Migration Strategy / Injected Services | Planned Outcome Status |
|---|---|---|---|---|---|
| `lib/ExampleProcessor.php` | `class ExampleProcessor` | `SERVICE_BUSINESS_LOGIC` | `src/Service/ExampleProcessor.php` | `@database`, `@config.factory` | `MIGRATED` |
| `{{ COMPONENT }}.module:L142` | `call_user_func($handler_func)` | `DYNAMIC_CALLABLE` | `src/Plugin/HandlerManager.php` | `PLUGIN_MANAGER_MAPPING` | `MIGRATED` |
| `{{ COMPONENT }}.module:hook_entity_info` | `entity: {{ COMPONENT }}_record` | `CONTENT_ENTITY` | `src/Entity/RecordEntity.php` | `ENTITY_TYPE_REBUILD` | `MIGRATED` |
| `{{ COMPONENT }}.install:hook_schema` | `table: {{ COMPONENT }}_record_revision` | `REVISIONABLE_ENTITY` | `src/Entity/RecordEntity.php` (`revision_table`) | `REVISION_MIGRATION` | `MIGRATED` |
| `{{ COMPONENT }}.module:hook_field_info` | `field: field_related_item` | `ENTITY_REFERENCE` | `core.base_field_override` / `field.storage` | `REFERENCE_REMAP` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `form: {{ COMPONENT }}_filter_form` | `FORM_BASE` | `src/Form/FilterForm.php` | `FORMBASE_REWRITE` (`@entity_type.manager`) | `MIGRATED` |
| `{{ COMPONENT }}.module` | `ajax: {{ COMPONENT }}_ajax_filter_callback` | `AJAX_CALLBACK` | `src/Form/FilterForm.php::ajaxFilterCallback` | `AJAX_REWRITE` (returns `AjaxResponse`) | `MIGRATED` |
| `templates/node--article.tpl.php` | `template: node--article` | `TWIG_TEMPLATE` | `templates/node/node--article.html.twig` | `DIRECT_TWIG_MIGRATION` | `MIGRATED` |
| `template.php:example_theme_preprocess_page` | `hook_preprocess_page` | `PREPROCESS_HOOK` | `{{ COMPONENT }}.theme:{{ COMPONENT }}_preprocess_page` | `PREPROCESS_REFACTOR` | `MIGRATED` |
| `template.php:example_theme_breadcrumb` | `theme_breadcrumb()` | `THEME_FUNCTION_REPLACEMENT` | `templates/navigation/breadcrumb.html.twig` | `THEME_FUNCTION_TO_TWIG` | `MIGRATED` |
| `theme-settings.php` | `theme settings form` | `THEME_CONFIGURATION` | `config/schema/{{ COMPONENT }}.schema.yml` | `THEME_SETTINGS_TO_CONFIG` | `MIGRATED` |
| `{{ COMPONENT }}.views_default.inc` | `view: {{ COMPONENT }}_content_listing` | `VIEW_DISPLAY_PAGE` | `config/install/views.view.{{ COMPONENT }}_content_listing.yml` | `VIEW_CONFIG_REBUILD` | `MIGRATED` |
| `includes/views/handlers/field.inc` | `class views_handler_field_custom_calc` | `VIEW_FIELD_PLUGIN` | `src/Plugin/views/field/CustomCalc.php` | `HANDLER_PLUGIN_REWRITE` (`@ViewsField`) | `MIGRATED` |
| `{{ COMPONENT }}.module:hook_views_query_alter` | `hook_views_query_alter` | `VIEWS_QUERY_ALTER` | `{{ COMPONENT }}.views_execution.inc:hook_views_query_alter` | `QUERY_ALTER_REWRITE` | `MIGRATED` |
| `js/widget.js` | `Drupal.behaviors.{{ COMPONENT }}Widget` | `JS_ONCE_BEHAVIOR` | `js/widget.js` (`{{ COMPONENT }}.libraries.yml`) | `ONCE_API_REWRITE` (`core/once`, `core/drupalSettings`) | `MIGRATED` |
| `css/widget.css` | `stylesheets[all][] = css/widget.css` | `CSS_LIBRARY` | `css/widget.css` (`{{ COMPONENT }}.libraries.yml`) | `CSS_LIBRARY_REWRITE` (SMACSS component) | `MIGRATED` |
| `{{ COMPONENT }}.install` | `table: {{ COMPONENT }}_records` | `USER_DATA` | `src/Entity/RecordEntity.php` | `ENTITY_MIGRATION` | `MIGRATED` |
| `includes/admin.inc:24` | `variable: {{ COMPONENT }}_endpoint` | `D7_ADMIN_SETTING` | `config/install/{{ COMPONENT }}.settings.yml` | `DIRECT_CONFIG_MIGRATION` (`@config.factory`) | `MIGRATED` |
| `{{ COMPONENT }}.module:110` | `variable: {{ COMPONENT }}_last_sync` | `D7_PERSISTENT_STATE` | `State API` (`{{ COMPONENT }}.last_sync`) | `STATE_MIGRATION` (`@state`) | `MIGRATED` |
| `includes/admin.inc:48` | `variable: {{ COMPONENT }}_api_key` | `D7_ENVIRONMENT_VALUE` | `settings.php` override / Key module | `SETTINGS_MIGRATION` (Rule 10: No Secrets in CMI) | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_menu()` | `CORE_HOOK` | `.routing.yml`, `src/Controller/`, `src/Form/`, `.links.menu.yml` | `DECOMPOSE_TO_ROUTES_AND_CONTROLLER` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_form_alter()` | `FORM_ALTER` | `src/Service/FormAlterService.php` | `@entity_type.manager` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_view()` | `CONTROLLER` | `src/Controller/ViewController.php` | `@current_user` | `MIGRATED` |
| `includes/admin.inc` | `{{ COMPONENT }}_admin_settings()` | `CONFIG_FORM_BASE` | `src/Form/SettingsForm.php` | `CONFIG_FORM_REWRITE` (`@config.factory`) | `MIGRATED` |
| `includes/helper.inc` | `{{ COMPONENT }}_calculate_tax()` | `SERVICE_BUSINESS_LOGIC` | `src/Service/CalculationService.php` | N/A | `MIGRATED` |
| `includes/drush.inc` | `drush_{{ COMPONENT }}_sync()` | `DRUSH_COMMAND` | `src/Drush/Commands/SyncCommands.php` | `@entity_type.manager` | `MIGRATED` |
| `lib/LegacyCompat.php` | `class LegacyCompat` | `LEGACY_OBSOLETE` | N/A | N/A | `OBSOLETE` |

---

## 4. hook_menu() Decomposition Mapping Matrix

| Legacy D7 Path | Callback (`page callback` / `drupal_get_form`) | Access Check (`access callback`) | Target D10 Route | Target D10 Controller / Form Class | Menu Link / Local Task Target |
|---|---|---|---|---|---|
| `admin/config/{{ COMPONENT }}` | `drupal_get_form('{{ COMPONENT }}_admin')` | `user_access('administer')` | `{{ COMPONENT }}.admin` | `src/Form/AdminSettingsForm.php` | `.links.menu.yml` |
| `{{ COMPONENT }}/item/%` | `{{ COMPONENT }}_view_item` | `{{ COMPONENT }}_item_access` | `{{ COMPONENT }}.item_view` | `src/Controller/ItemController.php` | N/A |

---

## 5. File Mapping & Scaffolding Checklist

| Action | Target D10 File | Source D7 Origin | Architectural Purpose |
|---|---|---|---|
| CREATED | `{{ COMPONENT }}.info.yml` | `{{ COMPONENT }}.info` | Module metadata |
| CREATED | `{{ COMPONENT }}.services.yml` | N/A | Service container definitions |
| CREATED | `{{ COMPONENT }}.routing.yml` | `hook_menu()` | Route definitions |
| CREATED | `{{ COMPONENT }}.libraries.yml` | `{{ COMPONENT }}.info` scripts/stylesheets | Library definitions |
| CREATED | `config/install/views.view.{{ COMPONENT }}_content_listing.yml` | `{{ COMPONENT }}.views_default.inc` | Views configuration |
| CREATED | `src/Entity/RecordEntity.php` | `hook_entity_info()` | Modern Content Entity class |
| CREATED | `src/Form/FilterForm.php` | `{{ COMPONENT }}_filter_form` | Modern FormBase class with AJAX handlers |
| CREATED | `src/Service/ExampleProcessor.php` | `lib/ExampleProcessor.php` | Modernized PSR-4 service class with constructor DI |
| CREATED | `templates/node/node--article.html.twig` | `templates/node--article.tpl.php` | Modern Twig template |
| CREATED | `{{ COMPONENT }}.theme` | `template.php` | Theme preprocess & suggestions |

---

## 6. Test Strategy
- **Unit Test**: `tests/src/Unit/ExampleProcessorTest.php`
- **Kernel Test**: `tests/src/Kernel/IntegrationTest.php`
- **Entity Test**: `tests/src/Kernel/RecordEntityTest.php`
- **Form Test**: `tests/src/Kernel/FilterFormTest.php`
- **Frontend / Library Test**: `tests/src/Kernel/LibraryRegistrationTest.php`
- **Views Test**: `tests/src/Kernel/ViewsConfigurationTest.php`
- **Theme & Twig Test**: `tests/src/Kernel/ThemeTemplateTest.php`


---

## 7. Potential Risks, Assumptions & Unverified Results
- **[ASSUMPTION]**:
- **[UNVERIFIED RESULT]**:
- **Mitigation Strategy**:
