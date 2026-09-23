# Rule: External Drupal-Integrated PHP Code Protocol

## 1. Multi-Vector Evidence Engine
Do not classify standalone PHP files outside standard `modules/` and `themes/` directories as migration-relevant based merely on file path or name. Require concrete repository evidence across:
- **Drupal Bootstrap Evidence**: `DRUPAL_ROOT`, `drupal_bootstrap()`, `includes/bootstrap.inc`, `$user`, `node_load()`, `user_load()`, `taxonomy_*`, `variable_get()`, `variable_set()`, etc.
- **Drupal Database Evidence**: Queries targeting core tables (`{node}`, `{users}`, `{variable}`) or custom module tables with `{...}` syntax.
- **Drupal Module Coupling Evidence**: Invocations of custom/contrib module functions, classes, hooks, or service wrappers.
- **Runtime Entry Point Evidence**: Webhook endpoints, CLI scripts, cron runners, or queue dispatchers referenced by Drupal code/config.
- **Deployment References**: References in `.htaccess`, crontab configurations, or Drush alias files.

## 2. Confidence Scoring & Role Classification
- Assign confidence: `HIGH` (direct code proof), `MEDIUM` (structural/config reference), `LOW` (ambiguous -> `HUMAN_INTERVENTION_REQUIRED`).
- Classify role: `CLI_SCRIPT`, `WEBHOOK_ENDPOINT`, `STANDALONE_GATEWAY`, `CRON_WORKER`, `SHARED_UTILITY`, `OBSOLETE_SCRIPT`.

## 3. Behavior Unit Decomposition
Deconstruct multi-purpose external scripts into granular behavior units so that each behavior receives its own canonical status (`COMPLETE`, `PARTIAL`, `MISSING`, `OBSOLETE`, etc.) rather than assigning an overly broad file-level verdict.

## 4. Modern Architecture Mapping & Scoped Sub-DAG Inclusion
- Map entry points to modern Drupal 10/11 destinations: Drush Command Classes (`src/Drush/Commands/`), Controllers (`src/Controller/`), Services (`src/Service/`), or QueueWorkers (`src/Plugin/QueueWorker/`).
- For targeted single-module runs (`/orchestrate <MODULE>`), include external artifacts only if empirical dependency edges exist with `<MODULE>`.

## 5. Reference
- Detailed specifications: [skills/d7-analysis/SKILL.md](../../skills/d7-analysis/SKILL.md) Section 102 and [skills/d7-to-d10-mapping/SKILL.md](../../skills/d7-to-d10-mapping/SKILL.md) Section 17
