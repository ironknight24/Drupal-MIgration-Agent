# Antigravity Workflow: Preflight Environment Validation

## Purpose
Validates environment paths, configuration syntax, path isolation, and Drupal core structural markers before initiating discovery or code modification.

## Trigger & Invocation
This workflow is triggered via either slash commands or natural language conversation:

- **Slash Command**: `/preflight`
- **Conversational Triggers / Natural Intent**:
  - `preflight`
  - `run preflight`
  - `run preflight checks`
  - `perform migration preflight`
  - `check environment readiness`
  - `validate migration configuration`
- **Corresponding Claude Command**: `commands/preflight.md`

## Operational Procedure
1. Verify `migration.config.yml` exists in the workspace root. If missing, instruct user to copy `migration.config.example.yml`.
2. Parse `migration.config.yml` and execute the 10 Preflight Validation Checks (`PRE-01` to `PRE-10`):
   - `PRE-01`: Config existence and syntax.
   - `PRE-02`: `source.path` exists and is readable.
   - `PRE-03`: `target.path` exists and is writable.
   - `PRE-04`: `source.path` and `target.path` do not overlap or nest.
   - `PRE-05`: `source.path` contains D7 core markers (`includes/bootstrap.inc`).
   - `PRE-06`: `target.path` contains D10/11 markers (`core/lib/Drupal.php` or `composer.json`).
   - `PRE-07`: `target.drupal_version` matches target core version (`10` or `11`).
   - `PRE-08`: Target subdirectories exist or target root is writable.
   - `PRE-09`: Zero plaintext passwords/tokens in configuration.
   - `PRE-10`: Test tools (`phpunit`, `phpstan`, `phpcs`) exist if testing is enabled.
3. Generate `reports/preflight/PREFLIGHT-REPORT-<DATE>.md` using `templates/preflight-report.md`.
4. If any critical check fails, mark status `BLOCKED` and halt. If all pass, mark `PASS` and notify workspace is ready.
