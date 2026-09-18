---
description: Perform a non-destructive preflight validation on the consumer migration configuration, paths, and environment markers.
---

# Drupal Migration: Preflight

Validate the consumer environment, configuration syntax, path isolation, and Drupal core structural markers before initiating discovery or code modification.

## Instructions for Claude:

1. Check if `migration.config.yml` exists in the workspace root.
   - If not found, instruct the user to copy `migration.config.example.yml` to `migration.config.yml` and provide project paths.
2. Parse `migration.config.yml` and validate required keys (`source.path`, `target.path`, `target.drupal_version`, `git.allow_commits`, etc.).
3. Execute the 10 Preflight Validation Checks:
   - **PRE-01**: `migration.config.yml` existence & syntax.
   - **PRE-02**: `source.path` exists and is readable.
   - **PRE-03**: `target.path` exists and is writable.
   - **PRE-04**: `source.path` and `target.path` do not overlap or nest.
   - **PRE-05**: `source.path` contains Drupal 7 core markers (`includes/bootstrap.inc`, `modules/system/system.module`).
   - **PRE-06**: `target.path` contains Drupal 10/11 core markers (`core/lib/Drupal.php` or `composer.json`).
   - **PRE-07**: `target.drupal_version` matches target core version (`10` or `11`).
   - **PRE-08**: Configured target subdirectories (`web/modules/custom`, `web/themes/custom`) exist or target root is writable.
   - **PRE-09**: Zero plaintext passwords/tokens in `migration.config.yml`.
   - **PRE-10**: Configured test tools (`phpunit`, `phpstan`, `phpcs`) exist if testing is enabled.
4. Generate the preflight validation report in `reports/preflight/PREFLIGHT-REPORT-<DATE>.md` using `templates/preflight-report.md`.
5. If any CRITICAL check fails:
   - Mark overall preflight status as `BLOCKED`.
   - Halt execution and present failing checks with concrete remediation steps.
6. If all CRITICAL checks pass:
   - Mark overall preflight status as `PASS`.
   - Instruct the user that the workspace is ready for `/discover` or `/orchestrate`.
