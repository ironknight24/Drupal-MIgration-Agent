# Drupal 7 Core & Contrib Hooks to Modern Architecture Catalog

This reference documents canonical Drupal 7 hooks and their architectural equivalents in modern Drupal (Drupal 10.x and Drupal 11.x).

---

## 1. System, Bootstrap & Lifecycle Hooks

| Drupal 7 Hook | Target Modern Architecture | Implementation Mechanism | Notes / Target Version Differences |
| :--- | :--- | :--- | :--- |
| `hook_boot()` | Removed / Middleware | HTTP Middleware (`http_middleware` service tag) | Drupal 8+ replaces bootstrap hooks with PSR-15 / Symfony middleware. |
| `hook_init()` | Event Subscriber | `KernelEvents::REQUEST` subscriber | Injected service implementing `EventSubscriberInterface`. |
| `hook_exit()` | Event Subscriber | `KernelEvents::TERMINATE` subscriber | Post-response cleanup and shutdown processing. |
| `hook_cron()` | `hook_cron()` or QueueWorker | Thin hook in `.module` delegating to Queue or Cron service | Core recommends decoupling heavy processing into `QueueWorker` plugins. |
| `hook_watchdog()` | Monolog / PSR-3 Logger | Custom `LoggerInterface` or Monolog handler | Register custom loggers via service container tag `logger`. |

---

## 2. Routing, Menu & Page Display Hooks

| Drupal 7 Hook | Target Modern Architecture | Implementation Mechanism | Notes / Target Version Differences |
| :--- | :--- | :--- | :--- |
| `hook_menu()` | Routing & Menu Links | `<module>.routing.yml`, `<module>.links.menu.yml`, `<module>.links.task.yml`, `<module>.links.action.yml` | In D7, `hook_menu` handled URLs, menus, tabs, and permissions. Modern Drupal completely decouples these concerns. |
| `hook_menu_alter()` | Route Subscriber | `RouteSubscriberBase` (`alterRoutes(RouteCollection $collection)`) | Event-driven dynamic route manipulation. |
| `hook_theme()` | `hook_theme()` | Kept in `.module`, returns render element / template definitions | Template files change from `.tpl.php` to Twig `.html.twig`. |
| `hook_block_info()` / `hook_block_view()` | Block Plugin | `BlockBase` plugin class under `src/Plugin/Block/` | In D10/D11, blocks are instantiated as plugins; UI placement is saved in CMI config. |

---

## 3. Entity & Field Lifecycle Hooks

| Drupal 7 Hook | Target Modern Architecture | Implementation Mechanism | Notes / Target Version Differences |
| :--- | :--- | :--- | :--- |
| `hook_node_load()` / `hook_entity_load()` | `hook_ENTITY_TYPE_load()` | Thin hook or Entity Storage handler | Delegate processing to injected entity helper service. |
| `hook_node_presave()` / `hook_entity_presave()` | `hook_ENTITY_TYPE_presave()` | Thin hook in `.module` delegating to service | Executes before entity database transaction commits. |
| `hook_node_insert()` / `hook_node_update()` | `hook_ENTITY_TYPE_insert()` / `update()` | Thin hook or custom Symfony Event | Prefer event dispatching from hooks for clean decoupling. |
| `hook_node_delete()` | `hook_ENTITY_TYPE_delete()` | Thin hook delegating to service | Cascading cleanup must use Entity API or Queue. |
| `hook_node_access()` | `hook_ENTITY_TYPE_access()` | Returns `AccessResultInterface` | Modern access returns `AccessResult::allowed()`, `neutral()`, or `forbidden()` with cache metadata. |
| `hook_node_view()` | `hook_ENTITY_TYPE_view()` | Modifies render array with cache tags | Must attach cache contexts and tags (`#cache`). |

---

## 4. Form & User Interaction Hooks

| Drupal 7 Hook | Target Modern Architecture | Implementation Mechanism | Notes / Target Version Differences |
| :--- | :--- | :--- | :--- |
| `drupal_get_form()` | Form Class | Class extending `FormBase` or `ConfigFormBase` | Form definition, validation, and submission encapsulated in OOP class. |
| `hook_form_alter()` | `hook_form_alter()` | Kept in `.module` or delegated to Form Alter Service | Thin hook calling service; must preserve form structure and state. |
| `hook_form_FORM_ID_alter()` | `hook_form_FORM_ID_alter()` | Specific form alter in `.module` | Preferred over global `hook_form_alter` for performance. |
| `hook_user_login()` | Event / Hook | `hook_user_login()` delegating to service | Symfony `EventSubscriber` can also listen to authentication events. |
| `hook_user_logout()` | Event / Hook | `hook_user_logout()` delegating to service | Session invalidation and audit logging. |

---

## 5. Database & Schema Hooks

| Drupal 7 Hook | Target Modern Architecture | Implementation Mechanism | Notes / Target Version Differences |
| :--- | :--- | :--- | :--- |
| `hook_schema()` | `hook_schema()` or Content Entity | `.install` file schema array, or Content Entity definition | If storing structured business data, prefer custom Content Entity types. |
| `hook_install()` | `hook_install()` | Thin hook in `.install` file | Used for initial non-configuration setup. |
| `hook_uninstall()` | `hook_uninstall()` | Thin hook in `.install` file | Cleanup of custom tables or state data. |
| `hook_update_N()` | `hook_update_N()` or `hook_post_update_NAME()` | `.install` or `.post_update.php` | Schema updates in `hook_update_N`; entity/content data fixes in `post_update`. |

---

## 6. Target Version Differences (Drupal 10 vs. Drupal 11)

| Area | Drupal 10.x | Drupal 11.x | Migration Implication |
| :--- | :--- | :--- | :--- |
| **Plugin Metadata** | DocBlock Annotations supported; Attributes supported in D10.2+. | PHP 8 Attributes preferred across all core plugin managers. | Verify target plugin manager support before converting. Prefer Attributes for forward readiness. |
| **Core Modules** | Modules like `book`, `forum`, `action`, `statistics` present in core. | Removed from core; available as contributed modules. | Evaluate component usage individually before migrating. |
| **Symfony Components** | Symfony 6.4 LTS foundation. | Symfony 7 foundation. | Stricter native PHP type declarations and return types. |
| **PHP Requirements** | PHP >= 8.1. | PHP >= 8.3. | Modern syntax (readonly classes, typed constants) fully supported. |
