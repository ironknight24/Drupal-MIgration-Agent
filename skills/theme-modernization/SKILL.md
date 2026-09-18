---
name: theme-modernization
description: Presentation Layer & Theme Modernization Playbook. Converts PHPTemplate templates into modern Twig templates, creates libraries.yml, and modernizes CSS/JS assets.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Presentation Layer & Theme Modernization Skill

## Overview
This skill provides the operational rules, template conversion patterns, and asset packaging workflows for modernizing legacy Drupal 7 PHPTemplate custom themes into clean, accessible, modern Drupal 10 and Drupal 11 Twig themes.

---

## Technical References
- [PHPTemplate to Modern Twig Conversion Reference](../../references/drupal-10/twig-filters.md)
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)

---

## 3-Tier Modernization Scope & Classification

Evaluate theme assets into three operational tiers:

### Tier 1: Direct Translation
- `.info` regions, metadata, and stylesheets -> `<theme>.info.yml`.
- Standard `.tpl.php` templates -> `.html.twig` templates (refer to `references/drupal-10/twig-filters.md`).
- Pure CSS stylesheets -> modern CSS files with CSS Custom Properties.
- Variable preprocessing -> `.theme` file preprocess functions.

### Tier 2: Migration Requiring Architectural Review
- Complex `template_preprocess_*` functions containing conditional business logic.
- jQuery plugins dependent on legacy D7 libraries (e.g. `$.browser`, `.live()`) -> Refactor to vanilla JavaScript or `Drupal.behaviors` using `core/once`.
- Theme settings forms (`theme-settings.php`) -> `ConfigFormBase` or CMI theme settings schema.
- Dynamic template suggestions -> `hook_theme_suggestions_HOOK_alter()`.

### Tier 3: Redesign Required
- Deprecated grid frameworks (e.g., 960gs, early Zen/Omega grids) -> Modern CSS Grid and Flexbox layouts.
- Raw SQL queries or business logic inside templates -> Must be decoupled into custom module services first.
- Outdated Flash, Silverlight, or legacy polyfills -> Modern HTML5 / SVG implementations.

---

## Modern Theme Scaffolding Checklist

1. **Theme Metadata (`<theme>.info.yml`)**:
   - Declare `name`, `type: theme`, `base theme: false` (or `claro`/`olivero`), `core_version_requirement: ^10 || ^11`, and `regions`.
2. **Asset Libraries (`<theme>.libraries.yml`)**:
   - Organize CSS/JS assets into modular libraries with explicit dependencies (`core/drupal`, `core/once`).
3. **Theme Hooks (`<theme>.theme`)**:
   - Implement `hook_preprocess_HOOK()` functions strictly for presentation formatting.
4. **Twig Templates (`templates/`)**:
   - Ensure zero PHP opening tags (`<?php`) exist in template files.
   - Use `{{ attach_library('theme/library') }}` for asset inclusion.
   - Enforce auto-escaping and pass render attributes via `{{ attributes }}`.
