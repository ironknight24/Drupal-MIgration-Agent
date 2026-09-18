---
report_id: "FINAL-AUDIT-{{ DATE }}"
category: "final"
agent: "final-audit"
created_at: "{{ TIMESTAMP }}"
overall_status: "{{ STATUS }}" # APPROVED | CONDITIONALLY_APPROVED | REJECTED
evidence_summary:
  observed_facts: 0
  inferences: 0
  proposals: 0
  assumptions: 0
  verified_results: 0
---

# Final Migration Audit & Sign-off Report

## 1. Migration Overview & Scorecard
- **Project**: {{ PROJECT_NAME }}
- **Migration Path**: Drupal 7 -> Drupal 10 (Drupal 11 Ready)
- **Total Components Discovered**: {{ TOTAL_COMPONENTS }}
- **Components Successfully Migrated**: {{ COMPLETED_COUNT }}
- **Components Blocked / Exception Backlog**: {{ BLOCKED_COUNT }}
- **Overall Migration Success Rate**: {{ SUCCESS_RATE }}%

---

## 2. Component Migration Status Summary

| Category | Total Discovered | Migrated (PASS) | Blocked | Verification Reference |
|---|---|---|---|---|
| **Custom Modules** | | | | |
| **Contrib Modules** | | | | |
| **Custom Themes** | | | | |
| **Configuration** | | | | |
| **Data Pipelines** | | | | |
| **Integrations** | | | | |

---

## 3. Drupal 11 Readiness & Modernization Audit
- [ ] Zero deprecated D10 APIs slated for removal in D11
- [ ] Constructor Dependency Injection utilized across all custom services
- [ ] Zero blind static `\Drupal::*` calls in migrated service classes
- [ ] PHP 8.1+ typing and attributes compliant
- [ ] Twig syntax compliant; zero PHP template tags

---

## 4. Security & Safety Verification
- [ ] Source D7 path verified 100% untouched and unmodified (MD5 checksum verification)
- [ ] Zero passwords, secrets, or API keys committed in code or configuration
- [ ] Permissions and access control verified on all routes
- [ ] Parameterized database queries verified (zero raw string concatenations)

---

## 5. Residual Technical Debt & Human Developer Backlog
- **Active Blocked Tickets**:
  - `BLOCKED-XXX-001`:
- **Recommended Post-Migration Enhancements**:

---

## 6. Final Sign-off
- **Auditor**: `final-audit` agent
- **Date**: {{ DATE }}
- **Final Recommendation**: `{{ RECOMMENDATION }}`
