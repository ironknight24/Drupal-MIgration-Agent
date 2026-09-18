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
This skill provides the step-by-step engineering instructions for modernizing Drupal 7 custom modules into Drupal 10/11 object-oriented modules without altering source files.

---

## The 12-Step Modernization Sequence

1. **Step 1: Inventory**
   - Catalog all source files (`.info`, `.module`, `.inc`, `.install`, `.js`, `.css`).
2. **Step 2: Dependency Analysis**
   - Identify core module, contrib module, and other custom module dependencies.
3. **Step 3: Behavior Extraction**
   - Document user stories, calculations, validation logic, and workflows.
4. **Step 4: D7 API Analysis**
   - Audit hook implementations, direct DB queries, and global variables.
5. **Step 5: D10 Architecture Design**
   - Define module namespace, services, controllers, form classes, and routing.
6. **Step 6: D10/D11-Ready Design Review**
   - Enforce constructor DI, eliminate deprecated APIs, verify type safety.
7. **Step 7: Migration Plan Formulation**
   - Generate `reports/custom-modules/PLAN-<MODULE>.md` using `templates/migration-plan.md`.
8. **Step 8: Controlled Implementation**
   - Scaffold module metadata (`.info.yml`, `.services.yml`, `.routing.yml`).
   - Implement services, controllers, form classes, and plugins strictly inside `target.path`.
   - Log all file creations and modifications in `logs/file-change-log/`.
9. **Step 9: Automated Testing**
   - Author PHPUnit Unit and Kernel tests targeting core business logic.
10. **Step 10: Behavioral Validation**
    - Execute comparative audit against D7 baseline specifications.
11. **Step 11: Gap Analysis**
    - Document any intentionally altered or deprecated legacy behavior.
12. **Step 12: Sign-Off & Manifest Update**
    - Update component status to `completed` in `state/migration-manifest.yml`.
