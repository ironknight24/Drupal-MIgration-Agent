# Drupal 10 & 11-Ready Object-Oriented Architecture Reference

## 1. Service Container & Dependency Injection
Drupal 10 is built on Symfony components. Procedural functions are replaced by services managed by the container.
- Services declared in `<module>.services.yml`:
  ```yaml
  services:
    my_module.business_service:
      class: Drupal\my_module\Service\BusinessService
      arguments: ['@database', '@entity_type.manager', '@logger.channel.my_module']
  ```
- **Constructor Injection** is mandatory for all custom classes:
  ```php
  namespace Drupal\my_module\Service;

  use Drupal\Core\Database\Connection;
  use Drupal\Core\Entity\EntityTypeManagerInterface;
  use Psr\Log\LoggerInterface;

  class BusinessService {
    public function __construct(
      protected Connection $database,
      protected EntityTypeManagerInterface $entityTypeManager,
      protected LoggerInterface $logger
    ) {}
  }
  ```

## 2. Configuration Management Interface (CMI)
Persistent configuration is stored as YAML files under `config/sync/` and manipulated via typed objects:
- Read-only config: `$config = $this->configFactory->get('my_module.settings');`
- Mutable config: `$config = $this->configFactory->getEditable('my_module.settings');`
- Schema defined in `config/schema/<module>.schema.yml`.

## 3. Entity API & EntityQuery
- Entity Type Manager: `$storage = $this->entityTypeManager->getStorage('node');`
- Loading: `$node = $storage->load($nid);` / `$nodes = $storage->loadMultiple($nids);`
- Saving/Deleting: `$node->save();` / `$node->delete();`
- Entity Queries:
  ```php
  $nids = $this->entityTypeManager->getStorage('node')->getQuery()
    ->accessCheck(TRUE)
    ->condition('status', 1)
    ->condition('type', 'article')
    ->execute();
  ```
- Field Access: `$value = $node->get('field_custom')->value;` / `$target_id = $node->get('field_ref')->target_id;`

## 4. Routing & Controllers
- Routes defined in `<module>.routing.yml`:
  ```yaml
  my_module.admin_settings:
    path: '/admin/config/system/custom'
    defaults:
      _form: '\Drupal\my_module\Form\SettingsForm'
      _title: 'Custom Settings'
    requirements:
      _permission: 'administer site configuration'
  ```
- Page Controllers inherit from `ControllerBase`:
  ```php
  class MyController extends ControllerBase {
    public function content() {
      return ['#markup' => $this->t('Hello World')];
    }
  }
  ```

## 5. Form API (OOP)
- Configuration Forms inherit from `ConfigFormBase`:
  ```php
  class SettingsForm extends ConfigFormBase {
    protected function getEditableConfigNames() { return ['my_module.settings']; }
    public function getFormId() { return 'my_module_settings_form'; }
    public function buildForm(array $form, FormStateInterface $form_state) { ... }
    public function submitForm(array &$form, FormStateInterface $form_state) { ... }
  }
  ```

## 6. Plugins & Annotations / Attributes
- Blocks inherit from `BlockBase` (`src/Plugin/Block/CustomBlock.php`).
- Field types, widgets, formatters inherit from plugin base classes.
- Drupal 10/11 supports modern PHP 8 attributes and standard annotations.

## 7. Event Dispatcher & Subscribers
- System hooks that have Symfony equivalents are handled via `EventSubscriberInterface`.
- Tagged with `event_subscriber` in `<module>.services.yml`.
