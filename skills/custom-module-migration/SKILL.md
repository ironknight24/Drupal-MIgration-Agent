---
name: custom-module-migration
description: Comprehensive 12-step engineering playbook for migrating custom Drupal 7 modules into modern Drupal 10/11 modules. Use when re-engineering custom legacy modules.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Custom Module Modernization Playbook Skill

## Overview
This skill provides the operational engineering playbook for re-engineering Drupal 7 custom modules into modern, object-oriented Drupal 10 and Drupal 11 modules without altering source files.

---

## Technical References & Associated Skills
- Associated Skills:
  - [`skills/d7-to-d10-mapping`](../d7-to-d10-mapping/SKILL.md)
  - [`skills/d10-architecture`](../d10-architecture/SKILL.md)
- Canonical References:
  - [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
  - [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)
  - [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)

---

## Target-Version Resolution
Determine target version from project configuration (`target.core_version`):
- For **Drupal 10.x**: Target PHP >= 8.1; use DocBlock annotations or PHP Attributes where supported.
- For **Drupal 11.x**: Target PHP >= 8.3; prefer PHP 8 Attributes for all supported plugins; ensure strict return types.

---

## The 12-Step Modernization Playbook

1. **Step 1: Inventory & Asset Discovery**
   - Catalog all source files (`.info`, `.module`, `.inc`, `.install`, `.js`, `.css`) and code volume.
2. **Step 2: Dependency Mapping**
   - Identify core module, contrib module, and custom module dependencies using `skills/dependency-analysis`.
3. **Step 3: Business Behavior Extraction**
   - Document user journeys, business rules, calculations, permissions, and edge cases.
4. **Step 4: Legacy API Audit**
   - Audit hook implementations, direct DB queries, and global variables against `references/drupal-7/hooks.md`.
5. **Step 5: Modern Architecture Design**
   - Design OOP namespace, services (`.services.yml`), controllers, form classes, and routing (`.routing.yml`).
6. **Step 6: Target-Ready Design Review**
   - Enforce constructor Dependency Injection, typehints; eliminate deprecated APIs.
7. **Step 7: Migration Plan Formulation**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
8. **Step 8: Controlled Implementation**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`, `.permissions.yml`).
   - Implement services, controllers, forms, and plugins strictly inside `target.path/web/modules/custom/<MODULE>/`.
   - Log all file creations and modifications in `logs/file-change-log/`.
9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting core business logic using `skills/testing`.
10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications using `skills/behavioral-validation`.
11. **Step 11: Gap Analysis**
    - Document any intentionally altered or deprecated legacy behavior.
12. **Step 12: Sign-Off & Manifest Update**
    - Update component status to `completed` in `state/migration-manifest.yml`.
