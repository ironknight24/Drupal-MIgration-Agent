---
name: theme-modernization
description: Presentation Layer & Theme Modernization Playbook. Converts PHPTemplate templates into modern Twig templates, creates libraries.yml, and modernizes CSS/JS assets.
version: 1.1.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Presentation Layer & Theme Modernization Skill

## Overview
This skill provides the authoritative operational rules, template conversion patterns, and asset packaging workflows for modernizing legacy Drupal 7 PHPTemplate custom themes into clean, accessible, modern Drupal 10 and Drupal 11 Twig themes.

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
- Pure CSS stylesheets -> modern CSS files with CSS Custom Properties and SMACSS categories.
- Variable preprocessing -> `.theme` file preprocess functions.

### Tier 2: Migration Requiring Architectural Review
- Complex `template_preprocess_*` functions containing conditional business logic.
- jQuery plugins dependent on legacy D7 libraries (e.g. `$.browser`, `.live()`) -> Refactor to vanilla JavaScript or `Drupal.behaviors` using `@drupal/once`.
- Theme settings forms (`theme-settings.php`) -> `ConfigFormBase` or CMI theme settings schema (`config/schema/<theme>.schema.yml`).
- Dynamic template suggestions -> `hook_theme_suggestions_HOOK_alter()`.

### Tier 3: Redesign Required
- Deprecated grid frameworks (e.g., 960gs, early Zen/Omega grids) -> Modern CSS Grid and Flexbox layouts.
- Raw SQL queries or business logic inside templates -> Must be decoupled into custom module services first.
- Outdated Flash, Silverlight, or legacy polyfills -> Modern HTML5 / SVG implementations.

---

## Modern Theme Scaffolding Checklist

1. **Theme Metadata (`<theme>.info.yml`)**:
   - Declare `name`, `type: theme`, `base theme: false` (or `claro`/`olivero`/starterkit), `core_version_requirement: ^10 || ^11`, `libraries`, and `regions`.
2. **Asset Libraries (`<theme>.libraries.yml`)**:
   - Organize CSS/JS assets into modular libraries with explicit dependencies (`core/drupal`, `core/once`, `core/drupalSettings`).
3. **Theme Hooks & Preprocess (`<theme>.theme`)**:
   - Implement `hook_preprocess_HOOK()` and `hook_theme_suggestions_HOOK_alter()` functions strictly for presentation formatting.
4. **Twig Templates (`templates/`)**:
   - Organize templates into structured subdirectories:
     - `templates/layout/`: `page.html.twig`, `region.html.twig`, `html.html.twig`
     - `templates/content/`: `node.html.twig`, `node--article.html.twig`, `comment.html.twig`
     - `templates/field/`: `field.html.twig`, `field--<field_name>.html.twig`
     - `templates/views/`: `views-view.html.twig`, `views-view-unformatted.html.twig`, `views-view-fields.html.twig`
     - `templates/form/`: `form-element.html.twig`, `input.html.twig`, `select.html.twig`
     - `templates/block/`: `block.html.twig`, `block--system-branding-block.html.twig`
     - `templates/navigation/`: `menu.html.twig`, `breadcrumb.html.twig`, `pager.html.twig`
   - Ensure zero PHP opening tags (`<?php`) exist in template files.
   - Use `{{ attach_library('theme/library') }}` for asset inclusion.
   - Enforce auto-escaping and pass render attributes via `{{ attributes }}`.
5. **Single Directory Components (SDC) (`components/`)**:
   - For Drupal 10.3+ and Drupal 11 targets, encapsulate self-contained UI widgets under `components/<component_name>/` with `<component_name>.component.yml`, `<component_name>.twig`, and `<component_name>.css`.
6. **Accessibility & Semantic HTML5**:
   - Enforce semantic landmark tags (`<header>`, `<nav role="navigation">`, `<main id="main-content">`, `<aside role="complementary">`, `<footer>`) and ARIA labels.
7. **Cache Metadata & Context Bubbling**:
   - Attach `#cache` tags, contexts, and max-age within preprocess functions and template render arrays to ensure dynamic caching.

## PHPTemplate to Twig Conversion Rules

| D7 PHPTemplate (`.tpl.php`) | D10/D11 Modern Twig (`.html.twig`) | Description |
|:---|:---|:---|
| `<?php print $title; ?>` | `{{ title }}` | Variable printing with automatic HTML escaping |
| `<?php print render($content); ?>` | `{{ content }}` | Render array output |
| `<?php print render($content['field_name']); ?>` | `{{ content.field_name }}` | Child element rendering |
| `<?php if ($logged_in): ?> ... <?php endif; ?>` | `{% if logged_in %} ... {% endif %}` | Conditional control structure |
| `<?php foreach ($items as $item): ?> ... <?php endforeach; ?>` | `{% for item in items %} ... {% endfor %}` | Loop iteration |
| `<?php print $classes; ?>` | `{{ attributes.addClass(classes) }}` | Semantic CSS class rendering |
| `<?php print $attributes; ?>` | `{{ attributes }}` | Core attribute object rendering |
| `<?php print t('Hello @name', array('@name' => $name)); ?>` | `{{ 'Hello @name'\|t({'@name': name}) }}` | Translatable string with placeholders |
| `<?php print check_plain($text); ?>` | `{{ text }}` | Native Twig auto-escaping |
| `<?php print url('node/' . $node->nid); ?>` | `{{ path('entity.node.canonical', {'node': node.id}) }}` | Route path generation |
| `<?php print $content_attributes; ?>` | `{{ content_attributes }}` | Content attribute container |

