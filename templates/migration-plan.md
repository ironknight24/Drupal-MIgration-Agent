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

## 1. D7 Baseline Behavior & Analysis
- **Source Files**: [OBSERVED FACT]
- **Key Functionality**: [OBSERVED FACT]
- **Hooks & Endpoints**: [OBSERVED FACT]
- **Business Logic Rules**: [OBSERVED FACT]

---

## 2. Target Drupal 10 Architecture (D11-Ready)
- **Target Namespace**: `Drupal\{{ COMPONENT }}`
- **Services & Dependency Injection**:
  - `Drupal\{{ COMPONENT }}\Service\BusinessService` (injected with `Connection`, `EntityTypeManagerInterface`)
- **Routing & Controllers**:
  - Route name: `{{ COMPONENT }}.main` -> `Drupal\{{ COMPONENT }}\Controller\MainController::index`
- **Plugins / Event Subscribers**:
- **Form Classes**: `Drupal\{{ COMPONENT }}\Form\SettingsForm` (`ConfigFormBase`)

---

## 3. File Mapping & Implementation Checklist

| Action | Target D10 File | Source D7 Origin | Architectural Purpose |
|---|---|---|---|
| CREATED | `{{ COMPONENT }}.info.yml` | `{{ COMPONENT }}.info` | Module metadata |
| CREATED | `{{ COMPONENT }}.services.yml` | N/A | Service container definitions |
| CREATED | `{{ COMPONENT }}.routing.yml` | `hook_menu()` | Route definitions |
| CREATED | `src/Service/MyService.php` | `{{ COMPONENT }}.module` | OOP business logic with DI |

---

## 4. Test Strategy
- **Unit Test**: `tests/src/Unit/MyServiceTest.php`
- **Kernel Test**: `tests/src/Kernel/IntegrationTest.php`

---

## 5. Potential Risks & Assumptions
- **[ASSUMPTION]**:
- **Mitigation Strategy**:
