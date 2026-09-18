---
report_id: "PREFLIGHT-{{ DATE }}"
category: "preflight"
agent: "orchestrator"
created_at: "{{ TIMESTAMP }}"
source_path: "{{ SOURCE_PATH }}"
target_path: "{{ TARGET_PATH }}"
target_version: "{{ TARGET_VERSION }}"
overall_status: "{{ OVERALL_STATUS }}" # PASS | BLOCKED | WARNING
evidence_summary:
  checks_total: 10
  passed: 0
  failed: 0
  warnings: 0
runtime_status: "[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]"
---

# Preflight Environment & Configuration Validation Report

## 1. Executive Summary
- **Evaluation Timestamp**: {{ TIMESTAMP }}
- **Source Codebase (D7)**: `{{ SOURCE_PATH }}`
- **Target Codebase (D10/D11)**: `{{ TARGET_PATH }}`
- **Target Architecture**: Drupal {{ TARGET_VERSION }}
- **Overall Preflight Gate Result**: **{{ OVERALL_STATUS }}**
- **Blocking Issues Count**: {{ FAILED_COUNT }}

---

## 2. Preflight Check Results Matrix

| Check ID | Check Description | Severity | Result | Evidence Type | Blocking? |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **PRE-01** | Configuration File Existence & Syntax | CRITICAL | {{ RES_01 }} | [OBSERVED FACT] | **YES** |
| **PRE-02** | Source Path Existence & Readability | CRITICAL | {{ RES_02 }} | [OBSERVED FACT] | **YES** |
| **PRE-03** | Target Path Existence & Writable Root | CRITICAL | {{ RES_03 }} | [OBSERVED FACT] | **YES** |
| **PRE-04** | Source / Target Isolation & Non-Overlap | CRITICAL | {{ RES_04 }} | [OBSERVED FACT] | **YES** |
| **PRE-05** | Drupal 7 Source Structural Markers | CRITICAL | {{ RES_05 }} | [OBSERVED FACT] | **YES** |
| **PRE-06** | Drupal 10/11 Target Markers | CRITICAL | {{ RES_06 }} | [OBSERVED FACT] | **YES** |
| **PRE-07** | Target Version Consistency | WARNING | {{ RES_07 }} | [OBSERVED FACT] | NO |
| **PRE-08** | Configured Target Subdirectory Scaffolding | MAJOR | {{ RES_08 }} | [OBSERVED FACT] | **YES** |
| **PRE-09** | Plaintext Secret & Credential Detection | CRITICAL | {{ RES_09 }} | [OBSERVED FACT] | **YES** |
| **PRE-10** | Configured Test Tool Availability | MINOR | {{ RES_10 }} | [OBSERVED FACT] | NO |

---

## 3. Detailed Check Findings & Evidence

### PRE-01: Configuration File Existence (`migration.config.yml`)
- **Status**: {{ RES_01 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_01 }}
- **Remediation**: Copy `migration.config.example.yml` to `migration.config.yml` in the workspace root.

### PRE-02: Source Path Accessibility
- **Status**: {{ RES_02 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_02 }}
- **Remediation**: Verify `source.path` points to a valid, readable local Drupal 7 directory.

### PRE-03: Target Path Accessibility & Permissions
- **Status**: {{ RES_03 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_03 }}
- **Remediation**: Verify `target.path` exists and current process has write permissions.

### PRE-04: Path Isolation & Non-Overlap
- **Status**: {{ RES_04 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_04 }}
- **Remediation**: Source and target directories must be completely separate filesystem trees.

### PRE-05: Drupal 7 Core Markers
- **Status**: {{ RES_05 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_05 }} (Expected: `includes/bootstrap.inc`, `modules/system/system.module`)
- **Remediation**: Point `source.path` to a valid Drupal 7 codebase root.

### PRE-06: Drupal 10/11 Core Markers
- **Status**: {{ RES_06 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_06 }} (Expected: `core/lib/Drupal.php` or `composer.json` containing `drupal/core`)
- **Remediation**: Point `target.path` to an initialized Drupal 10 or 11 codebase root.

### PRE-07: Target Version Alignment
- **Status**: {{ RES_07 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_07 }}
- **Remediation**: Ensure `target.drupal_version` in `migration.config.yml` matches installed target core version.

### PRE-08: Target Subdirectory Integrity
- **Status**: {{ RES_08 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_08 }}
- **Remediation**: Ensure `web/modules/custom` and `web/themes/custom` exist or target root is writable for scaffolding.

### PRE-09: Secret & Credential Scanning
- **Status**: {{ RES_09 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_09 }}
- **Remediation**: Remove plain-text passwords or secret tokens from `migration.config.yml`. Use environment variables.

### PRE-10: Configured Test Tools
- **Status**: {{ RES_10 }}
- **Evidence**: `[OBSERVED FACT]` {{ EVIDENCE_10 }}
- **Remediation**: If testing is enabled in config, verify `vendor/bin/phpunit`, `vendor/bin/phpstan`, or `vendor/bin/phpcs` exist.

---

## 4. Remediation & Next Actions

- **If Overall Result is PASS**:  
  Proceed to Discovery via `/discover` or begin orchestration via `/orchestrate`.
- **If Overall Result is BLOCKED**:  
  Resolve all failing CRITICAL / MAJOR checks above before proceeding. Re-run `/preflight` to verify remediation.
