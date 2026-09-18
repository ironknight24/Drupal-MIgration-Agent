---
name: d7-to-d10-mapping
description: Definitive mapping patterns, API conversions, and structural transformations from Drupal 7 to Drupal 10/11.
version: 1.11.0
user-invocable: false
disable-model-invocation: false
allowed-tools: Read, Grep, Find
---

# Drupal 7 to Drupal 10/11 Architectural Mapping Skill

## Overview
This skill provides the architectural mapping rules required to translate Drupal 7 procedural constructs, hooks (core, contrib, custom, alter, entity, form, theme, install/update), persistent variables, configuration forms, runtime state, custom entities, fields, bundles, revisions, translations, forms, Form API elements, AJAX commands, legacy custom PHP classes, constructors, interfaces, traits, and `.inc` files into modern Symfony/Drupal 10 and Drupal 11 object-oriented paradigms, prioritizing Dependency Injection, PSR-4 autoloading, service containers, event subscribers, typed configuration, and testability.

---

## Technical References
For detailed syntax examples and conversion catalogs, consult:
- [Common Migration & Modernization Patterns](../../references/migration-patterns/common-conversions.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](../../references/drupal-7/hooks.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](../../references/drupal-10/plugin-types.md)
- [Drupal 10 Architecture Reference](../../references/drupal-10/architecture.md)
- [Field Type & Data Migration Mapping Reference](../../references/migration-patterns/field-mapping.md)

---

## Core Mapping Rules

### 1. Legacy Custom PHP Class & OOP Modernization
- **PSR-4 Namespacing**: Custom classes declared in root, `includes/`, `lib/`, or `classes/` must be moved into PSR-4 compliant `src/` subdirectories:
  - Domain / Business Logic $\rightarrow$ `Drupal\<module>\Service\<ClassName>` (`src/Service/`)
  - Page / Endpoint Handlers $\rightarrow$ `Drupal\<module>\Controller\<ClassName>` (`src/Controller/`)
  - Form Handlers $\rightarrow$ `Drupal\<module>\Form\<ClassName>` (`src/Form/`)
  - Drush CLI Commands $\rightarrow$ `Drupal\<module>\Drush\Commands\<ClassName>` (`src/Drush/Commands/`)
  - Event Subscribers $\rightarrow$ `Drupal\<module>\EventSubscriber\<ClassName>` (`src/EventSubscriber/`)
  - Access Handlers $\rightarrow$ `Drupal\<module>\Access\<ClassName>` (`src/Access/`)
  - Value / Domain Objects $\rightarrow$ `Drupal\<module>\Model\<ClassName>` (`src/Model/` or `src/ValueObject/`)
- **Autoloading Modernization**: Eliminate manual `require`, `include`, `module_load_include()`, or `.info` `files[]` declarations. Target classes rely exclusively on Composer / Drupal PSR-4 autoloading.

### 2. Constructor Modernization & Dependency Injection
- **Constructor Refactoring**:
  - Legacy PHP4/D7 constructors (`function ClassName(...)`) must be refactored to standard `public function __construct(...)` with explicit parameter typehints and return types.
  - Eliminate global variable fetches inside constructors (`global $user, $conf, $language;` $\rightarrow$ injected `AccountProxyInterface`, `ConfigFactoryInterface`, `LanguageManagerInterface`).
  - Eliminate direct procedural calls inside constructors (`variable_get()` $\rightarrow$ injected `config.factory`, `db_query()` $\rightarrow$ injected `database`).
- **Dependency Injection Rules**:
  - Only inject services genuinely consumed by the resulting class. Avoid service proliferation.
  - For service classes: register arguments in `<module>.services.yml` and inject via constructor.
  - For controllers and form classes: implement `create(ContainerInterface $container)` and pass injected services to the constructor.

### 3. Non-1:1 Transformations (Decomposition & Consolidation)
- **One-to-Many**: A single legacy D7 PHP file, `.inc` file, or monolithic hook implementation (e.g. `hook_menu()`) must be decomposed into dedicated, single-responsibility PSR-4 classes, plugins, and YAML route/link files.
- **Many-to-One**: Multiple legacy procedural helper scripts, hook implementations, or related class shims can be consolidated into a unified modern service class where cohesive.

### 4. hook_menu() Exhaustive Decomposition
In Drupal 7, `hook_menu()` handled page routing, menu items, tabs, contextual links, and form endpoints simultaneously. In modern Drupal, these are decoupled:
- **Routes**: Page callbacks, form routes, delivery callbacks $\rightarrow$ `<module>.routing.yml` pointing to Controller (`_controller`) or Form (`_form`).
- **Controllers & Forms**: Procedural page callbacks $\rightarrow$ `src/Controller/<Name>Controller.php` extending `ControllerBase`; procedural form callbacks $\rightarrow$ `src/Form/<Name>Form.php` extending `FormBase` or `ConfigFormBase`.
- **Access Checkers**: Procedural access callbacks $\rightarrow$ custom access check services in `src/Access/` implementing `AccessCheckInterface` registered in `.services.yml` with `_custom_access` route requirements.
- **Permissions**: Defined in `<module>.permissions.yml` and referenced via `_permission` route requirement.
- **Menu Links**: `MENU_NORMAL_ITEM` $\rightarrow$ `<module>.links.menu.yml`.
- **Local Tasks (Tabs)**: `MENU_LOCAL_TASK` / `MENU_DEFAULT_LOCAL_TASK` $\rightarrow$ `<module>.links.task.yml`.
- **Local Actions**: `MENU_LOCAL_ACTION` $\rightarrow$ `<module>.links.action.yml`.
- **Contextual Links**: `MENU_CONTEXT_PAGE` / `MENU_CONTEXT_INLINE` $\rightarrow$ `<module>.links.contextual.yml`.
- **Parameter Converters & Wildcard Loaders**: `%node`, `%user`, `%custom` loaders $\rightarrow$ ParamConverters or route parameter auto-upcasting.

### 5. Hook Modernization & Event Architecture
- **Custom Hooks (`module_invoke_all`, `module_invoke`)**: Modernized to Symfony Event Dispatcher:
  - Define custom `Event` class extending `Symfony\Contracts\EventDispatcher\Event` in `src/Event/`.
  - Dispatch event via injected `EventDispatcherInterface`.
  - Implement listeners as `EventSubscriberInterface` classes in `src/EventSubscriber/` tagged with `event_subscriber` in `.services.yml`.
- **Lifecycle & Request Hooks (`hook_init`, `hook_exit`, `hook_boot`)**:
  - Map to Symfony Kernel Events (`KernelEvents::REQUEST`, `KernelEvents::RESPONSE`, `KernelEvents::TERMINATE`) in an event subscriber or HTTP middleware.
- **Alter Hooks**:
  - `hook_form_alter()` / `hook_form_FORM_ID_alter()`: Retained in `.module` but must delegate business processing to injected services.
  - `hook_menu_alter()` $\rightarrow$ Route subscriber extending `RouteSubscriberBase`.
  - `hook_views_data_alter()`, `hook_views_query_alter()` $\rightarrow$ Retained in `.views.execution.inc` or Views plugins.
  - `hook_theme_registry_alter()`, `hook_js_alter()`, `hook_css_alter()` $\rightarrow$ Target `.theme` hooks or `hook_page_attachments_alter()`.
- **Subsystem Procedural Hooks**:
  - *Entity Lifecycles (`hook_node_*`, `hook_user_*`, `hook_entity_*`)* $\rightarrow$ Entity hooks in `.module` delegating to entity service / event subscriber, or custom entity class overrides (`preSave()`, `postSave()`).
  - *Blocks (`hook_block_info`, `hook_block_view`, `hook_block_configure`, `hook_block_save`)* $\rightarrow$ Block plugins extending `BlockBase` in `src/Plugin/Block/`.
  - *Access Control (`hook_permission`, `hook_node_access`)* $\rightarrow$ `<module>.permissions.yml`, custom access checkers, or entity access control handlers.
  - *Tokens (`hook_token_info`, `hook_tokens`)* $\rightarrow$ Retained in `.tokens.inc` with modern `BubbleableMetadata` caching.
  - *Mail (`hook_mail`)* $\rightarrow$ Retained in `.module` or modernized via Mail plugins / `plugin.manager.mail`.
  - *Cron (`hook_cron`)* $\rightarrow$ Retained in `.module` delegating to a dedicated cron service or QueueWorker plugin in `src/Plugin/QueueWorker/`.

### 6. Configuration, State, Variable & Settings Modernization
- **Configuration API (CMI)**: Administrator-managed settings (`variable_get` / `variable_set` / `$conf`) map to Configuration Objects (`config/install/<module>.settings.yml`) with typed schema (`config/schema/<module>.schema.yml`). Access via injected `ConfigFactoryInterface` (`$this->configFactory->get('<module>.settings')`).
- **Configuration Forms**: Procedural `system_settings_form()` builders map to `ConfigFormBase` classes (`src/Form/SettingsForm.php`) implementing `getEditableConfigNames()`, `buildForm()`, `validateForm()`, and `submitForm()`.
- **State API**: Runtime, machine-specific flags and counters (timestamps, cron markers, sync counters) map to `StateInterface` (`\Drupal::state()` or injected `state` service).
- **Settings API & Secret Isolation (Rule 10)**: Secrets, passwords, private keys, API credentials, and environment overrides map to `Settings::get(...)`, `settings.php` overrides, or Key module. **NEVER** commit credentials into CMI YAML files.
- **KeyValue API**: Dedicated key-value collections map to `\Drupal::keyValue()` or `keyvalue.expirable`.
- **14 Migration Strategies Applied**: Explicitly choose from `DIRECT_CONFIG_MIGRATION`, `TRANSFORMED_CONFIG_MIGRATION`, `CONFIG_ENTITY_MIGRATION`, `STATE_MIGRATION`, `SETTINGS_MIGRATION`, `ENVIRONMENT_MIGRATION`, `KEY_VALUE_MIGRATION`, `CONTENT_MIGRATION`, `CACHE_REBUILD`, `CUSTOM_MIGRATION`, `REPLACED`, `OBSOLETE`, `HUMAN_DECISION_REQUIRED`, `UNVERIFIED`.

### 7. Entities, Fields, Revisions & Translations Modernization
- **Content Entity vs Config Entity Architectural Distinction**:
  - *Content Entity (`@ContentEntityType`)*: Domain content and fieldable business objects with database storage (`src/Entity/<EntityName>.php`), extending `ContentEntityBase` or `RevisionableContentEntityBase` and implementing `<EntityName>Interface`.
  - *Config Entity (`@ConfigEntityType`)*: Administrative, exportable entities (e.g. custom bundle types) map to `@ConfigEntityType` in `src/Entity/` extending `ConfigEntityBase` with CMI schema backing.
- **Base Fields vs Config Fields**:
  - Core entity attributes (`id`, `uuid`, `vid`, `langcode`, `title`, `created`, `changed`, `status`, `uid`) defined via `public static function baseFieldDefinitions(EntityTypeInterface $entity_type)` declaring field types, cardinality, requiredness, and constraints.
  - Dynamic / bundle-attachable fields mapped to CMI field storage (`field.storage.<entity>.<field>.yml`) and field instance (`field.field.<entity>.<bundle>.<field>.yml`) YAML definitions.
- **Entity References & Target Bundles**: Procedural `entityreference` / `taxonomy_term_reference` fields modernize to `entity_reference` base fields or config fields with typed target entity references (`target_type: node`, `target_bundles: [article]`).
- **Revisionable & Translatable Entities**:
  - Implement `RevisionableInterface` and `TranslatableInterface` on the entity class.
  - Enable Content Translation, declare `revision_table`, `data_table`, and `translatable: true` in the entity definition.
- **Entity Access Control Handler**: Custom entity access callbacks modernize to dedicated handlers (`src/<EntityName>AccessControlHandler.php`) extending `EntityAccessControlHandler`.
- **Entity View Builder & View Modes**: Procedural `entity_view()` builders modernize to `EntityViewBuilder` classes with configured view mode displays (`core.entity_view_display.*.yml`).
- **Entity Query & Storage Modernization**: Procedural `EntityFieldQuery` and direct entity SQL queries modernize to modern `EntityQuery` via `EntityStorageInterface` (`$entity_type_manager->getStorage('<entity>')->getQuery()`) or `\Drupal::entityQuery('<entity>')`.


### 8. Custom Database Table & Repository Abstraction
- **Core Entity Queries**: Direct `db_query()` targeting core tables (`{node}`, `{users}`, `{taxonomy_term_data}`, `{file_managed}`) MUST be replaced by Entity Queries or Entity Storage via `EntityTypeManagerInterface`.
- **Custom Database Table Target Architecture Mapping**:
  - *Content Entity (`src/Entity/`)*: Appropriate when the table represents domain content, user submissions, or business objects with fieldable requirements, revisioning, or access control.
  - *Config Entity / Config API (`config.factory`)*: Appropriate when table stores site/module configuration, settings, or administrative options.
  - *State API (`\Drupal::state()`)*: Appropriate for transient, environment-specific timestamps, counters, or flags.
  - *KeyValue API (`keyvalue` / `keyvalue.expirable`)*: Appropriate for key-value collections, tokens, or temporary storage.
  - *Custom Repository Service (`src/Repository/`)*: Appropriate when non-entity relational data requires high-performance direct SQL access via injected `\Drupal\Core\Database\Connection`.
  - *Queue Storage (`@queue`)*: Appropriate when table stores asynchronous work payloads.
- **Database API & Query Builder Modernization**:
  - Procedural `db_query()`, `db_query_range()`, `db_select()` $\rightarrow$ Injected `Connection` service `$connection->query()`, `$connection->select()`, or Repository query methods.
  - Procedural `db_insert()`, `db_update()`, `db_delete()`, `db_merge()` $\rightarrow$ `$connection->insert()`, `$connection->update()`, `$connection->delete()`, `$connection->merge()`.
  - Transaction Modernization: Procedural `db_transaction()` $\rightarrow$ `$transaction = $connection->startTransaction()` with comprehensive `try { ... } catch (\Exception $e) { $transaction->rollBack(); ... }` error handling.
  - SQL Safety & Injection Hardening: Eliminate string concatenation in SQL queries; enforce named parameter arrays (`[':id' => $id]`). Dynamic SQL where query structure or tables cannot be verified statically must be marked `HUMAN_DECISION_REQUIRED` or `UNVERIFIED`.
- **Serialized Data Modernization**:
  - Migrate legacy PHP serialized strings (`serialize()` / `unserialize()`) to modern structured formats (JSON, typed entity properties, or typed arrays).
  - Explicitly flag serialized PHP objects requiring custom migration process plugins.

### 9. Forms, AJAX & Form API Modernization
- **Form Class Hierarchy Mapping**:
  - *Standard Forms*: Procedural `drupal_get_form()` builders map to OOP form classes extending `FormBase` (`src/Form/<FormName>.php`), implementing `getFormId()`, `buildForm()`, `validateForm()`, and `submitForm()`.
  - *Configuration Settings Forms*: `system_settings_form()` builders map to classes extending `ConfigFormBase` (`src/Form/<FormName>SettingsForm.php`) implementing `getEditableConfigNames()`.
  - *Confirmation Forms*: `confirm_form()` builders map to classes extending `ConfirmFormBase` (`src/Form/<FormName>ConfirmForm.php`) implementing `getQuestion()`, `getCancelUrl()`, and `getConfirmText()`.
  - *Entity Forms*: Procedural entity edit/create forms map to `ContentEntityForm` or `ConfigEntityForm` registered in the entity annotation `handlers['form']`.
  - *Plugin Forms*: Reusable plugin configuration sub-forms map to classes implementing `PluginFormInterface` or extending `PluginFormBase`.
- **Form API Element & Property Modernization**:
  - Procedural element properties (`#type`, `#title`, `#description`, `#required`, `#default_value`, `#options`, `#tree`, `#states`) map directly to Form API render arrays in `buildForm(array $form, FormStateInterface $form_state)`.
  - `#attached`: Assets modernize to library attachments (`$form['#attached']['library'][] = '<module>/<library_name>'`) defined in `<module>.libraries.yml`.
  - File Elements: `#type => 'file'` and `file_save_upload()` modernize to `#type => 'managed_file'` with `#upload_validators` and injected `EntityTypeManagerInterface` file storage.
- **Validation & Submission Modernization**:
  - Validation: Procedural `form_set_error($name, $message)` modernizes to `$form_state->setErrorByName($name, $message)` in `validateForm()`.
  - Submission: Submit callbacks modernize to `submitForm()`, using `$form_state->getValue()`, `$form_state->setRedirect()`, `$form_state->setRebuild()`, and injected services for database/entity/state mutations.
- **Form Alteration Modernization**:
  - `hook_form_alter()` and `hook_form_FORM_ID_alter()` retained in `<module>.module` for simple alterations or converted to Symfony Event Subscribers for complex, decoupled form alter pipelines.
- **AJAX Behavior & Command Modernization**:
  - `#ajax['callback']`: Modernizes to public methods on the form class or controller returning `AjaxResponse` objects.
  - AJAX Commands: Procedural `ajax_command_*()` functions modernize to OOP command classes implementing `CommandInterface`:
    - `ajax_command_replace()` $\rightarrow$ `new ReplaceCommand($selector, $content)`
    - `ajax_command_html()` $\rightarrow$ `new HtmlCommand($selector, $content)`
    - `ajax_command_append()` $\rightarrow$ `new AppendCommand($selector, $content)`
    - `ajax_command_invoke()` $\rightarrow$ `new InvokeCommand($selector, $method, $args)`
    - `ajax_command_settings()` $\rightarrow$ `new SettingsCommand($settings, $merge)`
    - `drupal_set_message()` in AJAX $\rightarrow$ `new MessageCommand($message)`
- **Multistep & Wizard Modernization**:
  - Multi-step state persisted via `FormStateInterface` storage (`$form_state->set('step', $step)`, `$form_state->get('step')`).
  - Step transitions trigger `$form_state->setRebuild(TRUE)` to re-invoke `buildForm()` with the updated step state.

## 10. Frontend JavaScript, CSS, `*.libraries.yml`, `once()`, and `drupalSettings` Modernization
- **Modern Library Registration (`*.libraries.yml`)**:
  - All direct `drupal_add_js()` / `drupal_add_css()` calls and `.info` `scripts[]` / `stylesheets[]` declarations are replaced by structured `<module>.libraries.yml` definitions.
  - Stylesheets categorized by SMACSS: `css: { base: { ... }, layout: { ... }, component: { ... }, state: { ... }, theme: { ... } }`.
  - Core JavaScript dependencies explicitly declared (`dependencies: [core/drupal, core/drupalSettings, core/once, core/jquery]`).
- **`Drupal.behaviors` and `once()` Pattern**:
  - Legacy `jQuery.once()` is modernized to `@drupal/once` / `once()` iterating natively with `forEach()`:
    ```javascript
    (function (Drupal, once, drupalSettings) {
      'use strict';
      Drupal.behaviors.myModuleBehavior = {
        attach: function (context, settings) {
          once('my-behavior-key', '.my-selector', context).forEach(function (element) {
            // Behavioral attachment logic
          });
        },
        detach: function (context, settings, trigger) {
          if (trigger === 'unload') {
            // Cleanup logic
          }
        }
      };
    })(Drupal, once, drupalSettings);
    ```
- **`Drupal.settings` $\rightarrow$ `drupalSettings` Mapping**:
  - PHP runtime data passed via render array attachments: `$attachments['#attached']['drupalSettings']['myModule']['key'] = $value`.
  - Client-side scripts access data directly via the passed `drupalSettings` parameter in the behavior closure.
- **Client-Side AJAX Commands (`Drupal.AjaxCommands`)**:
  - Custom client-side AJAX command handlers modernize to prototype extensions:
    ```javascript
    (function (Drupal) {
      'use strict';
      Drupal.AjaxCommands.prototype.myCustomCommand = function (ajax, response, status) {
        // Custom DOM reaction logic
      };
    })(Drupal);
    ```
- **Attachment APIs**:
  - Page-level attachments modernized via `hook_page_attachments(array &$attachments)`.
  - Element-level attachments modernized via `#attached['library'][] = '<module>/<library_name>'`.
- **External & Third-Party Library Declarations**:
  - CDN and third-party external assets declared in `<module>.libraries.yml` with `type: external`:
    ```yaml
    external-cdn-lib:
      remote: https://cdn.example.com/lib
      version: 1.0.0
      license:
        name: MIT
        url: https://cdn.example.com/license
        gpl-compatible: true
      js:
        https://cdn.example.com/lib.min.js: { type: external, minified: true }
      css:
        component:
          https://cdn.example.com/lib.min.css: { type: external, minified: true }
    ```

## 11. Views, Displays, Custom Plugins & Query Re-Engineering
- **Views Configuration Modernization (`views.view.*.yml`)**:
  - Exported D7 Views and `hook_views_default_views()` are converted to modern Drupal 10/11 CMI configuration files located in `config/install/views.view.<view_id>.yml`.
  - Displays are declared under `display:` mapping keys (`default`, `page_1`, `block_1`, `rest_export_1`, `feed_1`, `attachment_1`, `embed_1`).
- **Custom Views Plugin Architecture**:
  - Legacy `views_handler_*` and `views_plugin_*` classes are modernized into PSR-4 annotated plugin classes under `src/Plugin/views/`:
    - Field Handlers $\rightarrow$ `@ViewsField` (`src/Plugin/views/field/`) extending `FieldPluginBase`.
    - Filter Handlers $\rightarrow$ `@ViewsFilter` (`src/Plugin/views/filter/`) extending `FilterPluginBase`.
    - Contextual Filter / Argument Handlers $\rightarrow$ `@ViewsArgument` (`src/Plugin/views/argument/`) extending `ArgumentPluginBase`.
    - Sort Handlers $\rightarrow$ `@ViewsSort` (`src/Plugin/views/sort/`) extending `SortPluginBase`.
    - Relationship Handlers $\rightarrow$ `@ViewsRelationship` (`src/Plugin/views/relationship/`) extending `RelationshipPluginBase`.
    - Area Handlers $\rightarrow$ `@ViewsArea` (`src/Plugin/views/area/`) extending `AreaPluginBase`.
    - Pager Plugins $\rightarrow$ `@ViewsPager` (`src/Plugin/views/pager/`) extending `PagerPluginBase`.
    - Access Plugins $\rightarrow$ `@ViewsAccess` (`src/Plugin/views/access/`) extending `AccessPluginBase`.
    - Query Plugins $\rightarrow$ `@ViewsQuery` (`src/Plugin/views/query/`) extending `QueryPluginBase`.
    - Style Plugins $\rightarrow$ `@ViewsStyle` (`src/Plugin/views/style/`) extending `StylePluginBase`.
    - Row Plugins $\rightarrow$ `@ViewsRow` (`src/Plugin/views/row/`) extending `RowPluginBase`.
    - Display Plugins $\rightarrow$ `@ViewsDisplay` (`src/Plugin/views/display/`) extending `DisplayPluginBase`.
  - Custom Views plugins implement `ContainerFactoryPluginInterface` implementing `create(ContainerInterface $container, array $configuration, $plugin_id, $plugin_definition)` for typehinted constructor dependency injection.
- **`hook_views_data()` & `hook_views_data_alter()`**:
  - Implemented in `<module>.views.inc` providing table metadata, joins, and mapping schema columns to plugin IDs.
- **`hook_views_query_alter()` Modernization**:
  - Query alterations operate on `\Drupal\views\Plugin\views\query\Sql` instances, utilizing `$query->addWhere()`, `$query->addTable()`, `$query->addField()`, and `$query->addWhereExpression()`.
- **Cache Metadata Integration**:
  - Views caching utilizes modern cache tags (`$view->element['#cache']['tags']`), cache contexts (`$view->element['#cache']['contexts']`), and cache max-age.
- **Programmatic Dispatches**:
  - `views_get_view($name)` $\rightarrow$ `\Drupal\views\Views::getView($name)`
  - `views_embed_view($name, $display_id, ...$args)` $\rightarrow$ `views_embed_view($name, $display_id, ...$args)`

## 12. Themes, Templates, Preprocess & Theme Layer Modernization
- **Theme Metadata & Declaration (`<theme>.info.yml`)**:
  - Converts D7 `<theme>.info` into modern YAML format:
    ```yaml
    name: 'Custom Corporate'
    type: theme
    description: 'Custom responsive corporate theme'
    core_version_requirement: ^10 || ^11
    base theme: olivero # or claro, starterkit, false
    libraries:
      - custom_corp/global_styling
    regions:
      header: 'Header'
      primary_menu: 'Primary menu'
      content: 'Content'
      sidebar_first: 'Sidebar first'
      footer: 'Footer'
    ```
- **PHPTemplate (`.tpl.php`) to Modern Twig (`.html.twig`) Conversion**:
  - All PHP tags (`<?php ... ?>`) are eliminated and converted to Twig expressions:
    - `<?php print $title; ?>` $\rightarrow$ `{{ title }}`
    - `<?php print render($page['content']); ?>` $\rightarrow$ `{{ page.content }}`
    - `<?php print render($content['field_image']); ?>` $\rightarrow$ `{{ content.field_image }}`
    - `<?php if ($logged_in): ?>` $\rightarrow$ `{% if logged_in %}`
    - `<?php foreach ($items as $item): ?>` $\rightarrow$ `{% for item in items %}`
    - `<?php print $classes; ?>` $\rightarrow$ `{{ attributes.addClass(classes) }}` or `{{ node.bundle|clean_class }}`
    - `<?php print $attributes; ?>` $\rightarrow$ `{{ attributes }}`
    - `<?php print t('Read more'); ?>` $\rightarrow$ `{{ 'Read more'|t }}`
    - `views-view.tpl.php` $\rightarrow$ `views-view.html.twig` (Views presentation override)
- **Theme Preprocess Modernization (`<theme>.theme`)**:
  - Preprocess functions in `template.php` are refactored into `<theme>.theme`:
    ```php
    /**
     * Implements hook_preprocess_HOOK() for node templates.
     */
    function custom_corp_preprocess_node(array &$variables): void {
      $node = $variables['node'] ?? null;
      if ($node instanceof \Drupal\node\NodeInterface) {
        $variables['publication_date'] = \Drupal::service('date.formatter')->format($node->getCreatedTime(), 'short');
      }
    }
    ```
- **Template Suggestions (`hook_theme_suggestions_HOOK_alter()`)**:
  - Replaces legacy `$variables['theme_hook_suggestions']` with structured suggestion hooks:
    ```php
    /**
     * Implements hook_theme_suggestions_HOOK_alter() for page templates.
     */
    function custom_corp_theme_suggestions_page_alter(array &$suggestions, array $variables): void {
      if (\Drupal::service('path.matcher')->isFrontPage()) {
        $suggestions[] = 'page__front';
      }
    }
    ```
- **Theme Functions to Twig Templates / Render Elements**:
  - Procedural `theme_*()` functions generating markup are rewritten into dedicated `.html.twig` templates or custom render elements (`#type`).
- **Theme Settings Modernization**:
  - `theme-settings.php` forms are migrated to modern CMI configuration schemas (`config/schema/<theme>.schema.yml`) and default settings (`config/install/<theme>.settings.yml`).

## 13. Dynamic, Runtime & Data-Driven Pattern Modernization (Step 21)
- **Variable Functions & Callables $\rightarrow$ Plugin Architecture / Tagged Services**:
  - Legacy `$func = $type . '_handler'; $func($context);` is modernized to a typed Plugin Manager:
    ```php
    namespace Drupal\my_module\Plugin;

    use Drupal\Core\Plugin\DefaultPluginManager;
    use Drupal\Core\Cache\CacheBackendInterface;
    use Drupal\Core\Extension\ModuleHandlerInterface;

    class HandlerPluginManager extends DefaultPluginManager {
      public function __construct(\Traversable $namespaces, CacheBackendInterface $cache_backend, ModuleHandlerInterface $module_handler) {
        parent::__construct('Plugin/Handler', $namespaces, $module_handler, 'Drupal\my_module\Plugin\HandlerInterface', 'Drupal\my_module\Annotation\Handler');
        $this->alterInfo('my_module_handler_info');
        $this->setCacheBackend($cache_backend, 'my_module_handler_plugins');
      }
    }
    ```
- **Dynamic Instantiation $\rightarrow$ Service Factory / Service Container**:
  - Legacy `new $class_name()` is modernized to Container injection or a dedicated factory service (`src/Service/HandlerFactory.php`).
- **Dynamic Hooks $\rightarrow$ Event Dispatcher / Custom Plugin Alter**:
  - Legacy `module_invoke_all($dynamic_event, ...)` is modernized to Symfony Event Dispatcher with typed Event classes (`src/Event/<EventName>Event.php`).
- **Dynamic SQL & Variable Tables $\rightarrow$ Query Builder / Entity Queries**:
  - Legacy `db_query("SELECT * FROM {" . $table . "} ...")` is modernized to `\Drupal::database()->select($table)` with parameterized conditions or `\Drupal::entityTypeManager()->getStorage($entity_type)->getQuery()`.
- **Serialized Data Payloads $\rightarrow$ Typed Configuration / JSON Field Storage**:
  - Legacy `serialize()` payloads stored in databases are normalized into structured columns or typed JSON schema fields.
- **Dynamic Include Paths $\rightarrow$ PSR-4 Autoloading / Plugin Discovery**:
  - Manual include loops (`module_load_include()`) are eliminated in favor of Composer PSR-4 class loading and Drupal plugin discovery mechanisms.

## 14. External Integrations, APIs, Web Services & Third-Party Systems Modernization (Step 22)
- **Procedural HTTP Calls (`drupal_http_request()`, cURL) $\rightarrow$ Guzzle `http_client` & Gateway Services**:
  - Legacy `drupal_http_request($url, $options)` is modernized to an injectable Gateway Service (`src/Service/<System>Client.php`) utilizing `\GuzzleHttp\ClientInterface` via dependency injection:
    ```php
    namespace Drupal\my_module\Service;

    use GuzzleHttp\ClientInterface;
    use Drupal\Core\Logger\LoggerChannelFactoryInterface;
    use Drupal\key\KeyRepositoryInterface;

    class ExternalApiClient {
      public function __construct(
        protected ClientInterface $httpClient,
        protected LoggerChannelFactoryInterface $loggerFactory,
        protected KeyRepositoryInterface $keyRepository,
      ) {}

      public function postPayload(string $endpoint, array $data): array {
        $apiKey = $this->keyRepository->getKey('my_api_key')?->getKeyValue();
        $response = $this->httpClient->post($endpoint, [
          'headers' => ['Authorization' => 'Bearer ' . $apiKey, 'Accept' => 'application/json'],
          'json' => $data,
          'timeout' => 30,
        ]);
        return json_decode((string) $response->getBody(), TRUE) ?? [];
      }
    }
    ```
- **Inbound Webhook Callbacks $\rightarrow$ Symfony Webhook Controller**:
  - Legacy `hook_menu()` callbacks handling webhooks or payment IPNs are modernized to Symfony Controller classes (`src/Controller/WebhookController.php`) with cryptographic HMAC signature verification and `JsonResponse`.
- **Inbound REST/JSON Endpoints $\rightarrow$ REST Resource Plugins / JSON:API**:
  - Legacy custom endpoint routers are migrated to `@RestResource` plugins (`src/Plugin/rest/resource/<Resource>.php`) or core JSON:API resources.
- **SOAP & XML-RPC $\rightarrow$ Modern Typed Service Wrappers**:
  - Legacy `SoapClient` and `xmlrpc()` calls are refactored into typed PHP 8.1+ SOAP service clients or modernized to REST/JSON gateway services.
- **Secret & API Key Handling $\rightarrow$ Drupal Key Module / Environment Variables**:
  - Legacy hardcoded keys or `variable_get()` secrets are migrated to Key module integrations (`key` module) or `getenv()` with `settings.php` overrides (Rule 10: zero secrets in CMI).
- **Remote Storage & SFTP/FTP $\rightarrow$ Flysystem Stream Wrappers**:
  - Legacy `ftp_*()` and `ssh2_sftp()` calls are modernized to Flysystem stream wrappers (`@FlysystemStreamWrapper`).
- **External CLI Binaries $\rightarrow$ Symfony Process Component**:
  - Legacy `exec()` / `shell_exec()` calls are modernized to `Symfony\Component\Process\Process` with strict argument escaping.
- **Asynchronous External Operations $\rightarrow$ Drupal Queue API (`@QueueWorker`)**:
  - Heavy external API syncs or batch requests are refactored into Queue Worker plugins (`src/Plugin/QueueWorker/<Worker>.php`) for non-blocking execution.