---

## 30 Theme Target Architecture Classifications

1. `THEME`: Root modern theme package declaration.
2. `BASE_THEME`: Parent theme in inheritance chain providing base templates and styling.
3. `SUB_THEME`: Child theme extending base theme with overrides and customizations.
4. `THEME_INFO`: Theme metadata declaration (`<theme>.info.yml`).
5. `THEME_REGION`: Layout region definition in `info.yml` and `page.html.twig`.
6. `TWIG_TEMPLATE`: Standard Twig presentation template (`templates/**/*.html.twig`).
7. `TWIG_TEMPLATE_OVERRIDE`: Twig template overriding core, module, or base theme template.
8. `THEME_HOOK`: Registered presentation theme hook definition.
9. `CUSTOM_THEME_HOOK`: Module- or theme-defined custom theme hook implementation.
10. `PREPROCESS_HOOK`: Preprocess function (`<theme>_preprocess_HOOK`) in `<theme>.theme`.
11. `PROCESS_HOOK`: Process function refactored to modern preprocess implementation.
12. `THEME_SUGGESTION`: Static template suggestion based on route, bundle, or view mode.
13. `DYNAMIC_THEME_SUGGESTION`: Runtime-calculated template suggestion requiring alter hooks.
14. `THEME_FUNCTION_REPLACEMENT`: Procedural `theme_*()` function converted to Twig or render element.
15. `RENDER_ARRAY`: Structured renderable array produced by theme functions or preprocess.
16. `RENDER_ELEMENT`: Plugin-based render element (`#type`).
17. `THEME_SERVICE`: Injected helper service supporting complex presentation calculations.
18. `THEME_CONFIGURATION`: CMI theme configuration (`config/install/<theme>.settings.yml`).
19. `THEME_LIBRARY`: Modular asset library in `<theme>.libraries.yml`.
20. `TEMPLATE_VARIABLE_PROVIDER`: Preprocess hook computing presentation variables.
21. `ENTITY_TEMPLATE`: Entity-specific presentation template (`node.html.twig`, `user.html.twig`).
22. `FIELD_TEMPLATE`: Field-level template (`field.html.twig`, `field--<field_name>.html.twig`).
23. `VIEW_TEMPLATE`: Views presentation template override (`views-view.html.twig`).
24. `FORM_TEMPLATE`: Form-level wrapper or element template.
25. `BLOCK_TEMPLATE`: Block wrapper template (`block.html.twig`).
26. `MENU_TEMPLATE`: Menu navigation template (`menu.html.twig`).
27. `PAGE_TEMPLATE`: Global page layout template (`page.html.twig`).
28. `OBSOLETE`: Deprecated theme artifact with no modern equivalent.
29. `HUMAN_DECISION_REQUIRED`: Ambiguous presentation logic or dynamic suggestions flagged for human review.
30. `UNVERIFIED`: Presentation behavior dependent on unavailable runtime state.

---

## 22 Standardized Theme Migration Strategies

1. `DIRECT_TWIG_MIGRATION`: Direct conversion of `.tpl.php` to `.html.twig` without logic refactoring.
2. `TWIG_WITH_PREPROCESS`: Twig conversion with extracted business/data logic moved to `.theme` preprocess functions.
3. `THEME_FUNCTION_TO_TWIG`: Procedural `theme_*()` converted to a standalone Twig template.
4. `THEME_FUNCTION_TO_RENDER_ARRAY`: Procedural `theme_*()` converted to structured render arrays.
5. `THEME_FUNCTION_TO_SERVICE`: Complex theme function extracted to an injectable service.
6. `PREPROCESS_REFACTOR`: Preprocess function modernized with typehinted `$variables` array access and bubbleable metadata.
7. `PROCESS_TO_PREPROCESS`: Legacy D7 process hook refactored into a modern preprocess hook.
8. `TEMPLATE_SUGGESTION_REFACTOR`: Modernized to `hook_theme_suggestions_HOOK_alter()`.
9. `DYNAMIC_SUGGESTION_HUMAN_REVIEW`: Non-deterministic runtime suggestions escalated for architecture review.
10. `REGION_TO_THEME_REGION`: D7 region definitions mapped to D10/D11 theme regions.
11. `BASE_THEME_REFACTOR`: Base theme declaration updated to Olivero, Claro, or custom starterkit.
12. `SUB_THEME_MIGRATION`: Sub-theme configuration and inheritance tree modernized.
13. `THEME_SETTINGS_TO_CONFIG`: Theme settings form converted to typed CMI configuration and schema.
14. `LIBRARY_HANDOFF_TO_STEP18`: Theme asset files packaged into `<theme>.libraries.yml` per Step 18 standards.
15. `ENTITY_TEMPLATE_REFACTOR`: Entity template modernized preserving Step 16 field structures.
16. `FIELD_TEMPLATE_REFACTOR`: Field template modernized with semantic attributes.
17. `SECURITY_ESCAPING_REFACTOR`: Unsafe print statements refactored to Twig auto-escaping and sanitized filters.
18. `CACHE_METADATA_REFACTOR`: Dynamic template logic annotated with cache tags, contexts, and max-age.
19. `REPLACED`: Legacy theme component replaced by modern Drupal core or contrib theme.
20. `OBSOLETE`: Deprecated theme helper, polyfill, or grid framework removed.
21. `EXCLUDED_WITH_REASON`: Explicitly excluded with documented rationale.
22. `HUMAN_DECISION_REQUIRED`: Complex template logic or custom design system refactor requiring human approval.
