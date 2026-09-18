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
This skill governs the standards for writing modern, testable, and Drupal 11-ready code. It enforces constructor Dependency Injection, modern PHP 8 typing, and proper Drupal plugin/service interfaces.

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

### 3. PHP 8.1+ Type Safety & Attributes
- Strict return types and parameter type declarations on all class methods.
- Avoid deprecated D10 annotations where modern PHP 8 attributes are supported.
- Never use `@` error suppression or unhandled exceptions.

### 4. Zero Hardcoded Static Service Calls
Blind usage of `\Drupal::*` is strictly forbidden in service classes, controllers, and plugins.
