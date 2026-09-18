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
- **Hooks & Endpoints**: [OBSERVED FACT]
- **Business Logic Rules**: [OBSERVED FACT]
- **Autoloading / Include Tree**: [OBSERVED FACT]

---

## 2. Target Drupal 10 Architecture (D11-Ready)
- **Target Namespace**: `Drupal\{{ COMPONENT }}`
- **Services & Constructor Dependency Injection**:
  - `Drupal\{{ COMPONENT }}\Service\BusinessService` (injected with `Connection`, `EntityTypeManagerInterface`)
- **Database & Repository Architecture**:
  - Content Entity: `Drupal\{{ COMPONENT }}\Entity\RecordEntity`
  - Repository Service: `Drupal\{{ COMPONENT }}\Repository\RecordRepository` (injected with `Connection`)
- **Routing & Controllers**:
  - Route name: `{{ COMPONENT }}.main` -> `Drupal\{{ COMPONENT }}\Controller\MainController::index`
- **Plugins / Event Subscribers**:
- **Form Classes**: `Drupal\{{ COMPONENT }}\Form\SettingsForm` (`ConfigFormBase`)
- **Drush Commands**: `Drupal\{{ COMPONENT }}\Drush\Commands\{{ COMPONENT_CAMEL }}Commands`

---

## 3. File, Class, Procedural Hook & Custom Database Table Accounting & D10 Architectural Mapping

| D7 Source File / Schema | Legacy Artifact / Class / Hook / Table | Classification / Semantics | Target D10 Class / Storage Destination | Migration Strategy / Injected Services | Planned Outcome Status |
|---|---|---|---|---|---|
| `lib/ExampleProcessor.php` | `class ExampleProcessor` | `SERVICE_BUSINESS_LOGIC` | `src/Service/ExampleProcessor.php` | `@database`, `@config.factory` | `MIGRATED` |
| `{{ COMPONENT }}.install` | `table: {{ COMPONENT }}_records` | `USER_DATA` | `src/Entity/RecordEntity.php` | `ENTITY_MIGRATION` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_menu()` | `CORE_HOOK` | `.routing.yml`, `src/Controller/`, `src/Form/`, `.links.menu.yml` | `NON_1_TO_1_DECOMPOSITION` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_form_alter()` | `ALTER_HOOK` | `src/Service/FormAlterService.php` | `@entity_type.manager` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_view()` | `CONTROLLER` | `src/Controller/ViewController.php` | `@current_user` | `MIGRATED` |
| `includes/admin.inc` | `{{ COMPONENT }}_admin_settings()` | `FORM` | `src/Form/SettingsForm.php` | `@config.factory` | `MIGRATED` |
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

## 4. File Mapping & Scaffolding Checklist

| Action | Target D10 File | Source D7 Origin | Architectural Purpose |
|---|---|---|---|
| CREATED | `{{ COMPONENT }}.info.yml` | `{{ COMPONENT }}.info` | Module metadata |
| CREATED | `{{ COMPONENT }}.services.yml` | N/A | Service container definitions |
| CREATED | `{{ COMPONENT }}.routing.yml` | `hook_menu()` | Route definitions |
| CREATED | `src/Service/ExampleProcessor.php` | `lib/ExampleProcessor.php` | Modernized PSR-4 service class with constructor DI |

---

## 5. Test Strategy
- **Unit Test**: `tests/src/Unit/ExampleProcessorTest.php`
- **Kernel Test**: `tests/src/Kernel/IntegrationTest.php`

---

## 6. Potential Risks, Assumptions & Unverified Results
- **[ASSUMPTION]**:
- **[UNVERIFIED RESULT]**:
- **Mitigation Strategy**:
