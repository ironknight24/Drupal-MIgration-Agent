# Claude Code Packaging & Distribution Specification

## 1. Overview & Architectural Standards

This document specifies the packaging conventions, discovery mechanics, and distribution workflows used by the **Drupal Migration Agent Framework** (`drupal-migration-agent`).

The packaging adheres strictly to the official Anthropic Claude Code specifications and the open Agent Skills standard (`agentskills.io`).

---

## 2. Component Taxonomy in Claude Code

Claude Code organizes extensible functionality into three distinct building blocks:

| Component | Responsibility | Directory Location | Primary Manifest / Schema |
|:---|:---|:---|:---|
| **Plugin** | The distributable container bundling agents, skills, commands, and hooks. | Repository Root | `.claude-plugin/plugin.json` |
| **Agent** | Autonomous specialized worker defining execution workflow, inputs, outputs, and safety guardrails. | `agents/` | Markdown with YAML frontmatter (`name`, `description`, `model`) |
| **Skill** | Contextual domain knowledge playbook teaching Claude specific patterns and heuristics. | `skills/<skill-name>/` | `SKILL.md` with YAML frontmatter (`name`, `description`, `user-invocable`) |
| **Command** | User-facing interactive entry points executed via `/` prefix. | `commands/` | Markdown files (`commands/<command>.md`) |

---

## 3. Manifest Schemas

### Plugin Manifest (`.claude-plugin/plugin.json`)
The plugin manifest marks the root of the plugin and declares package metadata:

```json
{
  "name": "drupal-migration-agent",
  "version": "1.0.0",
  "description": "AI-assisted Drupal 7 to Drupal 10/11 migration agent framework.",
  "author": {
    "name": "Drupal Migration Agent Team"
  },
  "repository": "https://github.com/ironknight24/Drupal-MIgration-Agent",
  "license": "MIT",
  "keywords": ["drupal", "migration", "drupal7", "drupal10"],
  "commands": [
    "./commands/discover.md",
    "./commands/orchestrate.md",
    "./commands/preflight.md",
    "./commands/status.md"
  ],
  "agents": [
    "./agents/api-modernization.md",
    "./agents/configuration.md",
    "./agents/contrib-module.md",
    "./agents/custom-module.md",
    "./agents/custom-theme.md",
    "./agents/data-migration.md",
    "./agents/dependency.md",
    "./agents/discovery.md",
    "./agents/final-audit.md",
    "./agents/integration.md",
    "./agents/orchestrator.md",
    "./agents/testing.md",
    "./agents/validation.md"
  ],
  "skills": [
    "./skills/behavioral-validation",
    "./skills/configuration-migration",
    "./skills/contrib-evaluation",
    "./skills/custom-module-migration",
    "./skills/d10-architecture",
    "./skills/d7-analysis",
    "./skills/d7-to-d10-mapping",
    "./skills/dependency-analysis",
    "./skills/integration-modernization",
    "./skills/migration-api",
    "./skills/testing",
    "./skills/theme-modernization"
  ]
}
```

### Marketplace Manifest (`.claude-plugin/marketplace.json`)
When distributing through Claude Code's marketplace mechanism, `marketplace.json` catalogues installable plugins:

```json
{
  "name": "drupal-migration-marketplace",
  "owner": {
    "name": "Drupal Migration Agent Team"
  },
  "metadata": {
    "description": "Marketplace catalog for Drupal migration plugins",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "drupal-migration-agent",
      "source": "./",
      "description": "Full Drupal 7 to Drupal 10/11 migration framework.",
      "version": "1.0.0",
      "author": { "name": "Drupal Migration Agent Team" },
      "license": "MIT"
    }
  ]
}
```

---

## 4. Discovery & Namespacing Rules

1. **Auto-Discovery**:
   - Claude Code automatically scans `agents/` for agent definitions.
   - Claude Code automatically scans `skills/` for subdirectories containing `SKILL.md`.
   - Claude Code automatically scans `commands/` for slash command definitions.
2. **Command Namespacing**:
   - Commands are namespaced by the plugin name: `/drupal-migration-agent:orchestrate`.
   - In single-plugin environments or when no collisions exist, short aliases (e.g. `/orchestrate`) are available.
3. **Agent Namespacing**:
   - Agents are namespaced as `drupal-migration:<agent-name>`.

---

## 5. Installation & Execution Workflows

### Option 1: Local Development Installation
For development, local testing, or manual execution, launch Claude Code with the `--plugin-dir` flag:

```bash
claude --plugin-dir /path/to/Drupal-MIgration-Agent
```

- In this mode, the local directory takes precedence over marketplace installs.
- To reload modifications during an active session, use `/reload-plugins`.

### Option 2: Direct GitHub Installation
Users can install the package directly from GitHub:

```bash
/plugin install ironknight24/Drupal-MIgration-Agent
```

### Option 3: Marketplace Installation (Optional)
If registering via the catalog:

```bash
# 1. Register the marketplace
/plugin marketplace add ironknight24/Drupal-MIgration-Agent

# 2. Install the plugin
/plugin install drupal-migration-agent@drupal-migration-marketplace
```

---

## 6. Project-Scoped vs. User-Scoped Execution

- **Globally Reusable**: The plugin package (`Drupal-MIgration-Agent`) contains only generic intelligence, agent workflows, and migration skills. It contains zero customer code or hardcoded paths.
- **Project-Scoped Runtime**: When a user runs Claude Code inside an actual Drupal migration project workspace, Claude Code consumes the global/installed plugin while reading the local project's `migration.config.yml` and generating project-specific reports in `reports/`.
