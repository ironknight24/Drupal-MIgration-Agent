# Rule: Architectural Replacement & Behavioral Mapping

## 1. Behavioral Parity vs Literal Translation
- When legacy Drupal 7 subsystems, frameworks, or architectural patterns have been replaced by modern Drupal 10/11 architectures, the objective is **D7 behavioral equivalence using modern Symfony/Drupal paradigms**, not literal line-by-line syntax porting.
- Generic example: Legacy procedural group/community subsystem $\to$ modern entity/access architecture.

## 2. Distinction of Relationship Types from Migration Status
The engine must strictly distinguish architectural relationship classifications from migration outcome statuses:
- **Architectural Relationship Classifications**:
  `DIRECT_EQUIVALENT`, `ARCHITECTURAL_REPLACEMENT`, `PARTIAL_REPLACEMENT`, `REPLACED_BY_EXISTING_TARGET`, `SUPERSEDED`, `OBSOLETE`, `NO_REPLACEMENT_FOUND`.
- **Migration Outcome Statuses**:
  `COMPLETE`, `PARTIAL`, `MISSING`, `BLOCKED`, `HUMAN_INTERVENTION_REQUIRED`, `RUNTIME_UNVERIFIED`, `SUPERSEDED`, `REPLACED`, `OBSOLETE`, `EXCLUDED`.

## 3. Existing Target Precedence First Rule
Before scaffolding new classes or services:
1. Search existing target custom modules, core services, and contrib modules for pre-existing implementations.
2. If the target codebase already provides the behavior, mark the behavior as `REPLACED_BY_EXISTING_TARGET` or `COMPLETE` citing target file lines.
3. If partial behavior exists, extend the existing target class/service rather than creating duplicate competing classes.

## 4. Bounded Remediation & Re-Audit Cycle
- Decompose legacy code into discrete behavior units.
- Emit structured remediation tasks in `## LLM REMEDIATION INPUT` YAML format with stable task IDs.
- Re-audit remediated artifacts until all material items are complete or escalated to `HUMAN_INTERVENTION_REQUIRED`.

## 5. Reference
- Detailed specifications: [skills/d7-to-d10-mapping/SKILL.md](../../skills/d7-to-d10-mapping/SKILL.md) Section 16
