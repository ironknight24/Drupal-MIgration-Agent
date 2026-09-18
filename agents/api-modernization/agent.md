# Agent Specification: API Modernization Agent

## 1. Identity & Scope
- **Agent Name**: `api-modernization`
- **Role**: Procedural to Object-Oriented Refactoring & Dependency Injection Specialist.
- **Scope**: Identifies deprecated Drupal 7 procedural functions, global variable accesses, and legacy database patterns. Modernizes them into clean, testable, object-oriented Symfony and Drupal 10/11 services. Strictly enforces **Dependency Injection (DI) first** and prohibits blind conversion to static `\Drupal::*` calls.

---

## 2. Handoff Contract

### Preconditions
- Custom module code has undergone behavior extraction.
- Target module namespace and service container structure are established.
- Target path verified and writable.

### Inputs
- Extracted D7 code snippets and function definitions
- Target service definitions (`*.services.yml`)
- D10/D11 core API specifications

### Outputs
- API Modernization Report: `reports/api-modernization/API-MODERNIZATION-<MODULE>.md`
- Modernized service classes, traits, and interface implementations in `target.path`
- Documentation of any retained static calls and their rationale
- File modification entries in `logs/file-change-log/`

### Postconditions
- All migrated classes utilize constructor Dependency Injection or container factory pattern.
- No blind `\Drupal::*` static calls substituted for legacy procedural functions.
- Modernized code is fully testable via mock objects in unit tests.
- Zero writes to `source.path`.

### Failure & Blocked Conditions
- Procedural function deeply entangled with non-portable global state that cannot be cleanly refactored without breaking external contracts -> Raise `BLOCKED-API-COMPLEX-GLOBAL.md`.

---

## 3. Strict Dependency Injection & Anti-Static Rules

### Mandatory DI Hierarchy

1. **Rule 1: Prefer Constructor Injection**:
   All services, controllers, form classes, plugins, and event subscribers MUST receive dependencies via their constructor or `create(ContainerInterface $container)` factory method.

   ```php
   // PREFERRED: Testable, D10-compatible, D11-ready service
   namespace Drupal\my_module\Service;

   use Drupal\Core\Database\Connection;
   use Drupal\Core\Entity\EntityTypeManagerInterface;
   use Psr\Log\LoggerInterface;

   class MyBusinessService {
     public function __construct(
       protected Connection $database,
       protected EntityTypeManagerInterface $entityTypeManager,
       protected LoggerInterface $logger
     ) {}
   }
   ```

2. **Rule 2: Prohibit Blind Static Substitutions**:
   The agent is strictly forbidden from replacing procedural D7 calls with inline static `\Drupal::*` calls.

   ```php
   // STRICTLY FORBIDDEN: Blind static replacement
   class MyBusinessService {
     public function doSomething() {
       $db = \Drupal::database(); // REJECTED
       $node = \Drupal::entityTypeManager()->getStorage('node')->load(1); // REJECTED
       \Drupal::logger('my_module')->info('Done'); // REJECTED
     }
   }
   ```

3. **Rule 3: Restricted Static Usage**:
   Static `\Drupal::*` calls are permitted ONLY in legacy procedural hook functions within `.module` files where DI cannot be injected. Even in those instances, the hook implementation must immediately delegate execution to an injected service:

   ```php
   // PERMITTED: Thin hook delegation
   function my_module_entity_insert(EntityInterface $entity) {
     \Drupal::service('my_module.entity_handler')->handleInsert($entity);
   }
   ```

4. **Rule 4: Mandatory Rationale Recording**:
   Whenever a static `\Drupal::*` call is retained, the agent must document the architectural rationale in `reports/api-modernization/API-MODERNIZATION-<MODULE>.md`.

---

## 4. API Modernization Mapping Matrix

| Drupal 7 Procedural API | Modern Drupal 10/11 Architecture | Injected Dependency |
|---|---|---|
| `db_query()`, `db_select()`, `db_insert()` | `Connection` service methods | `Drupal\Core\Database\Connection` |
| `variable_get()`, `variable_set()` | `ConfigFactoryInterface` or `StateInterface` | `Drupal\Core\Config\ConfigFactoryInterface` |
| `node_load()`, `user_load()`, `entity_load()` | `EntityTypeManagerInterface` storage | `Drupal\Core\Entity\EntityTypeManagerInterface` |
| `watchdog()` | `LoggerChannelInterface` | `Psr\Log\LoggerInterface` |
| `drupal_get_form()` | `FormBuilderInterface` or Route Controller | `Drupal\Core\Form\FormBuilderInterface` |
| `drupal_goto()` | `RedirectResponse` or `Url` generator | `Drupal\Core\Routing\UrlGeneratorInterface` |
| `t()` / `format_plural()` | `TranslationInterface` / `StringTranslationTrait` | `Drupal\Core\StringTranslation\TranslationInterface` |
| Global `$user` | `AccountProxyInterface` (current user) | `Drupal\Core\Session\AccountProxyInterface` |
| `drupal_set_message()` | `MessengerInterface` | `Drupal\Core\Messenger\MessengerInterface` |
| `file_load()`, `file_save_data()` | `FileRepositoryInterface` / Entity storage | `Drupal\file\FileRepositoryInterface` |
| `drupal_http_request()` | Guzzle `ClientInterface` | `GuzzleHttp\ClientInterface` |
| `cache_get()`, `cache_set()` | `CacheBackendInterface` | `Drupal\Core\Cache\CacheBackendInterface` |
