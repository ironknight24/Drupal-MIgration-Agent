# Rule: Safety Guarantees & Path Isolation

## 1. D7 Source Immutability (Rule 1 & Rule 2)
- All files under `source.path` (Drupal 7 codebase) are **strictly READ-ONLY**.
- Under no circumstances may any tool, agent, command, or script create, modify, or delete a file in `source.path`.
- Any attempt to write to `source.path` constitutes an immediate safety violation and must halt execution.

## 2. Target Path Isolation & Containment
- All generated code, modern classes, templates, and configuration MUST target `target.path` as specified in `migration.config.yml`.
- In single-module execution mode (`/orchestrate <MODULE>` or `/migrate-module <MODULE>`), file mutations are strictly restricted to:
  `target.path/<target_custom_modules_path>/<MODULE>/**/*` and `reports/migration/<MODULE>/*`.
- Writes to other custom modules, contrib modules, core files, or global directories outside the designated module scope are forbidden.

## 3. Secret & Credential Redaction (Rule 10)
- Never expose plaintext passwords, API keys, private tokens, or database credentials in reports, manifests, or generated modern code.
- If credentials or connection strings are detected in legacy files or external scripts, redact them as `[REDACTED]` and route target configuration to `settings.php` overrides, environment variables (`getenv()`), or the Drupal Key module.

## 4. Git & Data Safety
- No automated git commits, merges, or branch operations unless explicitly enabled in `migration.config.yml`.
- Strictly separate code behavior modernization from database table data migration. Never execute destructive data operations.

## 5. Reference
- Detailed specifications: [SAFETY_RULES.md](../../SAFETY_RULES.md)
