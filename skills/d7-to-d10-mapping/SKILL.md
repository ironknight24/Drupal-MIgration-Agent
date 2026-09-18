---
name: d7-to-d10-mapping
description: Behavioral and architectural mapping rules for converting procedural Drupal 7 APIs into modern Drupal 10/11 object-oriented patterns. Use when mapping legacy logic to modern Drupal architectures.
version: 1.0.0
user-invocable: true
disable-model-invocation: false
allowed-tools: Read, Grep
---

# Drupal 7 to Drupal 10/11 Architectural Mapping Skill

## Overview
This skill provides the architectural mapping rules required to translate Drupal 7 procedural constructs into modern Symfony/Drupal 10 and Drupal 11 object-oriented paradigms, prioritizing Dependency Injection, service containers, and testability.

---

## Technical References
For detailed syntax examples and conversion catalogs, consult:
- [Common Migration & Modernization Patterns](file:///Users/deepak/Desktop/Projects/drupal-migration/references/migration-patterns/common-conversions.md)
- [Drupal 7 Hooks to Modern Architecture Catalog](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-7/hooks.md)
- [Drupal 10 & 11 Plugin Types & Modern Architecture](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-10/plugin-types.md)
- [Drupal 10 Architecture Reference](file:///Users/deepak/Desktop/Projects/drupal-migration/references/drupal-10/architecture.md)

---

## Core Mapping Rules

### 1. hook_menu() Separation
In Drupal 7, `hook_menu()` handled page routing, menu items, tabs, contextual links, and form endpoints simultaneously. In modern Drupal, these are decoupled:
- Page URLs & Handlers -> `<module>.routing.yml` & `ControllerBase`
- Menu links -> `<module>.links.menu.yml`
- Local tasks (tabs) -> `<module>.links.task.yml`
- Contextual actions -> `<module>.links.action.yml`
- Permission definitions -> `<module>.permissions.yml`

### 2. State & Settings Modernization
- **Configuration (CMI)**: Static settings that should be deployed across environments (`site_name`, API endpoint URLs) map to Configuration Objects (`config/install/<module>.settings.yml` and `config/schema/`).
- **State API**: Dynamic environment-specific values (`last_cron_run`, synchronization timestamps) map to the `state` service (`\Drupal::state()` or injected `StateInterface`).

### 3. Entity & Database Abstraction
- Direct `db_query()` targeting core tables (`{node}`, `{users}`) MUST be replaced by Entity Queries via `EntityTypeManagerInterface`.
- Direct `db_query()` targeting bespoke custom tables must be refactored into either:
  1. A custom Content Entity type (preferred for structured business data).
  2. The injected `Connection` service using parameterized SQL queries.

### 4. Hook Alter & Event Conversion
- System events (e.g., user login, response filters, routing alterations) map to Symfony `EventSubscriberInterface`.
- Form alters (`hook_form_alter()`) remain in `.module` but must delegate business processing to an injected service.
