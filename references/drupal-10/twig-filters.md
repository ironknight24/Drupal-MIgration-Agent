# Drupal 7 PHPTemplate to Modern Twig Conversion Reference

This reference documents the translation of legacy Drupal 7 PHPTemplate patterns, procedural rendering functions, and template files into modern Drupal 10/11 Twig templates.

---

## 1. Template File Naming Conventions

In Drupal 7, template files used the `.tpl.php` extension and underscores. In Drupal 10/11, templates use `.html.twig` and hyphens.

| Drupal 7 Template (`.tpl.php`) | Target Drupal 10/11 Template (`.html.twig`) | Description |
| :--- | :--- | :--- |
| `html.tpl.php` | `html.html.twig` | Overall HTML page shell (`<html>`, `<head>`, `<body>`). |
| `page.tpl.php` | `page.html.twig` | Page content structure, header, footer, regions. |
| `region.tpl.php` | `region.html.twig` | Wrapper for block containers within a region. |
| `block.tpl.php` | `block.html.twig` | Wrapper for individual block plugins. |
| `node.tpl.php` | `node.html.twig` | Base node template. |
| `node--article.tpl.php` | `node--article.html.twig` | Bundle-specific template suggestion. |
| `field.tpl.php` | `field.html.twig` | Individual field render template. |
| `comment.tpl.php` | `comment.html.twig` | Comment wrapper and comment item. |
| `views-view.tpl.php` | `views-view.html.twig` | Views container display template. |

---

## 2. Procedural PHP to Twig Syntax Dictionary

| Drupal 7 PHPTemplate Pattern | Target Drupal 10/11 Twig Equivalent | Purpose / Notes |
| :--- | :--- | :--- |
| `<?php print $title; ?>` | `{{ title }}` | Variable interpolation and output. |
| `<?php print check_plain($var); ?>` | `{{ var }}` | Twig auto-escapes output by default for XSS protection. |
| `<?php print render($content); ?>` | `{{ content }}` | Render arrays are automatically rendered upon printing. |
| `<?php print render($content['field_name']); ?>` | `{{ content.field_name }}` | Field output rendering with formatters. |
| `<?php hide($content['field_name']); ?>` | `{{ content\|without('field_name') }}` | Render content array excluding specific field. |
| `<?php print t('Hello @name', ['@name' => $name]); ?>` | `{% trans %}Hello {{ name }}{% endtrans %}` | String translation block. |
| `<?php print url('node/1'); ?>` | `{{ url('entity.node.canonical', {'node': 1}) }}` | Route URL generation. |
| `<?php print drupal_attributes($attributes); ?>` | `{{ attributes }}` | Render Attribute object (`class="..." id="..."`). |
| `<?php drupal_add_css(...) / drupal_add_js(...) ?>` | `{{ attach_library('my_theme/my_library') }}` | Asset attachment via `libraries.yml`. Direct asset injection in templates is prohibited. |

---

## 3. Control Structures & Conditionals

### Conditionals (`if / elseif / else`)

```html
<!-- Drupal 7 -->
<?php if (!empty($subtitle)): ?>
  <h2 class="subtitle"><?php print $subtitle; ?></h2>
<?php elseif ($is_front): ?>
  <h2 class="welcome">Welcome</h2>
<?php else: ?>
  <div class="default-title">Home</div>
<?php endif; ?>

<!-- Drupal 10/11 Twig -->
{% if subtitle is not empty %}
  <h2 class="subtitle">{{ subtitle }}</h2>
{% elseif is_front %}
  <h2 class="welcome">{{ 'Welcome'|t }}</h2>
{% else %}
  <div class="default-title">{{ 'Home'|t }}</div>
{% endif %}
```

### Iteration (`foreach`)

```html
<!-- Drupal 7 -->
<?php foreach ($items as $delta => $item): ?>
  <li class="<?php print ($delta % 2 == 0) ? 'even' : 'odd'; ?>">
    <?php print render($item); ?>
  </li>
<?php endforeach; ?>

<!-- Drupal 10/11 Twig -->
{% for item in items %}
  <li class="{{ loop.index is even ? 'even' : 'odd' }}">
    {{ item }}
  </li>
{% endfor %}
```

---

## 4. Attributes Manipulation in Modern Twig

Modern Drupal passes attributes as `Drupal\Core\Template\Attribute` objects:

```twig
{# Adding CSS classes dynamically #}
{%
  set classes = [
    'node',
    'node--type-' ~ node.bundle|clean_class,
    view_mode ? 'node--view-mode-' ~ view_mode|clean_class,
  ]
%}

<article{{ attributes.addClass(classes) }}>
  <header>
    {{ title_prefix }}
    {% if label and not page %}
      <h2{{ title_attributes }}>
        <a href="{{ url }}" rel="bookmark">{{ label }}</a>
      </h2>
    {% endif %}
    {{ title_suffix }}
  </header>

  <div{{ content_attributes.addClass('node__content') }}>
    {{ content }}
  </div>
</article>
```

---

## 5. Modern Asset Attachment (`libraries.yml`)

Direct calls to `drupal_add_css()`, `drupal_add_js()`, or `<link>` / `<script>` tags in templates are strictly deprecated.

### Step 1: Declare Library in `<theme_name>.libraries.yml`

```yaml
global-styling:
  version: 1.0
  css:
    theme:
      css/styles.css: {}
      css/components/navigation.css: {}
  js:
    js/navigation.js: {}
  dependencies:
    - core/drupal
    - core/once
```

### Step 2: Attach Library in Template or Preprocess

In Twig template:
```twig
{{ attach_library('custom_theme/global-styling') }}
```

Or in `custom_theme.theme`:
```php
function custom_theme_preprocess_page(array &$variables): void {
  $variables['#attached']['library'][] = 'custom_theme/global-styling';
}
```
