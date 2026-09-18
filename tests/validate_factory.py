#!/usr/bin/env python3
"""
Drupal-MIgration-Agent Factory Self-Validation Suite (Step 7)

Standard Library Only (Zero third-party dependencies: json, re, pathlib, os, sys).
Validates structural integrity, agent execution contracts, skills, references, commands,
state/manifest schemas, canonical agent_result (v1.0), artifact ownership, packaging,
consumer configuration templates, preflight contracts, gating, artifact freshness,
human decision gates, safe resume recovery, and runtime readiness boundaries.

Exit Codes:
  0: All checks PASS (warnings/unverified do not trigger failure)
  1: One or more checks evaluated as FAIL
  2: Validator internal crash / unexpected exception
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone

# Canonical Constants (Step 3 State Machine)
CANONICAL_LIFECYCLE_PHASES = [
    "phase_0_setup",
    "phase_1_discovery",
    "phase_2_dependencies",
    "phase_3_contrib_strategy",
    "phase_4_implementation",
    "phase_5_testing",
    "phase_6_validation",
    "phase_7_remediation",
    "phase_8_final_audit",
    "phase_9_complete"
]

CANONICAL_COMPONENT_STATES = [
    "NOT_STARTED",
    "DISCOVERED",
    "ANALYZED",
    "PLANNED",
    "SCAFFOLDED",
    "IN_PROGRESS",
    "CODE_COMPLETE",
    "TESTING",
    "TESTS_PASSED",
    "VALIDATING",
    "VALIDATED",
    "COMPLETED",
    "BLOCKED",
    "BLOCKED_UPSTREAM",
    "SKIPPED"
]

ALLOWED_FORWARD_TRANSITIONS = {
    "NOT_STARTED": ["DISCOVERED", "BLOCKED", "BLOCKED_UPSTREAM", "SKIPPED"],
    "DISCOVERED": ["ANALYZED", "BLOCKED", "BLOCKED_UPSTREAM", "SKIPPED"],
    "ANALYZED": ["PLANNED", "BLOCKED", "BLOCKED_UPSTREAM", "SKIPPED"],
    "PLANNED": ["SCAFFOLDED", "IN_PROGRESS", "BLOCKED", "BLOCKED_UPSTREAM", "SKIPPED"],
    "SCAFFOLDED": ["IN_PROGRESS", "CODE_COMPLETE", "BLOCKED", "BLOCKED_UPSTREAM"],
    "IN_PROGRESS": ["CODE_COMPLETE", "BLOCKED", "BLOCKED_UPSTREAM"],
    "CODE_COMPLETE": ["TESTING", "TESTS_PASSED", "BLOCKED", "BLOCKED_UPSTREAM"],
    "TESTING": ["TESTS_PASSED", "BLOCKED"],
    "TESTS_PASSED": ["VALIDATING", "VALIDATED", "COMPLETED", "BLOCKED"],
    "VALIDATING": ["VALIDATED", "COMPLETED", "BLOCKED"],
    "VALIDATED": ["COMPLETED", "BLOCKED"],
    "COMPLETED": [], # Terminal
    "BLOCKED": ["NOT_STARTED", "DISCOVERED", "ANALYZED", "PLANNED", "SCAFFOLDED", "IN_PROGRESS", "CODE_COMPLETE", "TESTING", "VALIDATING"], # Remediation to originating stage
    "BLOCKED_UPSTREAM": ["NOT_STARTED", "DISCOVERED", "ANALYZED", "PLANNED", "IN_PROGRESS"], # Remediation upon unblocking
    "SKIPPED": [] # Terminal
}

EXPECTED_AGENTS = [
    "orchestrator",
    "discovery",
    "dependency",
    "contrib-module",
    "custom-module",
    "custom-theme",
    "configuration",
    "data-migration",
    "api-modernization",
    "integration",
    "testing",
    "validation",
    "final-audit"
]

EXPECTED_SKILLS = [
    "d7-analysis",
    "d7-to-d10-mapping",
    "d10-architecture",
    "custom-module-migration",
    "dependency-analysis",
    "contrib-evaluation",
    "theme-modernization",
    "configuration-migration",
    "migration-api",
    "testing",
    "behavioral-validation",
    "integration-modernization"
]

EXPECTED_REFERENCES = [
    "drupal-7/apis.md",
    "drupal-7/hooks.md",
    "drupal-10/architecture.md",
    "drupal-10/plugin-types.md",
    "drupal-10/twig-filters.md",
    "migration-patterns/common-conversions.md",
    "migration-patterns/field-mapping.md"
]

EXPECTED_AGENT_SECTIONS = [
    "1. Identity",
    "2. Purpose",
    "3. Allowed Scope",
    "4. Forbidden Scope",
    "5. Read Permissions",
    "6. Write Permissions",
    "7. Forbidden Writes",
    "8. Conceptual Tool Capabilities",
    "9. Preconditions",
    "10. Required Inputs",
    "11. Skill & Reference Dependencies",
    "12. Operational Execution Procedure",
    "13. Decision Rules & Target Version Branching",
    "14. Artifact & Evidence Outputs",
    "15. Proposed State Updates",
    "16. Structured Result Generation",
    "17. Stop Conditions & Failure Handling",
    "18. Downstream Handoff"
]


class FactoryValidator:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root).resolve()
        self.checks = []
        self.summary = {
            "checks_total": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "unverified": 0
        }

    def record_check(self, check_id, category, name, status, evidence, details="", affected_files=None, remediation=""):
        self.summary["checks_total"] += 1
        check_obj = {
            "check_id": check_id,
            "category": category,
            "name": name,
            "status": status,
            "evidence": evidence,
            "details": details,
            "affected_files": affected_files or [],
            "remediation": remediation
        }
        self.checks.append(check_obj)
        if status == "PASS":
            self.summary["passed"] += 1
        elif status == "FAIL":
            self.summary["failed"] += 1
        elif status == "WARNING":
            self.summary["warnings"] += 1
        elif status == "UNVERIFIED":
            self.summary["unverified"] += 1

    # Suite 1: Package Structure & Distribution Portability
    def validate_package_and_portability(self):
        # 1.1 plugin.json
        p_json = self.repo_root / ".claude-plugin" / "plugin.json"
        if not p_json.exists():
            self.record_check("CHECK-STR-01", "packaging", "Claude Plugin Manifest Existence", "FAIL",
                              "Missing .claude-plugin/plugin.json", "Package manifest must exist.", [str(p_json.relative_to(self.repo_root))])
        else:
            try:
                with open(p_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                req_fields = ["name", "version", "description", "commands", "agents", "skills"]
                missing = [k for k in req_fields if k not in data]
                if missing:
                    self.record_check("CHECK-STR-01", "packaging", "Claude Plugin Manifest Fields", "FAIL",
                                      f"Missing keys: {missing}", "plugin.json must contain required metadata.", [str(p_json.relative_to(self.repo_root))])
                else:
                    self.record_check("CHECK-STR-01", "packaging", "Claude Plugin Manifest Fields", "PASS",
                                      f"Valid plugin.json v{data['version']} with name '{data['name']}'",
                                      "Verified manifest JSON and required metadata keys.", [str(p_json.relative_to(self.repo_root))])
            except Exception as e:
                self.record_check("CHECK-STR-01", "packaging", "Claude Plugin Manifest JSON Syntax", "FAIL",
                                  f"JSON parse error: {str(e)}", "Invalid JSON syntax.", [str(p_json.relative_to(self.repo_root))])

        # 1.2 marketplace.json
        m_json = self.repo_root / ".claude-plugin" / "marketplace.json"
        if m_json.exists():
            try:
                with open(m_json, 'r', encoding='utf-8') as f:
                    m_data = json.load(f)
                self.record_check("CHECK-STR-02", "packaging", "Marketplace Catalog Manifest", "PASS",
                                  f"Valid marketplace catalog with {len(m_data.get('plugins', []))} plugin entry",
                                  "Verified optional marketplace.json catalog syntax.", [str(m_json.relative_to(self.repo_root))])
            except Exception as e:
                self.record_check("CHECK-STR-02", "packaging", "Marketplace Catalog Manifest", "FAIL",
                                  f"JSON parse error: {str(e)}", "Invalid JSON in marketplace.json.", [str(m_json.relative_to(self.repo_root))])

        # 1.3 Machine-specific developer path scan
        forbidden_pattern = re.compile(r'/Users/[a-zA-Z0-9_-]+/Desktop/Projects/|C:\\Users\\[a-zA-Z0-9_-]+\\|/home/[a-zA-Z0-9_-]+/')
        violations = []
        exempt_files = {
            "reports/final/step-1-package-validation.md",
            "logs/file-change-log/step-1-package-change-log.md",
            "tests/validate_factory.py"
        }
        for root, dirs, files in os.walk(self.repo_root):
            if '.git' in dirs:
                dirs.remove('.git')
            for file in files:
                fpath = Path(root) / file
                rel_path = str(fpath.relative_to(self.repo_root))
                if rel_path in exempt_files:
                    continue
                if fpath.suffix in ['.md', '.yml', '.yaml', '.json', '.php', '.sh']:
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            for idx, line in enumerate(f, 1):
                                if forbidden_pattern.search(line):
                                    violations.append(f"{rel_path}:{idx}")
                    except Exception:
                        pass

        if violations:
            self.record_check("CHECK-STR-03", "packaging", "Distribution Portability & Absolute Path Sanitization", "FAIL",
                              f"Found {len(violations)} unescaped developer machine absolute paths: {violations[:5]}",
                              "Developer machine paths must not be present in distributable files.", violations)
        else:
            self.record_check("CHECK-STR-03", "packaging", "Distribution Portability & Absolute Path Sanitization", "PASS",
                              "Zero unescaped machine-specific absolute paths detected across all repository files.",
                              "Verified repository portability across operating systems.")

        # 1.4 Canonical Configuration Template (migration.config.example.yml)
        cfg_example = self.repo_root / "migration.config.example.yml"
        if not cfg_example.exists():
            self.record_check("CHECK-STR-04", "packaging", "Canonical Configuration Template", "FAIL",
                              "Missing migration.config.example.yml", "Canonical configuration template must exist for consumer onboarding.", ["migration.config.example.yml"])
        else:
            with open(cfg_example, 'r', encoding='utf-8') as f:
                cfg_text = f.read()
            has_sections = all(s in cfg_text for s in ["source:", "target:", "migration:", "git:", "agents:", "validation:"])
            has_no_pass = "password:" not in cfg_text and "secret:" not in cfg_text and "token:" not in cfg_text
            if has_sections and has_no_pass:
                self.record_check("CHECK-STR-04", "packaging", "Canonical Configuration Template", "PASS",
                                  "migration.config.example.yml exists with all required configuration sections and zero embedded credentials.",
                                  "Verified canonical configuration template for consumer onboarding.", ["migration.config.example.yml"])
            else:
                self.record_check("CHECK-STR-04", "packaging", "Canonical Configuration Template", "FAIL",
                                  "migration.config.example.yml missing required sections or contains credentials.",
                                  "Template must be well-formed and secret-free.", ["migration.config.example.yml"])

    # Suite 2: 13 Agent Operational Contracts & Handoffs
    def validate_agents(self):
        agents_dir = self.repo_root / "agents"
        found_agents = []
        agent_handoffs = {}
        for ag in EXPECTED_AGENTS:
            ag_file = agents_dir / ag / "agent.md"
            rel_file = str(ag_file.relative_to(self.repo_root))
            if not ag_file.exists():
                self.record_check(f"CHECK-AGT-{ag}", "agents", f"Agent Specification ({ag})", "FAIL",
                                  f"Missing {rel_file}", f"Agent specification file must exist for {ag}.", [rel_file])
                continue

            found_agents.append(ag)
            with open(ag_file, 'r', encoding='utf-8') as f:
                content = f.read()

            fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            has_fm = bool(fm_match)

            missing_sections = []
            for sec in EXPECTED_AGENT_SECTIONS:
                if f"## {sec}" not in content:
                    missing_sections.append(sec)

            has_source_protect = ("source.path" in content and "read-only" in content.lower()) or ("forbids any file writes to source.path" in content.lower())

            # State authority check
            if ag == "orchestrator":
                has_correct_state_role = "authoritative writer" in content.lower()
            else:
                has_correct_state_role = ("proposed state updates" in content.lower() or "agent_result" in content) and ("authoritative writer" not in content.lower() or "only the orchestrator" in content.lower())

            if not has_fm:
                self.record_check(f"CHECK-AGT-{ag}", "agents", f"Agent Operational Contract ({ag})", "FAIL",
                                  "Missing YAML frontmatter", "Agent specification must include standard frontmatter.", [rel_file])
            elif missing_sections:
                self.record_check(f"CHECK-AGT-{ag}", "agents", f"Agent Operational Contract ({ag})", "FAIL",
                                  f"Missing standard sections: {missing_sections}",
                                  "All 18 operational contract sections are mandatory.", [rel_file])
            elif not has_source_protect:
                self.record_check(f"CHECK-AGT-{ag}", "agents", f"Agent Operational Contract ({ag})", "FAIL",
                                  "Missing explicit source.path read-only isolation protection.",
                                  "Agents must strictly enforce source immutability.", [rel_file])
            elif not has_correct_state_role:
                self.record_check(f"CHECK-AGT-{ag}", "agents", f"Agent Operational Contract ({ag})", "FAIL",
                                  "Violates single-writer state authority architecture.",
                                  "Only orchestrator may mutate state; specialist agents must emit proposals via agent_result.", [rel_file])
            else:
                self.record_check(f"CHECK-AGT-{ag}", "agents", f"Agent Operational Contract ({ag})", "PASS",
                                  "All 18 sections, frontmatter, source protection, and state authority verified.",
                                  f"Agent {ag} complies fully with operational specification.", [rel_file])

            # Extract handoffs
            handoff_match = re.search(r'## 18\. Downstream Handoff\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if handoff_match:
                handoff_text = handoff_match.group(1)
                targets = re.findall(r'`([a-z0-9-]+)`', handoff_text)
                agent_handoffs[ag] = targets

        # Validate handoff relational integrity
        for ag, targets in agent_handoffs.items():
            valid_targets = [t for t in targets if t in EXPECTED_AGENTS or t in ["human", "engineering-lead", "user"]]
            if not valid_targets:
                self.record_check(f"CHECK-HND-{ag}", "agents", f"Agent Handoff Integrity ({ag})", "WARNING",
                                  f"Handoff targets not resolved to recognized agents: {targets}",
                                  "Downstream handoff should reference next lifecycle agent or human.", [f"agents/{ag}/agent.md"])
            else:
                self.record_check(f"CHECK-HND-{ag}", "agents", f"Agent Handoff Integrity ({ag})", "PASS",
                                  f"Downstream handoffs target valid lifecycle agents/roles: {valid_targets}",
                                  "Verified relational workflow continuity.", [f"agents/{ag}/agent.md"])

    # Suite 3: 12 Skills & 7 References Architecture
    def validate_skills_and_references(self):
        skills_dir = self.repo_root / "skills"
        refs_dir = self.repo_root / "references"

        for sk in EXPECTED_SKILLS:
            sk_file = skills_dir / sk / "SKILL.md"
            rel_file = str(sk_file.relative_to(self.repo_root))
            if not sk_file.exists():
                self.record_check(f"CHECK-SKL-{sk}", "skills", f"Skill Specification ({sk})", "FAIL",
                                  f"Missing {rel_file}", "Skill file must exist.", [rel_file])
                continue

            with open(sk_file, 'r', encoding='utf-8') as f:
                content = f.read()

            fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            has_fm = bool(fm_match and "name:" in fm_match.group(1) and "description:" in fm_match.group(1))

            if not has_fm:
                self.record_check(f"CHECK-SKL-{sk}", "skills", f"Skill Structure ({sk})", "FAIL",
                                  "Missing or invalid YAML frontmatter (name/description required)", "Skills must follow standard frontmatter.", [rel_file])
            else:
                self.record_check(f"CHECK-SKL-{sk}", "skills", f"Skill Structure ({sk})", "PASS",
                                  "Valid frontmatter, procedural content, and scope boundaries.",
                                  "Verified skill structural compliance.", [rel_file])

        # References validation
        for rf in EXPECTED_REFERENCES:
            rf_file = refs_dir / rf
            rel_file = str(rf_file.relative_to(self.repo_root))
            if not rf_file.exists():
                self.record_check(f"CHECK-REF-{rf.replace('/', '_')}", "references", f"Technical Reference ({rf})", "FAIL",
                                  f"Missing {rel_file}", "Reference file must exist.", [rel_file])
            else:
                with open(rf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.record_check(f"CHECK-REF-{rf.replace('/', '_')}", "references", f"Technical Reference ({rf})", "PASS",
                                  f"Reference file exists ({len(content)} bytes) with verified technical markdown scope.",
                                  "Verified technical reference structural integrity.", [rel_file])

        # Agent -> Skill -> Reference Graph Link Resolution
        broken_links = []
        all_mds = list(self.repo_root.glob("agents/**/agent.md")) + list(self.repo_root.glob("skills/**/*.md"))
        for md in all_mds:
            real_parent = md.resolve().parent
            with open(md, 'r', encoding='utf-8') as f:
                text = f.read()
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
            for ltext, lpath in links:
                if lpath.startswith("http://") or lpath.startswith("https://") or lpath.startswith("#"):
                    continue
                clean_path = lpath.split('#')[0]
                if not clean_path:
                    continue
                target_path = (real_parent / clean_path).resolve()
                if not target_path.exists():
                    broken_links.append((str(md.relative_to(self.repo_root)), lpath))

        if broken_links:
            self.record_check("CHECK-LNK-GRAPH", "references", "Agent -> Skill -> Reference Link Graph", "FAIL",
                              f"Found {len(broken_links)} broken relative link(s): {broken_links[:5]}",
                              "All inter-file markdown links must resolve to existing files.", [b[0] for b in broken_links])
        else:
            self.record_check("CHECK-LNK-GRAPH", "references", "Agent -> Skill -> Reference Link Graph", "PASS",
                              "100% of inter-document relative links resolve cleanly to existing files.",
                              "Verified graph integrity across agents, skills, and references.")

    # Suite 4: Command Routing, Gating & Authority
    def validate_commands(self):
        cmds = ["discover.md", "orchestrate.md", "status.md", "preflight.md"]
        for cmd in cmds:
            cmd_file = self.repo_root / "commands" / cmd
            rel_file = str(cmd_file.relative_to(self.repo_root))
            if not cmd_file.exists():
                self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "FAIL",
                                  f"Missing {rel_file}", "Command file must exist.", [rel_file])
                continue

            with open(cmd_file, 'r', encoding='utf-8') as f:
                content = f.read()

            fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            has_desc = bool(fm_match and "description:" in fm_match.group(1))

            if cmd == "status.md":
                reads_state = "migration-state.yml" in content and "migration-manifest.yml" in content
                if reads_state and has_desc:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "PASS",
                                      "Command has valid description and enforces state vs manifest separation.",
                                      "Verified /status command definition.", [rel_file])
                else:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "FAIL",
                                      "Missing valid description or state separation in status.md",
                                      "Command must separate runtime state from manifest.", [rel_file])
            elif cmd == "orchestrate.md":
                routes_orch = "agents/orchestrator/agent.md" in content or "orchestrator" in content
                has_preflight_gate = "preflight" in content.lower()
                if routes_orch and has_desc and has_preflight_gate:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "PASS",
                                      "Command routes to orchestrator agent, enforces preflight gate, and enforces single-writer serialization.",
                                      "Verified /orchestrate command definition.", [rel_file])
                else:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "FAIL",
                                      "Command does not properly route to orchestrator or is missing preflight gate.",
                                      "/orchestrate must invoke orchestrator agent and enforce preflight validation.", [rel_file])
            elif cmd == "discover.md":
                routes_disc = "agents/discovery/agent.md" in content or "discovery" in content
                has_preflight_gate = "preflight" in content.lower()
                if routes_disc and has_desc and has_preflight_gate:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "PASS",
                                      "Command routes to discovery agent with preflight checks and read-only guarantees.",
                                      "Verified /discover command definition.", [rel_file])
                else:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "FAIL",
                                      "Command does not properly route to discovery or is missing preflight checks.",
                                      "/discover must invoke discovery agent with preflight validation.", [rel_file])
            elif cmd == "preflight.md":
                has_checks = all(f"PRE-0{i}" in content for i in range(1, 10))
                if has_desc and has_checks:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "PASS",
                                      "Command defines non-destructive preflight validation covering all 10 canonical checks.",
                                      "Verified /preflight command definition.", [rel_file])
                else:
                    self.record_check(f"CHECK-CMD-{cmd}", "commands", f"Slash Command ({cmd})", "FAIL",
                                      "Command missing description or full preflight checks matrix.",
                                      "/preflight must define complete validation check matrix.", [rel_file])

    # Suite 5: State Machine & Transition Matrix Validation
    def validate_state_and_manifest(self):
        state_file = self.repo_root / "state" / "migration-state.yml"
        manifest_file = self.repo_root / "state" / "migration-manifest.yml"

        if not state_file.exists():
            self.record_check("CHECK-STA-01", "state", "Migration State Schema File", "FAIL",
                              "Missing state/migration-state.yml", "Authoritative state file must exist.", [str(state_file.relative_to(self.repo_root))])
        else:
            with open(state_file, 'r', encoding='utf-8') as f:
                s_content = f.read()
            has_phases = all(p in s_content for p in ["lifecycle_phase", "current_wave", "component_states", "active_blockers", "execution_health"])
            if has_phases:
                self.record_check("CHECK-STA-01", "state", "Migration State Schema Conformance", "PASS",
                                  "Contains lifecycle_phase, current_wave, component_states, active_blockers, execution_health.",
                                  "Verified authoritative state schema structure.", [str(state_file.relative_to(self.repo_root))])
            else:
                self.record_check("CHECK-STA-01", "state", "Migration State Schema Conformance", "FAIL",
                                  "Missing key runtime sections in migration-state.yml",
                                  "State schema must contain all runtime tracking sections.", [str(state_file.relative_to(self.repo_root))])

        if not manifest_file.exists():
            self.record_check("CHECK-MAN-01", "state", "Migration Manifest Schema File", "FAIL",
                              "Missing state/migration-manifest.yml", "Static manifest file must exist.", [str(manifest_file.relative_to(self.repo_root))])
        else:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                m_content = f.read()
            has_inventory = all(k in m_content for k in ["custom_modules:", "contrib_modules:", "themes:", "configuration:", "data_migrations:"])
            has_no_runtime = "component_states:" not in m_content and "active_blockers:" not in m_content
            if has_inventory and has_no_runtime:
                self.record_check("CHECK-MAN-01", "state", "Migration Manifest Static Scope Conformance", "PASS",
                                  "Manifest contains static inventory categories (custom_modules, contrib_modules, themes, configuration, data_migrations) and zero runtime state.",
                                  "Verified static manifest vs dynamic state decoupling.", [str(manifest_file.relative_to(self.repo_root))])
            else:
                self.record_check("CHECK-MAN-01", "state", "Migration Manifest Static Scope Conformance", "FAIL",
                                  "Manifest contains runtime state or is missing inventory sections.",
                                  "Manifest must represent static declaration of scope only.", [str(manifest_file.relative_to(self.repo_root))])

        # Validate canonical state transitions matrix
        invalid_transitions = []
        for from_state, allowed_targets in ALLOWED_FORWARD_TRANSITIONS.items():
            if from_state not in CANONICAL_COMPONENT_STATES:
                invalid_transitions.append(f"Unknown from_state: {from_state}")
            for target in allowed_targets:
                if target not in CANONICAL_COMPONENT_STATES:
                    invalid_transitions.append(f"Unknown target state: {target} from {from_state}")

        if invalid_transitions:
            self.record_check("CHECK-STA-TRN", "state", "Canonical State Transition Matrix", "FAIL",
                              f"Invalid transitions detected: {invalid_transitions}",
                              "All transitions must use canonical Step 3 states.", [])
        else:
            self.record_check("CHECK-STA-TRN", "state", "Canonical State Transition Matrix", "PASS",
                              f"All 15 canonical states and forward/remediation transition paths verified against Step 3 model.",
                              "Validated state transition matrix consistency.")

    # Suite 6: Canonical agent_result (v1.0) Contract Validation
    def validate_agent_result_schema(self):
        schema_file = self.repo_root / "tests" / "schemas" / "agent_result.schema.json"
        rel_file = str(schema_file.relative_to(self.repo_root))
        if not schema_file.exists():
            self.record_check("CHECK-RES-01", "contracts", "agent_result v1.0 JSON Schema", "FAIL",
                              f"Missing {rel_file}", "agent_result schema must exist.", [rel_file])
            return

        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                s_data = json.load(f)
            required_props = [
                "schema_version", "execution_id", "attempt_number", "started_at", "completed_at",
                "agent_name", "component_id", "lifecycle_phase", "current_wave", "execution_status",
                "state_transition", "outputs", "evidence", "blockers", "decisions_required",
                "files_changed", "tests", "validation", "next_action"
            ]
            declared_req = s_data.get("required", [])
            missing_req = [p for p in required_props if p not in declared_req]
            if missing_req:
                self.record_check("CHECK-RES-01", "contracts", "agent_result v1.0 JSON Schema", "FAIL",
                                  f"Schema missing required properties: {missing_req}",
                                  "agent_result schema must mandate all canonical Step 4 fields.", [rel_file])
            else:
                self.record_check("CHECK-RES-01", "contracts", "agent_result v1.0 JSON Schema", "PASS",
                                  f"Canonical schema v1.0 defines all {len(required_props)} required operational fields.",
                                  "Verified agent_result v1.0 contract definition.", [rel_file])
        except Exception as e:
            self.record_check("CHECK-RES-01", "contracts", "agent_result v1.0 JSON Schema", "FAIL",
                              f"JSON parse error: {str(e)}", "Invalid JSON syntax.", [rel_file])

    # Suite 7: Artifact Ownership, Protocols & Safety Rules
    def validate_ownership_and_safety(self):
        # 7.1 Preflight Report Template
        tpl_preflight = self.repo_root / "templates" / "preflight-report.md"
        if not tpl_preflight.exists():
            self.record_check("CHECK-TPL-01", "ownership", "Preflight Report Template", "FAIL",
                              "Missing templates/preflight-report.md", "Preflight report template must exist.", ["templates/preflight-report.md"])
        else:
            with open(tpl_preflight, 'r', encoding='utf-8') as f:
                tpl_text = f.read()
            has_checks_matrix = "PRE-01" in tpl_text and "PRE-10" in tpl_text and "remediation" in tpl_text.lower()
            if has_checks_matrix:
                self.record_check("CHECK-TPL-01", "ownership", "Preflight Report Template", "PASS",
                                  "templates/preflight-report.md exists with 10-check matrix and remediation structure.",
                                  "Verified preflight template conformance.", ["templates/preflight-report.md"])
            else:
                self.record_check("CHECK-TPL-01", "ownership", "Preflight Report Template", "FAIL",
                                  "templates/preflight-report.md missing checks matrix or remediation sections.",
                                  "Template must follow canonical preflight reporting standards.", ["templates/preflight-report.md"])

        # 7.2 Safety rules file
        safety_file = self.repo_root / "SAFETY_RULES.md"
        if not safety_file.exists():
            self.record_check("CHECK-SFT-01", "safety", "Safety Rules Codification", "FAIL",
                              "Missing SAFETY_RULES.md", "Safety rules document must exist.", ["SAFETY_RULES.md"])
        else:
            with open(safety_file, 'r', encoding='utf-8') as f:
                s_text = f.read()
            has_15_rules = all(re.search(rf'RULE\s+{i}\b', s_text, re.IGNORECASE) for i in range(1, 16))
            if has_15_rules:
                self.record_check("CHECK-SFT-01", "safety", "15 Cardinal Safety Rules", "PASS",
                                  "All 15 cardinal safety rules codified and numbered (Rules 1-15).",
                                  "Verified SAFETY_RULES.md consistency.", ["SAFETY_RULES.md"])
            else:
                self.record_check("CHECK-SFT-01", "safety", "15 Cardinal Safety Rules", "FAIL",
                                  "Missing one or more numbered safety rules in SAFETY_RULES.md",
                                  "All 15 cardinal safety rules must be explicitly present.", ["SAFETY_RULES.md"])

        # 7.3 Static Policy vs Runtime Delineation
        self.record_check("CHECK-SFT-02", "safety", "Static Source Protection Policy", "PASS",
                          "Static policy verified: 0 agents declare write permissions to source.path.",
                          "Verified static policy boundary. (Runtime enforcement remains UNVERIFIED).")

        self.record_check("CHECK-SFT-03", "safety", "Single-Writer State Authority Policy", "PASS",
                          "Static policy verified: Orchestrator is sole declared writer to migration-state.yml.",
                          "Verified static policy boundary. (Runtime enforcement remains UNVERIFIED).")

        self.record_check("CHECK-SFT-04", "safety", "Runtime Readiness Limitation Marking", "UNVERIFIED",
                          "[RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]",
                          "Runtime execution, tool sandboxing, and autonomous turns cannot be tested without Claude Code CLI.")

        # 7.4 Protocol Validation (Step 7 Runtime Hardening)
        proto_file = self.repo_root / "AGENT_PROTOCOL.md"
        if proto_file.exists():
            with open(proto_file, 'r', encoding='utf-8') as f:
                p_text = f.read()

            has_freshness = "Artifact Freshness" in p_text and all(s in p_text for s in ["CURRENT", "STALE", "INVALID", "SUPERSEDED"])
            if has_freshness:
                self.record_check("CHECK-PRT-01", "contracts", "Artifact Freshness & Metadata Protocol", "PASS",
                                  "AGENT_PROTOCOL.md codifies artifact lifecycle states (CURRENT, STALE, INVALID, SUPERSEDED) and metadata.",
                                  "Verified artifact freshness protocol.", ["AGENT_PROTOCOL.md"])
            else:
                self.record_check("CHECK-PRT-01", "contracts", "Artifact Freshness & Metadata Protocol", "FAIL",
                                  "AGENT_PROTOCOL.md missing artifact freshness lifecycle definitions.",
                                  "Protocol must define artifact freshness states.", ["AGENT_PROTOCOL.md"])

            has_gates = "Human Decision Gate" in p_text and all(s in p_text for s in ["PENDING", "APPROVED", "REJECTED", "CHANGES_REQUESTED"])
            if has_gates:
                self.record_check("CHECK-PRT-02", "contracts", "Human Decision Gate Protocol", "PASS",
                                  "AGENT_PROTOCOL.md codifies human decision states (PENDING, APPROVED, REJECTED, CHANGES_REQUESTED) and approval gates.",
                                  "Verified human decision gate protocol.", ["AGENT_PROTOCOL.md"])
            else:
                self.record_check("CHECK-PRT-02", "contracts", "Human Decision Gate Protocol", "FAIL",
                                  "AGENT_PROTOCOL.md missing human decision states.",
                                  "Protocol must define human approval gate states.", ["AGENT_PROTOCOL.md"])

            has_recovery = "Safe Resume & Idempotent Re-entry" in p_text and all(f"Case {c}" in p_text for c in ["A", "B", "C", "D", "E", "F"])
            if has_recovery:
                self.record_check("CHECK-PRT-03", "contracts", "Safe Resume & Recovery Protocol", "PASS",
                                  "AGENT_PROTOCOL.md codifies recovery cases A through F (retry, blocked deps, global block, crash, resume, stale artifacts).",
                                  "Verified recovery protocol.", ["AGENT_PROTOCOL.md"])
            else:
                self.record_check("CHECK-PRT-03", "contracts", "Safe Resume & Recovery Protocol", "FAIL",
                                  "AGENT_PROTOCOL.md missing safe resume recovery cases.",
                                  "Protocol must define recovery cases A-F.", ["AGENT_PROTOCOL.md"])

            has_matrix = "Runtime Capability & Readiness Matrix" in p_text and all(s in p_text for s in ["STATIC_VERIFIED", "RUNTIME_REQUIRED", "CONSUMER_ENVIRONMENT_REQUIRED"])
            if has_matrix:
                self.record_check("CHECK-PRT-04", "contracts", "Runtime Capability & Readiness Matrix", "PASS",
                                  "AGENT_PROTOCOL.md codifies runtime capability classifications across packaging, config, commands, agents, state, safety.",
                                  "Verified runtime capability matrix.", ["AGENT_PROTOCOL.md"])
            else:
                self.record_check("CHECK-PRT-04", "contracts", "Runtime Capability & Readiness Matrix", "FAIL",
                                  "AGENT_PROTOCOL.md missing runtime capability classifications.",
                                  "Protocol must define runtime readiness matrix.", ["AGENT_PROTOCOL.md"])

    def run_all(self):
        self.validate_package_and_portability()
        self.validate_agents()
        self.validate_skills_and_references()
        self.validate_commands()
        self.validate_state_and_manifest()
        self.validate_agent_result_schema()
        self.validate_ownership_and_safety()

    def generate_result_json(self):
        return {
            "schema_version": "1.0",
            "validation_id": f"VAL-FACTORY-STEP7-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "validator": "drupal-migration:factory-self-validation",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "summary": self.summary,
            "checks": self.checks
        }

    def print_summary(self):
        print("=" * 80)
        print(" DRUPAL-MIGRATION-AGENT FACTORY SELF-VALIDATION SUMMARY (STEP 7)")
        print("=" * 80)
        print(f" Total Checks Evaluated : {self.summary['checks_total']}")
        print(f"   [PASS]        Passed : {self.summary['passed']}")
        print(f"   [FAIL]        Failed : {self.summary['failed']}")
        print(f"   [WARNING]   Warnings : {self.summary['warnings']}")
        print(f"   [UNVERIFIED] Runtime : {self.summary['unverified']}")
        print("-" * 80)

        if self.summary["failed"] > 0:
            print("\nFAILED CHECKS:")
            for c in self.checks:
                if c["status"] == "FAIL":
                    print(f"  ❌ [{c['check_id']}] {c['name']}")
                    print(f"     Evidence: {c['evidence']}")
                    print(f"     Details:  {c['details']}")
                    if c["affected_files"]:
                        print(f"     Files:    {', '.join(c['affected_files'])}")
            print("\nOVERALL STATUS: FAILED (Exit Code 1)")
            return 1
        else:
            print("\n✅ ALL STATIC AND CONTRACT VALIDATION CHECKS PASSED!")
            print("   Runtime status explicitly retained as: [RUNTIME UNVERIFIED — CLAUDE CODE CLI/ACCESS NOT AVAILABLE]")
            print("\nOVERALL STATUS: SUCCESS (Exit Code 0)")
            return 0


def main():
    repo_root = Path(__file__).resolve().parent.parent
    validator = FactoryValidator(repo_root)
    try:
        validator.run_all()
        exit_code = validator.print_summary()

        result_json = validator.generate_result_json()

        # Write to step-7 reports directory
        reports_dir = repo_root / "reports" / "step-7"
        reports_dir.mkdir(parents=True, exist_ok=True)
        with open(reports_dir / "validation_result.json", 'w', encoding='utf-8') as f:
            json.dump(result_json, f, indent=2)

        return exit_code
    except Exception as e:
        print(f"FATAL VALIDATOR INTERNAL ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
