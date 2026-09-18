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
- **Hooks & Endpoints**: [OBSERVED FACT]
- **Business Logic Rules**: [OBSERVED FACT]
- **Autoloading / Include Tree**: [OBSERVED FACT]

---

## 2. Target Drupal 10 Architecture (D11-Ready)
- **Target Namespace**: `Drupal\{{ COMPONENT }}`
- **Services & Constructor Dependency Injection**:
  - `Drupal\{{ COMPONENT }}\Service\BusinessService` (injected with `Connection`, `EntityTypeManagerInterface`)
- **Routing & Controllers**:
  - Route name: `{{ COMPONENT }}.main` -> `Drupal\{{ COMPONENT }}\Controller\MainController::index`
- **Plugins / Event Subscribers**:
- **Form Classes**: `Drupal\{{ COMPONENT }}\Form\SettingsForm` (`ConfigFormBase`)
- **Drush Commands**: `Drupal\{{ COMPONENT }}\Drush\Commands\{{ COMPONENT_CAMEL }}Commands`

---

## 3. File-to-Class/Function Accounting & D10 Architectural Mapping

| D7 Source File | Legacy Class / Callable | Legacy Constructor / Init | Architectural Classification | Target D10 Class / Service | Injected Services (DI) | Planned Outcome Status |
|---|---|---|---|---|---|---|
| `lib/ExampleProcessor.php` | `class ExampleProcessor` | `ExampleProcessor($db)` | `SERVICE_BUSINESS_LOGIC` | `src/Service/ExampleProcessor.php` | `@database`, `@config.factory` | `MIGRATED` |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_view()` | N/A | `CONTROLLER` | `src/Controller/ViewController.php` | `@current_user` | `MIGRATED` |
| `includes/admin.inc` | `{{ COMPONENT }}_admin_settings()` | N/A | `FORM` | `src/Form/SettingsForm.php` | `@config.factory` | `MIGRATED` |
| `includes/helper.inc` | `{{ COMPONENT }}_calculate_tax()` | N/A | `SERVICE_BUSINESS_LOGIC` | `src/Service/CalculationService.php` | N/A | `MIGRATED` |
| `includes/drush.inc` | `drush_{{ COMPONENT }}_sync()` | N/A | `DRUSH_COMMAND` | `src/Drush/Commands/SyncCommands.php` | `@entity_type.manager` | `MIGRATED` |
| `lib/LegacyCompat.php` | `class LegacyCompat` | `none` | `LEGACY_OBSOLETE` | N/A | N/A | `OBSOLETE` |

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
