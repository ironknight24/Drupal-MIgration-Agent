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
- **Discovered Source Files**: [OBSERVED FACT] (`.module`, `.inc`, `.install`, `.php`)
- **Key Functionality**: [OBSERVED FACT]
- **Hooks & Endpoints**: [OBSERVED FACT]
- **Business Logic Rules**: [OBSERVED FACT]
- **Include / Require Tree**: [OBSERVED FACT]

---

## 2. Target Drupal 10 Architecture (D11-Ready)
- **Target Namespace**: `Drupal\{{ COMPONENT }}`
- **Services & Dependency Injection**:
  - `Drupal\{{ COMPONENT }}\Service\BusinessService` (injected with `Connection`, `EntityTypeManagerInterface`)
- **Routing & Controllers**:
  - Route name: `{{ COMPONENT }}.main` -> `Drupal\{{ COMPONENT }}\Controller\MainController::index`
- **Plugins / Event Subscribers**:
- **Form Classes**: `Drupal\{{ COMPONENT }}\Form\SettingsForm` (`ConfigFormBase`)
- **Drush Commands**: `Drupal\{{ COMPONENT }}\Drush\Commands\{{ COMPONENT_CAMEL }}Commands`

---

## 3. File-to-Functionality Accounting & D10 Architectural Mapping

| D7 Source File | Legacy Function / Callable | Functional Classification | Target D10 Class / Service | Planned Outcome Status |
|---|---|---|---|---|
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_view()` | `CONTROLLER_PAGE` | `src/Controller/ViewController.php` | `MIGRATED` |
| `includes/admin.inc` | `{{ COMPONENT }}_admin_settings()` | `FORM_HANDLER` | `src/Form/SettingsForm.php` | `MIGRATED` |
| `includes/helper.inc` | `{{ COMPONENT }}_calculate_tax()` | `SERVICE_BUSINESS_LOGIC` | `src/Service/CalculationService.php` | `MIGRATED` |
| `includes/drush.inc` | `drush_{{ COMPONENT }}_sync()` | `DRUSH_COMMAND` | `src/Drush/Commands/SyncCommands.php` | `MIGRATED` |
| `includes/legacy.inc` | `{{ COMPONENT }}_d6_compat()` | `LEGACY_OBSOLETE` | N/A | `OBSOLETE` |

---

## 4. File Mapping & Scaffolding Checklist

| Action | Target D10 File | Source D7 Origin | Architectural Purpose |
|---|---|---|---|
| CREATED | `{{ COMPONENT }}.info.yml` | `{{ COMPONENT }}.info` | Module metadata |
| CREATED | `{{ COMPONENT }}.services.yml` | N/A | Service container definitions |
| CREATED | `{{ COMPONENT }}.routing.yml` | `hook_menu()` | Route definitions |
| CREATED | `src/Service/MyService.php` | `includes/helper.inc` | Modernized OOP business logic with DI |

---

## 5. Test Strategy
- **Unit Test**: `tests/src/Unit/MyServiceTest.php`
- **Kernel Test**: `tests/src/Kernel/IntegrationTest.php`

---

## 6. Potential Risks, Assumptions & Unverified Results
- **[ASSUMPTION]**:
- **[UNVERIFIED RESULT]**:
- **Mitigation Strategy**:
