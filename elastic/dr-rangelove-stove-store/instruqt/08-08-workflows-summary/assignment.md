---
slug: 08-workflows-summary
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

## What you learned in this workshop

- Triggers and inputs
- Steps and connectors (HTTP, Elasticsearch, AI agents, console, if/else)
- Passing data across steps and accessing `output`
- Building alert-triggered automation with AI decisioning
- Logging and basic observability of workflow runs

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


