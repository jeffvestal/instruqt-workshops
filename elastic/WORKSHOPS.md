# Workshops in This Repo

This repo contains multiple Instruqt workshops under `elastic/`. Each top-level directory corresponds to a workshop (or a workshop's working codename). This file explains what's what.

## Directory Structure

```
elastic/
├── WORKSHOPS.md                                          # This file
├── elastic-ai-agents-tools-agents-mcp--9-2-0--snap/      # Workshop 1: AI Agents (production)
│   ├── 01-overview/
│   ├── 02-setup/
│   ├── 03-onechat-tools-ui/
│   ├── 04-tool-ui/
│   ├── 05-esql-refresher/
│   ├── 06-apis/
│   ├── 07-mcp-client/
│   ├── 08-feedback/
│   ├── assets/
│   └── track.yml
└── dr-rangelove-stove-store/                             # Workshop 2: Workflows & Agents
    ├── README.md, INSTRUQT_REFERENCE.md, etc.            # Supporting docs
    ├── instruqt/                                         # Production track (slug: workflows-agents-alerts)
    │   ├── 01-01-intro/ ... 09-09-workflows-summary/
    │   ├── assets/, config.yml, track.yml, track_scripts/
    └── dr-rangelove-stove-store/                         # Dev/staging track (slug: dr-rangelove-stove-store)
        ├── 01-01-intro/ ... 09-09-workflows-summary/
        ├── assets/, config.yml, track.yml, track_scripts/
```

---

## Workshop 1: Elastic Agent Builder - Chat, Tools, Agents, and MCP

| Field | Value |
|---|---|
| Directory | `elastic-ai-agents-tools-agents-mcp--9-2-0--snap/` |
| Instruqt Slug | `elastic-ai-agents-tools-agents-mcp--9-2-0--snap` |
| Track ID | `hqcegji4bh0y` |
| Title | Elastic Agent Builder - Chat, Tools, Agents, and MCP |
| Sandbox Preset | `managed-vm-elastic-9-2-0-snapshot-dev` |
| Instruqt URL | https://play.instruqt.com/manage/elastic/tracks/elastic-ai-agents-tools-agents-mcp--9-2-0--snap |

### Challenges (8)

1. **Elastic AI Agents - Tools, Agents, and MCP** -- Intro presentation and MCP overview
2. **Chat Setup** -- Configure LLM connector for Elastic Chat
3. **Create a New Tool** -- Build a custom ES|QL tool in the UI
4. **Create a New Agent** -- Build a Financial Manager agent with tools
5. **A Quick Refresher on ES|QL** -- ES|QL basics, date math, LOOKUP JOIN, query parameters
6. **Exploring the Agentic APIs** -- Tools API, Agents API, Converse API
7. **Connecting to Elastic Agent with an MCP Client** -- Simple MCP Client setup and chat
8. **Feedback** -- Workshop feedback form

### History

Originally developed under the codename **johnnyrazorstotallynormalcandystore** (a Bob's Burgers reference). That directory was deleted in Feb 2026 after confirming it was a stale copy superseded by the current directory.

---

## Workshop 2: From Findings to Outcomes - Elastic Workflows & Agents

| Field | Value |
|---|---|
| Directory | `dr-rangelove-stove-store/` |
| Production Instruqt Slug | `workflows-agents-alerts` (in `instruqt/` subdirectory) |
| Production Track ID | `tvu7yvg32vsk` |
| Dev/Staging Slug | `dr-rangelove-stove-store` (in `dr-rangelove-stove-store/` subdirectory) |
| Dev/Staging Track ID | `bmusmpbufrmz` |
| Title | From Findings to Outcomes: Automating with Elastic Workflows & Agents |

### Challenges (9)

1. **The "Why": From Findings to Outcomes** -- Intro to the Two-Vendor Problem
2. **Building Your First Workflow** -- YAML workflow structure, inputs, console steps
3. **Chaining Steps** -- HTTP steps, Liquid templating, data transformation
4. **Making it Robust** -- Retry logic, conditional branching, error handling
5. **The AI "Assembly Line"** -- Multi-agent orchestration (generator-critic-remediator)
6. **The "Full Circle": AI Agent Tools** -- Workflow-as-tool pattern, SRE Triage Bot
7. **Self-Healing AI** -- Alert-triggered automation with AI analysis and remediation
8. **Capstone: Business Impact Detection** -- ES|QL + AI + deterministic logic
9. **Workflows Summary** -- Recap

### Directory Layout

This workshop has two Instruqt track copies inside it (both with the same 9 challenges but different content versions):

- **`instruqt/`** -- The production track pushed to Instruqt (slug: `workflows-agents-alerts`)
- **`dr-rangelove-stove-store/`** -- A dev/staging copy (slug: `dr-rangelove-stove-store`)

The top-level `dr-rangelove-stove-store/` directory also contains supporting documentation (README, reference guides, marketing copy, etc.) that is not part of the Instruqt track itself.

### History

"Dr. Rangelove's Stove Store" is a Bob's Burgers codename used during development.

---

## Instruqt Push Workflow

To push a track to Instruqt, `cd` into the directory that contains `track.yml` and run `instruqt track push`.

```bash
# AI Agents workshop
cd elastic/elastic-ai-agents-tools-agents-mcp--9-2-0--snap/
instruqt track push

# Workflows workshop (production)
cd elastic/dr-rangelove-stove-store/instruqt/
instruqt track push

# Workflows workshop (dev/staging)
cd elastic/dr-rangelove-stove-store/dr-rangelove-stove-store/
instruqt track push
```

If the remote has changes you haven't pulled, Instruqt will block the push. Use `instruqt track pull` to fetch remote changes, or `instruqt track push --force` to overwrite.

## About `.remote` Files

When you run `instruqt track pull`, Instruqt creates `.remote` files (e.g., `assignment.md.remote`, `track.yml.remote`) alongside your local files. These show what's currently on the Instruqt server so you can diff against your local version.

**Do not commit `.remote` files to git.** They are local diff artifacts and will cause `instruqt track push` to fail (script `.remote` files get misinterpreted as referencing hosts like `host-1.remote`). Delete them after you've reviewed the diff.
