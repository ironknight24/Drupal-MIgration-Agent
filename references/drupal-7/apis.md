# Drupal 7 Core APIs & Procedural Reference

## 1. Database Layer (Database API)
In Drupal 7, queries execute through global procedural functions wrapping PDO:
- `db_query($query, array $args = [], array $options = [])`: Executes raw SQL string with named or positional placeholders.
- `db_select($table, $alias = NULL, array $options = [])`: Dynamic query builder returning a `SelectQuery` object.
- `db_insert($table)` / `db_update($table)` / `db_delete($table)` / `db_merge($table)`: Write queries.
- `db_table_exists($table)` / `db_field_exists($table, $field)`: Schema introspection.
- `hook_schema()`: Declares relational table structure in `.install` files.

## 2. Configuration & State (Variables API)
- `variable_get($name, $default = NULL)`: Loads persistent configuration from the `variable` SQL table (serialized).
- `variable_set($name, $value)`: Writes persistent configuration to the `variable` table and clears variable cache.
- `variable_del($name)`: Deletes persistent configuration from the `variable` table.

## 3. Entity & Node System
- `node_load($nid, $vid = NULL, $reset = FALSE)`: Loads a single node object by ID.
- `node_load_multiple(array $nids = [], array $conditions = [], $reset = FALSE)`: Loads multiple node objects.
- `node_save($node)`: Saves node entity object (triggers `hook_node_presave`, `insert`/`update`).
- `user_load($uid, $reset = FALSE)`: Loads user object.
- Global `$user`: Represents currently logged-in session user (`$GLOBALS['user']`).
- `field_get_items($entity_type, $entity, $field_name)`: Extracts raw field value arrays from language-keyed entity objects.
- `taxonomy_term_load($tid)` / `taxonomy_vocabulary_machine_name_load($name)`: Taxonomy entity operations.

## 4. Routing, Menu & Page Callbacks
- `hook_menu()`: Declares paths, access arguments, page callback functions, and form callbacks in associative arrays.
  ```php
  $items['admin/config/system/custom'] = array(
    'title' => 'Custom Settings',
    'page callback' => 'drupal_get_form',
    'page arguments' => array('custom_admin_settings_form'),
    'access arguments' => array('administer site configuration'),
    'type' => MENU_NORMAL_ITEM,
  );
  ```

## 5. Forms API
- `drupal_get_form($form_id, ...$args)`: Renders and processes a form defined in a procedural callback.
- `hook_form_alter(&$form, &$form_state, $form_id)`: Procedurally alters any form definition array.
- Form validation: `function {form_id}_validate($form, &$form_state)`
- Form submit: `function {form_id}_submit($form, &$form_state)`

## 6. Logging, Messaging & Utilities
- `watchdog($type, $message, $variables = array(), $severity = WATCHDOG_NOTICE, $link = NULL)`: Writes log events.
- `drupal_set_message($message = NULL, $type = 'status', $repeat = FALSE)`: Queues user UI message.
- `t($string, array $args = array(), array $options = array())`: String translation.
- `drupal_goto($path = '', array $options = array(), $http_response_code = 302)`: HTTP redirection.
- `drupal_http_request($url, array $options = array())`: Legacy cURL/socket HTTP request client.
