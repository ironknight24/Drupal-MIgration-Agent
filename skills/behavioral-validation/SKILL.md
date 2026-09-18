---
name: behavioral-validation
description: 12-Dimensional Comparative Behavioral Validation Playbook with exhaustive custom PHP file, class, constructor, and .inc file outcome auditing.
version: 1.2.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# 12-Dimensional Comparative Behavioral Validation Skill

## Overview
This skill provides the operational audit methodology and evidence standards for conducting rigorous side-by-side behavioral comparisons between the Drupal 7 baseline and the migrated Drupal 10/11 implementation across 12 distinct functional dimensions, including exhaustive accounting and outcome verification for legacy custom PHP files, OOP classes, constructors, methods, and `.inc` files.

---

## Technical References
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
- [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)

---

## The 12-Dimensional Validation Matrix

Every evaluated component must be audited across the following 12 dimensions:

| # | Dimension | Audit Criteria | Empirical Proof Required |
| :-: | :--- | :--- | :--- |
| 1 | **Functionality** | Do core module features, custom classes, and UI actions produce equivalent outcomes? | Execution test output or automated assertion. |
| 2 | **Business Rules** | Are calculations, state transitions, constraints, and validation rules preserved? | Unit test result or verified calculation comparison. |
| 3 | **Permissions & Access** | Are route requirements, entity access checks, and role permissions correctly enforced? | Access check log / automated kernel test asserting 403 vs 200. |
| 4 | **Data Integrity** | Are record counts, UTF-8 character sets, and timestamps preserved without truncation? | Database count query output comparing D7 to D10. |
| 5 | **Relationships** | Are entity references, parent-child links, and taxonomy associations accurate? | Sample query verifying target entity reference IDs. |
| 6 | **Configuration** | Does exported CMI configuration match intended runtime site behavior? | CMI validation against `config/schema/`. |
| 7 | **Routes & URLs** | Do legacy paths, route aliases, redirects, and query parameters resolve? | Route definition inspection and HTTP status response. |
| 8 | **Forms** | Do form elements, CSRF tokens, AJAX callbacks, and submit handlers behave correctly? | Form submit assertion log or functional test. |
| 9 | **Integrations** | Do outbound payloads, webhook responses, and API auth mechanisms conform to specifications? | Integration test log with mock API response assertions. |
| 10 | **Output & Markup** | Does rendered Twig template markup meet visual, semantic, and accessibility standards? | HTML diff or render array inspection. |
| 11 | **Workflows** | Do content moderation transitions, revisions, and publication states function identically? | Moderation state log or revision history assertion. |
| 12 | **Performance** | Are database queries indexed, cache contexts attached, and memory limits respected? | Query log or cache tag verification. |

---

## Mandatory Custom PHP File, Class & `.inc` Outcome Accounting

In addition to the 12 functional dimensions, validate that every custom PHP source file, class, interface, trait, constructor, method, and `.inc` file discovered in the D7 source has reached an approved, certified outcome:

### Approved Outcome States
- **`MIGRATED`**: The class/function/behavior has been re-engineered into a target D10 PSR-4 class/service with verified tests.
- **`REPLACED`**: The legacy behavior is superseded by a modern Drupal 10 core API, contrib module, or service with documented mapping.
- **`OBSOLETE`**: The functionality is dead code or deprecated API with documented evidence.
- **`EXCLUDED_WITH_REASON`**: Explicitly excluded from migration scope with documented business/architectural rationale.
- **`HUMAN_DECISION_REQUIRED`**: Unresolved business logic or ambiguity flagged for human decision in `reports/blocked/`.
- **`UNVERIFIED`**: Dynamic behavior that cannot be statically verified, explicitly marked with `[UNVERIFIED RESULT]`.

### Forbidden States (Immediate Validation `FAIL`)
- **`UNACCOUNTED`**: Any custom PHP file, class, constructor, method, or `.inc` file present in discovery but missing from the migration plan or report.
- **`UNKNOWN_WITHOUT_REASON`**: Any excluded or omitted code lacking documented technical or business rationale.
- **`SILENTLY_OMITTED`**: Any code dropped during refactoring without an explicit record.

---

## Verdict Standards & Proof Rules

Assign strictly one verdict per dimension:

- **`PASS`**: Feature is fully equivalent to the D7 baseline and all custom PHP files and classes are accounted for. **Mandatory**: Must cite an empirical terminal log, test result, or code diff.
- **`PARTIAL`**: Core behavior works, but minor non-blocking divergence is noted. **Mandatory**: Discrepancy must be documented with impact assessed as low.
- **`FAIL`**: Functional divergence, data corruption, broken calculation, access vulnerability, or unaccounted custom code detected. **Mandatory**: Detailed reproduction steps and failing output must be documented.
- **`BLOCKED`**: An upstream missing dependency or environmental failure prevented verification. **Mandatory**: Upstream ticket reference must be cited.
- **`N/A`**: Dimension does not apply to this specific component. **Mandatory**: Architectural rationale must be stated.
