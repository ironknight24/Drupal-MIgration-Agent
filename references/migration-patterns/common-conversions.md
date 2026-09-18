# Common Migration & Modernization Patterns (D7 -> D10/11)

This reference outlines canonical conversions between procedural Drupal 7 paradigms and modern Drupal 10/11 architectures.

---

## Pattern 1: Page Callbacks -> Routing & Controllers

### Drupal 7 (`hook_menu`)
```php
function mymodule_menu() {
  $items['custom/report'] = array(
    'title' => 'Custom Report',
    'page callback' => 'mymodule_report_page',
    'access arguments' => array('view custom reports'),
    'type' => MENU_NORMAL_ITEM,
  );
  return $items;
}

function mymodule_report_page() {
  return '<div>Report Content</div>';
}
```

### Drupal 10 Target (`mymodule.routing.yml` & Controller)
```yaml
# mymodule.routing.yml
mymodule.report:
  path: '/custom/report'
  defaults:
    _controller: '\Drupal\mymodule\Controller\ReportController::view'
    _title: 'Custom Report'
  requirements:
    _permission: 'view custom reports'
```
```php
// src/Controller/ReportController.php
namespace Drupal\mymodule\Controller;

use Drupal\Core\Controller\ControllerBase;

class ReportController extends ControllerBase {
  public function view() {
    return [
      '#type' => 'container',
      '#markup' => $this->t('Report Content'),
    ];
  }
}
```

---

## Pattern 2: Variables API -> Configuration Management (CMI)

### Drupal 7
```php
$api_key = variable_get('mymodule_api_key', 'default_key');
variable_set('mymodule_api_key', 'new_key');
```

### Drupal 10 Target (Injected Service / ConfigFactory)
```yaml
# config/schema/mymodule.schema.yml
mymodule.settings:
  type: config_object
  label: 'MyModule Settings'
  mapping:
    api_key:
      type: string
      label: 'API Key'
```
```php
// Read
$apiKey = $this->configFactory->get('mymodule.settings')->get('api_key') ?? 'default_key';

// Write
$this->configFactory->getEditable('mymodule.settings')
  ->set('api_key', 'new_key')
  ->save();
```

---

## Pattern 3: Procedural DB Queries -> Injected Connection & Entity Queries

### Drupal 7
```php
$result = db_query("SELECT nid, title FROM {node} WHERE type = :type AND status = 1", array(':type' => 'article'));
foreach ($result as $record) {
  $node = node_load($record->nid);
}
```

### Drupal 10 Target (Entity Storage or Connection)
```php
// Preferred: Entity Query
$nids = $this->entityTypeManager->getStorage('node')->getQuery()
  ->accessCheck(TRUE)
  ->condition('type', 'article')
  ->condition('status', 1)
  ->execute();

$nodes = $this->entityTypeManager->getStorage('node')->loadMultiple($nids);

// Or when querying custom relational SQL tables:
$query = $this->database->select('my_custom_table', 'm')
  ->fields('m', ['id', 'label'])
  ->condition('status', 1);
$results = $query->execute()->fetchAll();
```

---

## Pattern 4: Global `$user` -> Current User Proxy

### Drupal 7
```php
global $user;
if ($user->uid > 0 && in_array('editor', $user->roles)) {
  // logic
}
```

### Drupal 10 Target
```php
if ($this->currentUser->isAuthenticated() && $this->currentUser->hasRole('editor')) {
  $uid = $this->currentUser->id();
}
```

---

## Pattern 5: `watchdog()` -> PSR-3 `LoggerInterface`

### Drupal 7
```php
watchdog('mymodule', 'Transaction @id failed.', array('@id' => $id), WATCHDOG_ERROR);
```

### Drupal 10 Target
```php
$this->logger->error('Transaction @id failed.', ['@id' => $id]);
```
