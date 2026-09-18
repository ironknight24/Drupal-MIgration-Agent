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

## 6. Contributed Modules Inventory

| Contrib Module | D7 Version | Core in D10? | D10 Available? | Community Replacement | Action Plan |
|---|---|---|---|---|---|
| `views` | 7.x-3.24 | Yes | Core | `drupal/core` | Core migration |
| `ctools` | 7.x-1.15 | Partial | Yes (4.x) | `drupal/ctools` | Composer require |

---

## 7. Custom Themes Inventory

| Theme Name | Path | Base Theme | Template Files (.tpl.php) | Preprocess Functions |
|---|---|---|---|---|
| `example_theme` | `themes/custom/example` | None | 14 | 6 |

---

## 8. Custom Database Tables & Data-Model Inventory

| Module | Table Name | Schema Location (`hook_schema`) | Primary Key & Indexes | Entity References (`uid`, `nid`, etc.) | Data Semantics (17 Categories) | Serialization (`PHP_SERIALIZE`, `JSON`, etc.) | CRUD Callers (Create/Read/Update/Delete) | Target Architecture |
|---|---|---|---|---|---|---|---|---|
| `example_module` | `example_records` | `example.install:hook_schema` | PK: `record_id`, Idx: `uid` | `uid` (user) | `USER_DATA` | `PHP_SERIALIZE` | C: `example_save()`, R: `example_load()`, U: `example_update()`, D: `example_delete()` | `CONTENT_ENTITY` |

---

## 9. Entity & Data Architecture
- **Content Types**:
- **Taxonomy Vocabularies**:
- **Custom SQL Tables**:
- **User Roles & Permissions**:

---

## 9. Integrations, External Endpoints & Drush Commands
- **Webhooks & APIs**:
- **Authentication Protocols**:
- **Custom Drush Commands**:

---

## 10. Baseline Audit Findings & Risks
- **Risk Assessment**:
- **Recommended Sequence Overrides**:
