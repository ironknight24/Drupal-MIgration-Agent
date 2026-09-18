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

---

## 2. 12-Dimensional Behavioral Comparison Matrix

| Dimension | D7 Expected / Baseline Behavior | D10 Implemented Behavior | Verdict | Evidence / Reference |
|---|---|---|---|---|
| **1. Functionality** | | | `PASS` | |
| **2. Business Rules** | | | `PASS` | |
| **3. Permissions & Access**| | | `PASS` | |
| **4. Data Integrity** | | | `PASS` | |
| **5. Relationships** | | | `PASS` | |
| **6. Configuration** | | | `PASS` | |
| **7. Routes & URLs** | | | `PASS` | |
| **8. Forms** | | | `PASS` | |
| **9. Integrations** | | | `PASS` | |
| **10. Output & Markup** | | | `PASS` | |
| **11. Workflows** | | | `PASS` | |
| **12. Performance** | | | `PASS` | |

---

## 3. Detailed Evidence Logs

### Automated Test Logs
```
{{ TEST_COMMAND_OUTPUT }}
```

### Behavioral Output Comparison
- **D7 Observed**: [OBSERVED FACT]
- **D10 Implemented**: [VERIFIED RESULT]

---

## 4. Discrepancies & Gaps (if any)
- **Identified Gaps**:
- **Action Required**:
