---
report_id: "VALIDATION-{{ COMPONENT }}-{{ DATE }}"
component: "{{ COMPONENT }}"
category: "validation"
agent: "validation"
created_at: "{{ TIMESTAMP }}"
verdict: "{{ OVERALL_VERDICT }}" # PASS | PARTIAL | FAIL | BLOCKED
evidence_summary:
  observed_facts: 0
  inferences: 0
  proposals: 0
  assumptions: 0
  verified_results: 0
---

# Behavioral Validation Report: {{ COMPONENT }}

## 1. Validation Summary
- **Component**: `{{ COMPONENT }}`
- **Overall Verdict**: `{{ OVERALL_VERDICT }}`
- **Automated Tests Executed**: {{ TESTS_COUNT }}
- **Manual Verification Checks**: {{ CHECKS_COUNT }}
- **Custom PHP Classes Accounted For**: {{ CLASSES_ACCOUNTED_COUNT }} / {{ CLASSES_TOTAL_COUNT }}
- **Procedural Hooks Accounted For**: {{ HOOKS_ACCOUNTED_COUNT }} / {{ HOOKS_TOTAL_COUNT }}
- **Legacy .inc Files Accounted For**: {{ INC_ACCOUNTED_COUNT }} / {{ INC_TOTAL_COUNT }}
- **Custom Database Tables Accounted For**: {{ TABLES_ACCOUNTED_COUNT }} / {{ TABLES_TOTAL_COUNT }}
- **Configuration & State Items Accounted For**: {{ CONFIG_ACCOUNTED_COUNT }} / {{ CONFIG_TOTAL_COUNT }}
- **Custom Entity Types Accounted For**: {{ ENTITIES_ACCOUNTED_COUNT }} / {{ ENTITIES_TOTAL_COUNT }}
- **Fields & Instances Accounted For**: {{ FIELDS_ACCOUNTED_COUNT }} / {{ FIELDS_TOTAL_COUNT }}
- **Revision Tables Accounted For**: {{ REVISIONS_ACCOUNTED_COUNT }} / {{ REVISIONS_TOTAL_COUNT }}
- **Translation Artifacts Accounted For**: {{ TRANSLATIONS_ACCOUNTED_COUNT }} / {{ TRANSLATIONS_TOTAL_COUNT }}

---

## 2. 12-Dimensional Behavioral Comparison Matrix

| Dimension | D7 Expected / Baseline Behavior | D10 Implemented Behavior | Verdict | Evidence / Reference |
|---|---|---|---|---|
| **1. Functionality** | | | `PASS` | |
| **2. Business Rules** | | | `PASS` | |
| **3. Permissions & Access**| | | `PASS` | |
| **4. Data Integrity** | | | `PASS` | |
| **5. Relationships** | | | `PASS` | |
| **6. Configuration & State** | | | `PASS` | |
| **7. Routes & URLs** | | | `PASS` | |
| **8. Forms** | | | `PASS` | |
| **9. Integrations** | | | `PASS` | |
| **10. Output & Markup** | | | `PASS` | |
| **11. Workflows** | | | `PASS` | |
| **12. Performance** | | | `PASS` | |

---

## 3. Custom Class, Hook, Database, Entity & Configuration Outcome Verification

| D7 Source File / Schema / Key / Entity | Class / Hook / Table / Variable / Field | Legacy Dependencies / Fallback | D10 Target Implementation | Final Outcome Status | Verification Evidence / Reason |
|---|---|---|---|---|---|
| `lib/ExampleProcessor.php` | `class ExampleProcessor` | `ExampleProcessor($db)` | `src/Service/ExampleProcessor.php` | `MIGRATED` | Service construction & Unit test passed |
| `{{ COMPONENT }}.module:hook_entity_info` | `entity: {{ COMPONENT }}_record` | `hook_entity_info` | `src/Entity/RecordEntity.php` | `MIGRATED` | Entity CRUD & access control test passed |
| `{{ COMPONENT }}.install:hook_schema` | `table: {{ COMPONENT }}_record_revision` | `revision table` | `src/Entity/RecordEntity.php` (`revision_table`) | `MIGRATED` | Revision creation & history loading verified |
| `{{ COMPONENT }}.module:hook_field_info` | `field: field_related_item` | `entityreference` | `field.storage.record.field_related_item` | `MIGRATED` | Reference integrity & lookup verified |
| `{{ COMPONENT }}.install` | `table: {{ COMPONENT }}_records` | `hook_schema: record_id, uid` | `src/Entity/RecordEntity.php` | `MIGRATED` | Entity CRUD & migration test verified |
| `includes/admin.inc:24` | `variable: {{ COMPONENT }}_endpoint` | `https://api.example.com` | `config/install/{{ COMPONENT }}.settings.yml` | `MIGRATED` | Schema test & ConfigForm submit verified |
| `{{ COMPONENT }}.module:110` | `variable: {{ COMPONENT }}_last_sync` | `0` (int) | `State API` (`{{ COMPONENT }}.last_sync`) | `MIGRATED` | State persistence kernel test passed |
| `includes/admin.inc:48` | `variable: {{ COMPONENT }}_api_key` | `""` (secret) | `settings.php` override / Key module | `MIGRATED` | Zero secrets in CMI assertion passed |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_menu()` | `hook_menu` | `.routing.yml`, `src/Controller/` | `MIGRATED` | Route & controller response verified |
| `{{ COMPONENT }}.module` | `{{ COMPONENT }}_form_alter()` | `hook_form_alter` | `src/Service/FormAlterService.php` | `MIGRATED` | Form alter unit test passed |
| `includes/admin.inc` | `{{ COMPONENT }}_admin_settings()` | N/A | `src/Form/SettingsForm.php` | `MIGRATED` | Form submission unit test passed |
| `includes/helper.inc` | `{{ COMPONENT }}_calc()` | N/A | `src/Service/CalcService.php` | `MIGRATED` | Kernel test verified math parity |
| `includes/drush.inc` | `drush_{{ COMPONENT }}_sync()` | N/A | `src/Drush/Commands/SyncCommands.php` | `MIGRATED` | CLI execution verified |
| `lib/LegacyCompat.php` | `class LegacyCompat` | `none` | N/A | `OBSOLETE` | Deprecated D6 compatibility shim |

---

## 4. Detailed Evidence Logs

### Automated Test Logs
```
{{ TEST_COMMAND_OUTPUT }}
```

### Behavioral Output Comparison
- **D7 Observed**: [OBSERVED FACT]
- **D10 Implemented**: [VERIFIED RESULT]

---

## 5. Discrepancies & Gaps (if any)
- **Identified Gaps**:
- **Action Required**:
