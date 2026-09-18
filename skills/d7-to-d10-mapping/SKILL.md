---
name: d7-to-d10-mapping
description: Behavioral and architectural mapping rules for converting procedural Drupal 7 APIs, hooks, variables, custom entities, fields, revisions, translations, forms, AJAX interactions, and legacy custom PHP classes into modern Drupal 10/11 object-oriented patterns.
version: 1.5.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep
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
