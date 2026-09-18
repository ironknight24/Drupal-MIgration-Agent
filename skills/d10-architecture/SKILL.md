---
name: d10-architecture
description: Drupal 10 and 11-ready object-oriented programming standards, constructor Dependency Injection, PHP 8 attributes, and plugin patterns. Use when designing modern Drupal architecture.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep
---

# Drupal 10 & 11-Ready Architectural Standards Skill

## Overview
This skill governs the standards for writing modern, testable, and Drupal 11-ready code. It enforces constructor Dependency Injection, target-version-aware PHP typing, and proper Drupal plugin/service interfaces.

---

## Technical References
For full code patterns and catalogs, consult:
- [Drupal 10 & 11 Plugin Types & Modern Architecture](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-10/plugin-types.md)
- [Drupal 10 Architecture Reference](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-10/architecture.md)
- [Common Migration & Modernization Patterns](file:///Users/deepak/Desktop/Projects/drupal-migration/references/migration-patterns/common-conversions.md)

---

## Target Version Resolution & PHP Standards

```text
Target-version requirements must be resolved from the specific Drupal
core version being migrated to.

Current baseline:
- Drupal 10: PHP >= 8.1
- Drupal 11: PHP >= 8.3

Do not hard-code these requirements as permanent truths.
During actual migration discovery, verify the exact target Drupal core
version and its official system requirements.
```

---

## Plugin Discovery: Attributes vs. Annotations

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

---

## Architecture Principles

### 1. Mandatory Constructor Dependency Injection
All services, controllers, form classes, and plugins must receive dependencies via constructor injection.

```php
namespace Drupal\my_module\Service;

use Drupal\Core\Database\Connection;
use Drupal\Core\Entity\EntityTypeManagerInterface;
use Psr\Log\LoggerInterface;

class OrderProcessor {
  public function __construct(
    protected Connection $database,
    protected EntityTypeManagerInterface $entityTypeManager,
    protected LoggerInterface $logger
  ) {}
}
```

### 2. Container Injection in Controllers / Forms / Plugins
Classes instantiated by Drupal's factory must implement `ContainerInjectionInterface` or use `create(ContainerInterface $container)`:

```php
public static function create(ContainerInterface $container) {
  return new static(
    $container->get('database'),
    $container->get('entity_type.manager'),
    $container->get('logger.channel.my_module')
  );
}
```

### 3. Type Safety & Return Types
- Strict return types and parameter type declarations on all class methods.
- Eliminate `@` error suppression. Handle exceptions explicitly with structured logging.

### 4. Zero Hardcoded Static Service Calls
Blind usage of `\Drupal::*` is strictly forbidden in service classes, controllers, and plugins.
