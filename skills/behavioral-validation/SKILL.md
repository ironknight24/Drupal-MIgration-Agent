---
name: behavioral-validation
description: 12-Dimensional Comparative Behavioral Validation Playbook with exhaustive custom PHP file, class, constructor, procedural hook, custom hook, database schema, configuration, state, entity, bundle, field, revision, translation, form, AJAX, frontend JavaScript/CSS, Views/custom plugin, Theme template/preprocess/theme hook, Dynamic runtime dependency, and External Integration outcome auditing.
version: 1.11.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# 12-Dimensional Comparative Behavioral Validation Skill

## Overview
This skill provides the operational audit methodology and evidence standards for conducting rigorous side-by-side behavioral comparisons between the Drupal 7 baseline and the migrated Drupal 10/11 implementation across 12 distinct functional dimensions, including exhaustive accounting and outcome verification for legacy custom PHP files, OOP classes, constructors, methods, procedural hooks, custom hooks, alter hooks, custom database schemas, configuration, state, persistent variables, custom entities, bundles, fields, revisions, translations, forms, form alters, AJAX callbacks, frontend JavaScript behaviors, CSS stylesheets, asset libraries, Views definitions, displays, custom Views plugins, query alterations, theme `.info` definitions, PHPTemplate `.tpl.php` templates, theme functions, `hook_theme()` registrations, preprocess/process hooks, template suggestions, theme regions, theme settings, dynamic runtime dependencies, external integrations (outbound HTTP, REST/SOAP clients, inbound webhooks, API endpoints, payment gateways, email/SMS services, remote storage/SFTP, external databases, queue workers, third-party SDKs, and CLI binaries), and `.inc` files.

---

## Technical References
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
- [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)

---

## The 12-Dimensional Validation Matrix

Every evaluated component must be audited across the following 12 dimensions:

| # | Dimension | Audit Criteria | Empirical Proof Required |
| :-: | :--- | :--- | :--- |
| 1 | **Functionality** | Do core module features, custom classes, procedural hooks, entities, Views, dynamic plugin managers, external gateway services, and UI actions produce equivalent outcomes? | Execution test output or automated assertion. |
| 2 | **Business Rules** | Are calculations, state transitions, constraints, and validation rules preserved? | Unit test result or verified calculation comparison. |
| 3 | **Permissions & Access** | Are route requirements, entity access checks, custom access control handlers, Views access rules, and role permissions correctly enforced? | Access check log / automated kernel test asserting 403 vs 200. |
| 4 | **Data Integrity** | Are record, entity, revision, and translation row counts, UTF-8 character sets, and timestamps preserved without truncation? | Database row count query output comparing D7 to D10. |
| 5 | **Relationships** | Are entity references, parent-child links, Views relationships, and taxonomy associations accurate? | Sample query verifying target entity reference IDs. |
| 6 | **Configuration & State** | Does exported CMI configuration match intended runtime site behavior? Are State API values, entity type definitions, and Views configurations preserved? | CMI validation against `config/schema/` and State API assertion logs. |
| 7 | **Routes & URLs** | Do legacy paths from `hook_menu()`, Views page displays, route aliases, entity canonical URLs, redirects, and query parameters resolve? | Route definition inspection and HTTP status response. |
| 8 | **Forms & Frontend** | Do form elements, CSRF tokens, AJAX callbacks, entity forms, form alters, Views exposed filters, JavaScript behaviors (`once()`), CSS libraries, and submit handlers behave correctly? | Form submit assertion log, JS behavior test, or functional test. |
| 9 | **Integrations** | Do outbound payloads, webhook responses, event subscribers, Views REST exports, Guzzle gateway services, and API auth mechanisms conform to specifications with zero secrets in CMI? | Integration test log with mock API response assertions. |
| 10 | **Output & Markup** | Does rendered Twig template markup, entity view builder output, Views displays, theme regions, and theme functions meet visual, semantic, and accessibility standards? | HTML diff or render array inspection. |
| 11 | **Workflows** | Do content moderation transitions, revisions, and publication states function identically? | Moderation state log or revision history assertion. |
| 12 | **Performance** | Are database queries indexed, Views queries optimized, cache contexts attached, and memory limits respected? | Query log or cache tag verification. |

---

## Mandatory Custom Code, Hook, Database, Configuration, Entity, Form, Frontend, Views, Theme, Dynamic & Integration Outcome Accounting

In addition to the 12 functional dimensions, validate that every custom PHP source file, class, interface, trait, constructor, method, procedural hook implementation, custom hook, alter hook, `.inc` file, custom database table, stored data-model artifact, configuration/state/variable artifact, custom entity type, bundle, field definition, revision table, translation artifact, form builder, form alter, AJAX callback, JavaScript file, behavior, CSS stylesheet, library definition, View definition, display, custom Views plugin, query alteration, theme `.info` definition, PHPTemplate `.tpl.php` template, theme function, `hook_theme()` registration, preprocess/process hook, template suggestion, theme region, theme settings form, dynamic runtime dependency, and external integration discovered in the D7 source has reached an approved, certified outcome:

