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
| `example_module` | `modules/custom/example` | `example.module`, `includes/admin.inc`, `includes/helper.inc` | 420 | `hook_menu`, `hook_form_alter` | Yes | `not_started` |

---

## 4. Legacy .inc File & Inclusion Graph Inventory

| Module | Relative Path | Inclusion Mechanism (`include`, `module_load_include`, `hook_menu`) | Extracted Functions & Callables | Functional Classification | Drush Commands |
|---|---|---|---|---|---|
| `example_module` | `includes/admin.inc` | `module_load_include('inc', 'example_module', 'includes/admin')` | `example_admin_settings_form()`, `example_admin_validate()` | `FORM_HANDLER` | None |
| `example_module` | `includes/drush.inc` | `hook_drush_command()` | `drush_example_sync()` | `DRUSH_COMMAND` | `example-sync` |

---

## 5. Contributed Modules Inventory

| Contrib Module | D7 Version | Core in D10? | D10 Available? | Community Replacement | Action Plan |
|---|---|---|---|---|---|
| `views` | 7.x-3.24 | Yes | Core | `drupal/core` | Core migration |
| `ctools` | 7.x-1.15 | Partial | Yes (4.x) | `drupal/ctools` | Composer require |

---

## 6. Custom Themes Inventory

| Theme Name | Path | Base Theme | Template Files (.tpl.php) | Preprocess Functions |
|---|---|---|---|---|
| `example_theme` | `themes/custom/example` | None | 14 | 6 |

---

## 7. Entity & Data Architecture
- **Content Types**:
- **Taxonomy Vocabularies**:
- **Custom SQL Tables**:
- **User Roles & Permissions**:

---

## 8. Integrations, External Endpoints & Drush Commands
- **Webhooks & APIs**:
- **Authentication Protocols**:
- **Custom Drush Commands**:

---

## 9. Baseline Audit Findings & Risks
- **Risk Assessment**:
- **Recommended Sequence Overrides**:
