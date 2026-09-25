# Safety Rules & Guardrails

This document establishes the 15 non-negotiable safety rules governing all agent behaviors in the Drupal Migration Framework. Violations will trigger an immediate halt and raise a safety exception.

---

## The 15 Cardinal Safety Rules

### RULE 1: Never Delete Source Drupal 7 Files
The source Drupal 7 codebase is historic reference material. Under no circumstances may an agent invoke `rm`, delete, unlink, or prune files or directories within `source.path`.

### RULE 2: Never Modify Drupal 7 Source Files
The Drupal 7 codebase is strictly **READ-ONLY**. Agents must not edit, format, patch, touch, or alter permissions on any file inside `source.path`.

### RULE 3: Never Overwrite Target Files Without Recording the Change
Before writing, modifying, or creating any file in `target.path`, the agent must log the target path, source reference, action type, and rationale into `logs/file-change-log/`. Unrecorded file mutations are forbidden.

### RULE 4: Never Claim Functionality Was Migrated Without Evidence
An agent must never declare a module, feature, or route "migrated" simply because code was written. A claim of completion requires an implementation report, functional tests, or a comparative behavioral validation ticket citing empirical proof.

### RULE 5: Never Claim Tests Passed Unless Tests Were Actually Executed
Agents must never generate synthetic test results or assume tests would pass. A `PASS` status requires an executed CLI test command returning exit code 0, complete with terminal output logs.

### RULE 6: Never Silently Ignore Errors
Any exception, compilation error, fatal hook failure, database error, or missing dependency must be explicitly documented. Suppressing errors with `@`, empty `catch` blocks, or unhandled return values is strictly prohibited.

### RULE 7: Never Silently Replace a Contributed Module
The Contrib Module Agent must not unilaterally substitute a D7 contributed module with a modern equivalent. Replacements must be proposed in a structured report (`reports/contrib/`) documenting feature parity, data implications, and configuration changes for human approval.

### RULE 8: Never Migrate Data Without Documenting Source-to-Target Mapping
Every database table, entity, field, and taxonomy migration must have a documented field-by-field and type-by-type mapping plan in `reports/data/` before migration execution begins.

### RULE 9: Never Commit Git Changes
Git commits and branch creations are disabled by default (`allow_commits: false`, `allow_branch_creation: false`). Changes must be preserved in the filesystem and tracked through file change logs and diffs.

### RULE 10: Never Expose Credentials or Secrets in Reports
Passwords, API keys, private tokens, salt keys, hash secrets, and database credentials must never be written to reports, plans, manifests, or logs. Use environment variables or placeholders (`${SECRET_KEY}`).

### RULE 11: When Uncertain, Document the Uncertainty
If a Drupal 7 implementation has ambiguous business logic, undefined data formats, or obscure hook alters, the agent must document the uncertainty as an `[ASSUMPTION]` and request human clarification rather than guessing.

### RULE 12: When Blocked, Continue Unrelated Work and Create a Blocked Report
An issue affecting a single module or feature must never stall the entire migration. The agent creates a `BLOCKED-XXX.md` ticket, updates the manifest, and moves to independent components. Only safety or system-level corruptions justify a `GLOBAL MIGRATION BLOCKED` halt.

### RULE 13: Do Not Confuse Syntactic Compatibility with Functional Equivalence
Code that compiles cleanly under PHP 8 or satisfies a D10 interface may still fail business expectations. Compatibility is validated by behavioral comparison of business outputs, not merely linter or syntax passes.

### RULE 14: Do Not Blindly Translate Drupal 7 Code into Drupal 10 Code
Direct 1:1 translation of procedural code into static classes or global calls is rejected. Code must be re-engineered into modern Drupal paradigms: Dependency Injection, services, plugins, event subscribers, and Twig templates.

### RULE 15: Preserve Business Behavior Unless Explicitly Documented
Business rules, validation logic, access restrictions, calculation routines, and workflow triggers must remain functionally identical to D7 unless a deliberate change was specified and documented in the approved migration plan.

### RULE 16: Strict Path Confinement & Adjacent Directory Prohibition
All source code reads must be strictly confined to `source.path` and all target code writes/inspections must be strictly confined to `target.path` as declared in `migration.config.yml`. The agent is strictly prohibited from searching, inspecting, referencing, or importing code from adjacent directories, sibling folders, parent directories, or backup repositories outside the configured `source.path` and `target.path`.

### RULE 17: Pure Drupal 10 Standards for From-Scratch Module Generation
When a custom module exists in `source.path` and does not exist in `target.path`, the agent must scaffold and generate the modern D10 module from scratch. It must faithfully reproduce the D7 module's business behavior, caching mechanisms (tags/contexts/max-age), security controls (permissions/CSRF/access checkers), and inter-module interactions (events/hooks/services) using 100% pure modern Drupal 10/11 standards (PSR-4 autoloading, Constructor Dependency Injection, CMI YAML configuration, Twig templates).

---

## Enforceable Path Protection Mechanics

Every agent must enforce the following validation logic prior to ANY filesystem modification:

```python
# Conceptual Path Isolation Gate
def validate_write_operation(target_file_path, config):
    source_root = os.path.abspath(config['source']['path'])
    target_root = os.path.abspath(config['target']['path'])
    file_path = os.path.abspath(target_file_path)

    # Check 1: Target must not reside inside source
    if file_path.startswith(source_root):
        raise SecurityException(f"SAFETY VIOLATION: Attempted write to D7 source path: {file_path}")

    # Check 2: Target must reside within target.path
    if not file_path.startswith(target_root):
        raise SecurityException(f"SAFETY VIOLATION: Write target outside D10 target directory: {file_path}")

    # Check 3: Overlap detection
    if source_root == target_root or source_root.startswith(target_root) or target_root.startswith(source_root):
        raise SecurityException(f"GLOBAL SAFETY VIOLATION: Source and Target paths overlap!")
```
