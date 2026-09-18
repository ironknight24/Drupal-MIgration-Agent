# Drupal 10 & 11 Plugin Types & Modern Architecture Reference

This reference details modern Drupal plugin architectures, constructor Dependency Injection, and the transition between DocBlock Annotations and PHP 8 Attributes.

---

## 1. Architectural Rules for Plugin Discovery

```text
Drupal 10.2+ supports PHP Attributes for plugin discovery.

For new plugin implementations, prefer PHP Attributes when the relevant
plugin manager supports them.

Existing DocBlock annotations remain supported where applicable.

Drupal 11 core predominantly uses PHP Attributes, but migration logic
must verify the specific target plugin type/plugin manager before converting
annotations to Attributes.

Never perform a blind annotation → Attribute conversion.
```

### Discovery Compatibility Matrix

| Plugin Type | Annotations Supported | Attributes Supported (D10.2+) | Attributes Preferred (D11) | Annotation Class | Attribute Class |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Block** | Yes | Yes (10.2+) | Yes | `@Block` | `Drupal\Core\Block\Attribute\Block` |
| **FieldType** | Yes | Yes (10.2+) | Yes | `@FieldType` | `Drupal\Core\Field\Attribute\FieldType` |
| **FieldWidget** | Yes | Yes (10.2+) | Yes | `@FieldWidget` | `Drupal\Core\Field\Attribute\FieldWidget` |
| **FieldFormatter** | Yes | Yes (10.2+) | Yes | `@FieldFormatter` | `Drupal\Core\Field\Attribute\FieldFormatter` |
| **MigrateSource** | Yes | Yes (10.3+) | Yes | `@MigrateSource` | `Drupal\migrate\Attribute\MigrateSource` |
| **MigrateProcess** | Yes | Yes (10.3+) | Yes | `@MigrateProcessPlugin` | `Drupal\migrate\Attribute\MigrateProcessPlugin` |
| **MigrateDestination**| Yes | Yes (10.3+) | Yes | `@MigrateDestination`| `Drupal\migrate\Attribute\MigrateDestination` |
| **QueueWorker** | Yes | Yes (10.2+) | Yes | `@QueueWorker` | `Drupal\Core\Queue\Attribute\QueueWorker` |
| **Condition** | Yes | Yes (10.2+) | Yes | `@Condition` | `Drupal\Core\Condition\Attribute\Condition` |

---

## 2. Block Plugin Implementation Pattern

### PHP 8 Attribute Syntax (Preferred for D10.2+ & D11)

```php
namespace Drupal\custom_core\Plugin\Block;

use Drupal\Core\Block\Attribute\Block;
use Drupal\Core\Block\BlockBase;
use Drupal\Core\Plugin\ContainerFactoryPluginInterface;
use Drupal\Core\StringTranslation\TranslatableMarkup;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Drupal\Core\Session\AccountProxyInterface;

#[Block(
  id: "custom_user_status_block",
  admin_label: new TranslatableMarkup("Custom User Status"),
  category: new TranslatableMarkup("Custom")
)]
class CustomUserStatusBlock extends BlockBase implements ContainerFactoryPluginInterface {

  public function __construct(
    array $configuration,
    $plugin_id,
    $plugin_definition,
    protected AccountProxyInterface $currentUser
  ) {
    super($configuration, $plugin_id, $plugin_definition);
  }

  public static function create(ContainerInterface $container, array $configuration, $plugin_id, $plugin_definition): static {
    return new static(
      $configuration,
      $plugin_id,
      $plugin_definition,
      $container->get('current_user')
    );
  }

  public function build(): array {
    return [
      '#theme' => 'custom_user_status',
      '#user_id' => $this->currentUser->id(),
      '#cache' => [
        'contexts' => ['user'],
      ],
    ];
  }
}
```

### DocBlock Annotation Syntax (Legacy D10 Compatibility)

```php
/**
 * Provides a user status block.
 *
 * @Block(
 *   id = "custom_user_status_block",
 *   admin_label = @Translation("Custom User Status"),
 *   category = @Translation("Custom")
 * )
 */
class CustomUserStatusBlock extends BlockBase implements ContainerFactoryPluginInterface {
  // Same implementation
}
```

---

## 3. Migration Process Plugin Pattern

Migration process plugins transform source values inside migration pipelines (`migrate_plus.migration.*.yml`).

```php
namespace Drupal\custom_migrate\Plugin\migrate\process;

use Drupal\migrate\Attribute\MigrateProcessPlugin;
use Drupal\migrate\MigrateExecutableInterface;
use Drupal\migrate\Plugin\MigrateProcessPluginBase;
use Drupal\migrate\Row;

#[MigrateProcessPlugin(
  id: "custom_timestamp_converter"
)]
class CustomTimestampConverter extends MigrateProcessPluginBase {

  public function transform($value, MigrateExecutableInterface $migrate_executable, Row $row, $destination_property): mixed {
    if (empty($value)) {
      return NULL;
    }
    // Convert D7 UNIX timestamp or date string to ISO-8601 format
    return date('Y-m-d\TH:i:s', (int) $value);
  }
}
```

---

## 4. QueueWorker Plugin Pattern

Queue workers process background jobs queued during entity lifecycles, webhooks, or cron.

```php
namespace Drupal\custom_core\Plugin\QueueWorker;

use Drupal\Core\Plugin\ContainerFactoryPluginInterface;
use Drupal\Core\Queue\Attribute\QueueWorker;
use Drupal\Core\Queue\QueueWorkerBase;
use Drupal\Core\StringTranslation\TranslatableMarkup;
use Symfony\Component\DependencyInjection\ContainerInterface;
use Psr\Log\LoggerInterface;

#[QueueWorker(
  id: "custom_external_sync_queue",
  title: new TranslatableMarkup("Custom External Sync Queue"),
  cron: ["time" => 30]
)]
class CustomExternalSyncQueueWorker extends QueueWorkerBase implements ContainerFactoryPluginInterface {

  public function __construct(
    array $configuration,
    $plugin_id,
    $plugin_definition,
    protected LoggerInterface $logger
  ) {
    super($configuration, $plugin_id, $plugin_definition);
  }

  public static function create(ContainerInterface $container, array $configuration, $plugin_id, $plugin_definition): static {
    return new static(
      $configuration,
      $plugin_id,
      $plugin_definition,
      $container->get('logger.channel.custom_core')
    );
  }

  public function processItem($data): void {
    $this->logger->info('Processing queued item: @id', ['@id' => $data['id'] ?? 'unknown']);
  }
}
```

---

## 5. Event Subscriber Pattern (Symfony Event Dispatcher)

Event subscribers handle system-wide events without modifying core or upstream modules.

### Class Definition (`src/EventSubscriber/UserLoginSubscriber.php`)

```php
namespace Drupal\custom_core\EventSubscriber;

use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\KernelEvents;
use Psr\Log\LoggerInterface;

class UserLoginSubscriber implements EventSubscriberInterface {

  public function __construct(
    protected LoggerInterface $logger
  ) {}

  public static function getSubscribedEvents(): array {
    return [
      KernelEvents::REQUEST => ['onRequest', 20],
    ];
  }

  public function onRequest(RequestEvent $event): void {
    if (!$event->isMainRequest()) {
      return;
    }
    // Execution logic
  }
}
```

### Container Registration (`custom_core.services.yml`)

```yaml
services:
  custom_core.request_subscriber:
    class: Drupal\custom_core\EventSubscriber\UserLoginSubscriber
    arguments: ['@logger.channel.custom_core']
    tags:
      - { name: event_subscriber }
```
