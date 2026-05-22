---
slug: agent-builder-ui
id: yf8lczaygpwr
type: challenge
title: Explore Agent Builder in Kibana
teaser: Navigate to Agent Builder and create your first AI agent
notes:
- type: text
  contents: |
    ## Elastic Agent Builder

    Agent Builder is built into Kibana. It lets you create AI agents that can:

    - Answer questions using your Elasticsearch data
    - Call tools like ES|QL queries, search APIs, and custom connectors
    - Chain together with other agents for multi-agent workflows

    No code required — configure everything from the Kibana UI.
- type: text
  contents: |
    ## What We're Building

    In this challenge, you'll:

    1. Navigate to Agent Builder in Kibana
    2. Create a simple agent with a system prompt
    3. Chat with it to confirm it's working

    The **Kibana** tab is already pointed at the Agent Builder section.
tabs:
- id: rp9w8qup9qyx
  title: Kibana - Agent Builder
  type: service
  hostname: kubernetes-vm
  path: /app/enterpriseSearch/content/agents
  port: 30001
- id: mq9nzdunnfma
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: basic
timelimit: 900
enhanced_loading: null
---

## Overview

In this challenge you'll use the **Kibana - Agent Builder** tab to create a simple AI agent
and have a conversation with it.

## What You'll Do

- Open the Agent Builder interface
- Create a new agent with a custom name and system prompt
- Send it a test message and verify it responds

## Steps

### 1. Open Agent Builder

Click the **Kibana - Agent Builder** tab. You should see the Agent Builder landing page.

If prompted to log in, use:
- **Username**: `elastic`
- **Password**: run `echo $ELASTICSEARCH_PASSWORD` in the Terminal tab to get the value

### 2. Create a New Agent

Click **Create agent** (or **New agent**).

Fill in:
- **Name**: `Test Agent`
- **Instructions**: `You are a helpful assistant. When asked what you are, say you are a test agent created in an Instruqt workshop.`

Click **Save**.

### 3. Chat With Your Agent

In the chat panel, type:

```
What are you?
```

The agent should respond confirming it's a test agent.

> **Hint**: If the agent tab shows a loading spinner for more than 30 seconds, try refreshing the tab. The Kibana service is available once the setup script finishes (usually within 2-3 minutes of track start).

## Verify

Your agent responds to the test message with something that confirms it received your instructions.

<details>
<summary>Agent not responding? Expand for troubleshooting</summary>

1. Load env vars if missing: `export $(curl -s http://kubernetes-vm:9000/env | xargs)`
2. Verify Kibana is reachable: `curl -s -H "Authorization: Basic ${ELASTICSEARCH_AUTH_BASE64}" ${KIBANA_URL}/api/status | jq .status.overall`
3. Check LLM connector: `echo $LLM_APIKEY` — should be non-empty if setup script completed.
4. If Kibana returns `"level": "available"`, the UI should be accessible.

</details>