### Approved Outcome States
- **`MIGRATED`**: The class/function/hook/table/variable/entity/field/form/AJAX callback/JS behavior/CSS library/View definition/Views plugin/theme template/preprocess hook/theme setting/dynamic callable/external integration has been re-engineered into a target D10 PSR-4 class, service, repository, event subscriber, controller, `FormBase`, `ConfigFormBase`, `ConfirmFormBase`, `ContentEntityForm`, plugin, plugin manager, gateway service, webhook controller, Config Object, State API key, `@ContentEntityType`, `@ConfigEntityType`, CMI field configuration, `<module>.libraries.yml` asset, `views.view.*.yml` configuration, Twig template (`.html.twig`), `<theme>.theme` preprocess function, or CMI theme configuration with verified tests.
- **`REPLACED`**: The legacy behavior/hook/table/variable/entity/field/form/frontend asset/View/theme function/dynamic pattern/external SDK is superseded by a modern Drupal 10 core API (e.g. Media, Workflows, Views exposed forms, Core Dialog, JSON:API, Twig, Single Directory Components, Plugin API, Guzzle HTTP client), contrib module, or service with documented mapping.
- **`OBSOLETE`**: The functionality/hook/table/variable/entity/field/form/frontend asset/View/theme template/dynamic callable/integration is dead code, temporary cache, deprecated polyfill, or obsolete API with documented evidence.
- **`EXCLUDED_WITH_REASON`**: Explicitly excluded from migration scope with documented business/architectural rationale.
- **`HUMAN_DECISION_REQUIRED`**: Unresolved business logic, ambiguous hook semantics, ambiguous schema relationships, entity architecture decisions, dynamic form IDs, ambiguous security flows, third-party library decisions, dynamic View dispatches, dynamic theme suggestions, credentials/secrets, dynamic callables, unverified external endpoints, or unverified dynamic SQL flagged for human decision in `reports/blocked/`.
- **`UNVERIFIED`**: Dynamic behavior, dynamic variable keys, dynamic field types, dynamic form builders, unverified AJAX endpoints, dynamic JS asset paths, dynamic View IDs, dynamic template suggestions, dynamic callables, external staging endpoints, or runtime database state that cannot be statically verified, explicitly marked with `[UNVERIFIED RESULT]` and retaining status `[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]`.

### Forbidden States (Immediate Validation `FAIL`)
- **`UNACCOUNTED`**: Any custom PHP file, class, constructor, method, procedural hook, custom hook, `.inc` file, custom database table, configuration/state variable, entity type, bundle, field, form, form alter, AJAX callback, JavaScript file, behavior, CSS stylesheet, View definition, custom Views plugin, theme `.info`, template, theme function, preprocess hook, dynamic dependency, or external integration present in discovery but missing from the migration plan or report.
- **`UNKNOWN_WITHOUT_REASON`**: Any excluded or omitted code, hook, database table, variable, entity, field, form, AJAX callback, frontend asset, View, Views plugin, theme template, theme function, dynamic dependency, or external integration lacking documented technical or business rationale.
- **`SILENTLY_OMITTED`**: Any code, hook, database table, variable, entity, field, form, AJAX callback, frontend asset, View, Views plugin, theme template, theme function, dynamic dependency, or external integration dropped during refactoring without an explicit record.

---

## Verdict Standards & Proof Rules

Assign strictly one verdict per dimension:

- **`PASS`**: Feature is fully equivalent to the D7 baseline and all custom PHP files, classes, procedural hooks, database tables, variables, entities/fields, forms, AJAX callbacks, frontend assets, Views definitions, plugins, themes, templates, preprocess hooks, dynamic dependencies, and external integrations are accounted for. **Mandatory**: Must cite an empirical terminal log, test result, or code diff.
- **`PARTIAL`**: Core behavior works, but minor non-blocking divergence is noted. **Mandatory**: Discrepancy must be documented with impact assessed as low.
- **`FAIL`**: Functional divergence, data corruption, broken calculation, access vulnerability, or unaccounted custom code/hooks/entities/fields/forms/frontend assets/Views/themes/templates/dynamic dependencies/external integrations detected. **Mandatory**: Detailed reproduction steps and failing output must be documented.
- **`BLOCKED`**: An upstream missing dependency or environmental failure prevented verification. **Mandatory**: Upstream ticket reference must be cited.
- **`N/A`**: Dimension does not apply to this specific component. **Mandatory**: Architectural rationale must be stated.
