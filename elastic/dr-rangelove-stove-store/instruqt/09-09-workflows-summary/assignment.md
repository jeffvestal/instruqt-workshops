---
slug: 09-workflows-summary
id: tazfbxorwrv8
type: challenge
title: Workflows Summary and Next Steps
teaser: A quick recap of Kibana Workflows, core concepts, and where to learn more
tabs:
- id: yryjjgkyxb07
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: iehqfny90dyg
  title: Docs - Kibana Workflows
  type: website
  url: https://www.elastic.co/guide/en/kibana/current/workflows.html
difficulty: basic
timelimit: 600
enhanced_loading: null
---

# Workflows Summary and Next Steps

Kibana Workflows let you compose automations that react to alerts, perform HTTP calls, interact with Elasticsearch, call AI agents, and more — all declaratively in YAML.

## What You Built

Throughout this workshop, you've built increasingly sophisticated workflows:

### Challenge 2: Hello World
- **Simple input/output**: Created your first workflow with user input and console output
- **Key concept**: Liquid templating with `{{ inputs.username }}`

### Challenge 3: Chaining Steps
- **HTTP API chaining**: Called an external geolocation API and used its response
- **Key concept**: Accessing step outputs with `steps.<step>.output.data.<field>`

### Challenge 4: Robust Workflows
- **Error handling + conditionals**: Added retry logic and conditional branching based on API responses
- **Key concept**: `on-failure` blocks, `if` conditions, and handling edge cases

### Challenge 5: AI Orchestration
- **AI agent pipeline**: Orchestrated multiple AI agents in sequence (draft → analyze → revise → verify)
- **Key concept**: Chaining AI agents to create sophisticated content workflows

### Challenge 6: Agent + Workflow Tools
- **Workflow as a tool**: Created a workflow that an AI agent can use as a tool
- **Key concept**: Integrating workflows with Agent Builder for complex query capabilities

### Challenge 7: Self-Healing with AI
- **Alert-triggered automation**: Built a workflow that triggers from alerts, uses AI to decide remediation, and calls external APIs
- **Key concept**: Complete automation loop: Alert → AI Analysis → Action → Audit Log

### Challenge 8: Business Impact Detection
- **Business-critical automation**: Created a workflow from scratch that detects both technical AND business metrics
- **Key concept**: Bridging observability data with business outcomes, automated scaling decisions

## Architecture Overview

Here's what you've built:

```
┌─────────────┐
│   Alerts    │  (Observability, Security, ML Anomalies)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         Workflows                    │  (You built these!)
│  ┌──────────────────────────────┐  │
│  │ 1. Parse alert data           │  │
│  │ 2. Query Elasticsearch        │  │
│  │ 3. Call AI agents              │  │
│  │ 4. Make decisions (if/else)    │  │
│  │ 5. Call external APIs          │  │
│  │ 6. Log to Elasticsearch        │  │
│  └──────────────────────────────┘  │
└──────┬──────────────────────────────┘
       │
       ├─────────────────┬──────────────────┐
       ▼                 ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ AI Agents   │  │ External     │  │ Elasticsearch│
│ (Agent      │  │ APIs         │  │ (Audit Logs)│
│  Builder)   │  │ (Remediation)│  │              │
└─────────────┘  └──────────────┘  └──────────────┘
```

**The Power**: You've created autonomous systems that turn findings (alerts, anomalies) into outcomes (automated actions, remediation, scaling).

## What You Learned

- **Triggers and inputs**: Manual triggers, alert triggers, and user inputs
- **Steps and connectors**: HTTP, Elasticsearch, AI agents, console, if/else, error handling
- **Data flow**: Passing data across steps and accessing `output` with correct paths
- **AI orchestration**: Chaining multiple agents, using agents as tools, AI-powered decision making
- **Alert-driven automation**: Complete automation loops from detection to action
- **Business automation**: Connecting technical metrics to business outcomes

## Common workflow use cases

- Alert-driven remediation (restart services, open tickets, page on-call)
- Enrich/triage alerts with external data sources
- Notify and summarize with AI (Slack/Email)
- Index audit trails and outcomes back to Elasticsearch

## Learn more

- Official docs: Kibana Workflows (link in the Docs tab)
- Best practices, patterns, and advanced topics (coming soon)
- Advanced AI orchestration and tool creation (coming soon)

---

Note: Clicking the "Next" button will end the workshop and return you to the track list.


