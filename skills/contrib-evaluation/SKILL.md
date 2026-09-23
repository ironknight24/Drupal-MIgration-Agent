---
name: contrib-evaluation
description: Contributed Module Strategy & Compatibility Evaluation Playbook. Assesses D7 contrib modules against modern Drupal 10/11 ecosystems, core consolidations, and community replacements.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep
---

# Contributed Module Strategy & Compatibility Evaluation Skill

## Overview
This skill provides the decision frameworks and evaluation heuristics for assessing Drupal 7 contributed modules against the modern Drupal 10 and Drupal 11 ecosystem. It determines core consolidations, community replacements, and compatibility paths without mutating the target environment.

---

## Technical References
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)

---

## The 8 Mandatory Assessment Criteria

For every D7 contrib module evaluated, document:
1. **Target Core Availability**: Is there an official compatible release on Drupal.org / Packagist? (`[OBSERVED FACT]`).
2. **Release Stability & D11 Readiness**: Is the release stable, RC, or alpha? Does it support Drupal 11?
3. **Core Consolidation**: Has the functionality been absorbed into Drupal core? (e.g., Views, Date, Entity API, CKEditor, Breakpoint, Email, Link, Telephone).
4. **Community Replacement**: If abandoned, has the community standardized on an alternative? (e.g., Webform 7.x -> Webform 6.x in D10/D11; Bean -> Block Content; Panopoly -> Layout Builder).
5. **Custom Port Requirement**: Does the module require custom re-implementation due to unique custom patches or lack of modern equivalents?
6. **Configuration Migration**: Does the module store configuration that must be translated into CMI YAML?
7. **Data Migration**: Does the module own custom database tables or field tables that require Migration API pipelines?
8. **Custom Module Couplings**: Which custom modules invoke hooks, plugins, or APIs provided by this contrib module?

---

## Target Version Architecture: Drupal 11 Removed Core Extensions

```text
Drupal 11 removed/deprecated core extensions (e.g., action, book, forum,
statistics, tracker) must be evaluated individually.

For every affected component:
1. Determine whether equivalent functionality exists in target core.
2. Determine whether a contributed replacement exists.
3. Determine whether a custom implementation is required.
4. Determine whether the functionality is actually used by the source project.
5. Record the evidence.
6. Record the migration decision.
7. Record any functional gap or accepted change.

Never assume that removal from Drupal core means that the business
functionality must be removed.
```

---

## Categorization Taxonomy

Assign one of the following standard statuses to each evaluated module:

- `CORE_MERGED`: Functionality provided natively by the target Drupal core version.
- `D10_AVAILABLE`: Official compatible port exists for Drupal 10.
- `D11_READY`: Official compatible port exists for both Drupal 10 and Drupal 11.
- `COMMUNITY_REPLACEMENT`: Modern community replacement module identified.
- `ARCHITECTURAL_REPLACEMENT`: Modern architectural subsystem replacement identified requiring behavioral mapping.
- `CUSTOM_REIMPLEMENTATION`: Bespoke code or custom service required.
- `OBSOLETE`: No longer needed in modern Drupal architectures.

---

## Architectural Replacement vs Direct Port Evaluation
When evaluating modules where the modern ecosystem has evolved beyond a 1:1 port:
1. **Repository Evidence First**: Inspect `composer.json`, installed modules, and target custom code to discover which modern subsystem is present in the target environment.
2. **Behavioral Scope Analysis**: Assess whether the target replacement covers all source behaviors (memberships, access, entities, forms, cache invalidation) or leaves gaps.
3. **No Blind Porting**: Prevent literal API ports when an architectural replacement exists; route to Behavioral Mapping protocol.

---

## Safety & Non-Destructive Guardrails (Rule 7)
- **Strictly Advisory**: Never execute `composer require` or modify `composer.json` unilaterally.
- **Evidence Citation**: Cite exact project versions, Drupal.org project URLs, or core change records for all claims.
