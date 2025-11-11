---
slug: 06-observability-bot
id: p7vdgfytqack
type: challenge
title: 'The ''Full Circle'': AI Agent Tools'
teaser: Give an AI agent a workflow as a tool to perform complex operations
tabs:
- id: vtbs6dxl9ui9
  title: Kibana
  type: service
  hostname: kubernetes-vm
  path: /app/management/kibana/workflows
  port: 30001
- id: aovug3gwcqds
  title: Agent Builder
  type: service
  hostname: kubernetes-vm
  path: /app/agent_builder
  port: 30001
- id: boqsyf6qjdpr
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: intermediate
timelimit: 1200
enhanced_loading: null
---

# 📖 Challenge 6: The "Full Circle" - The Observability Triage Bot

So far, our workflows have called AI. Now, let's make an **AI call our workflow**.

This "full circle" integration is the key concept. We will give an AI Agent a "Workflow Tool" to run automation on its behalf.

**Goal:** We will build an "SRE Triage Bot." When we ask it to "triage a service," it will run a workflow to pull logs and metrics from our `o11y-heartbeat` index, then give us a summary.

## Part 1: Build the Workflow "Tool"

An AI Agent can't query Elasticsearch on its own. We'll build a workflow that does the "dirty work" of data retrieval from our index.

1. Create a new workflow named `triage_service_incident`.
2. Paste this entire workflow. **Read it carefully.** It uses a new step type: `elasticsearch.search`, and queries our custom `o11y-heartbeat` index.

```yaml
version: "1"
name: triage_service_incident
description: "Triage a service by querying observability data"
enabled: true

inputs:
  - name: service_name
    type: string
    required: true
    description: "The name of the service to triage"

triggers:
  - type: manual

steps:
  # Get 5 most recent 5xx error messages
  - name: get_error_logs
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        bool:
          must:
            - term:
                service.name: "{{ inputs.service_name }}"
            - range:
                http.status_code:
                  gte: 500
      size: 5
      sort:
        - "@timestamp": "desc"

  # Get the P95 latency
  - name: get_latency
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        term:
          service.name: "{{ inputs.service_name }}"
      aggs:
        p95_latency:
          percentiles:
            field: "latency_ms"
            percents: [95]
      size: 0

  # Format a report for the AI
  - name: format_triage_report
    type: console
    with:
      message: |
        Triage Report for {{ inputs.service_name }}:
        - P95 Latency is {{ steps.get_latency.response.aggregations.p95_latency.values["95.0"] }} ms.
        - Found {{ steps.get_error_logs.response.hits.total.value }} error logs.
        - Sample Error: {{ steps.get_error_logs.response.hits.hits[0]._source.log.message }}
```

3. **Save** this workflow. Do NOT run it yet.

## Part 2: Test the Workflow Manually

Before giving it to the agent, let's verify it works:

1. Click **"Run"** on the workflow.
2. For `service_name`, enter: `payment-service`
3. Observe the three steps execute.
4. Check the `format_triage_report` output—you should see latency stats and error counts.

## Part 3: Give the Agent its "Tool"

Now we'll attach this workflow to the `sre_triage_bot` agent that was created during setup.

1. In Kibana, go to the menu and find **Agent Builder** (under AI & Machine Learning).
2. Click on **"Agents"** and find `sre_triage_bot`.
3. Click **"Edit"**.
4. Scroll down to **"Tools"** and click **"Add tool"**.
5. Select **"Workflow"** as the tool type.
6. From the **Workflow** dropdown, select your `triage_service_incident` workflow.
7. The `service_name` input should appear automatically.
8. Click **"Save"** to save the tool, then **"Save"** again to save the agent.

## Part 4: Run the "Full Circle"

1. At the top of the Agent Builder screen, click the **"Chat"** tab.
2. In the chat window, type:

   ```
   Hey, can you please run triage on the "payment-service"?
   ```

3. **Observe:**
   * The agent will respond that it is "using a tool."
   * In the background, it just triggered your workflow and passed it `payment-service` as the input.
   * It will get the formatted "Triage Report" message back from the workflow.
   * It will then present this data to you in natural language.

You have closed the loop. The AI is now a "conversational front-end" for your complex automation.

**Click "Next" for the final capstone challenge.**
