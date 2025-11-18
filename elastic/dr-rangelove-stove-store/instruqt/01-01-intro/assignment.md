---
slug: 01-intro
id: tom9sadinbfe
type: challenge
title: 'The ''Why'': From Findings to Outcomes'
teaser: Understand the 'Two-Vendor Problem' and how Workflows solve it
notes:
- type: text
  contents: |
    # Welcome to the Elastic Workflow & AI Agent Workshop!

    In this hands-on workshop, you'll learn to build robust automation that bridges the gap between findings and outcomes.

    We'll start with simple workflows and progress to building a complete business impact detection system that combines ES|QL queries, AI agents, and deterministic logic.
tabs:
- id: 5wlncph7b7pt
  title: Kibana
  type: service
  hostname: kubernetes-vm
  path: /
  port: 30001
- id: 6d8wv6pm17ce
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: basic
timelimit: 300
enhanced_loading: null
---

# 📖 Challenge 1: The "Why" - From Findings to Outcomes

Welcome to the workshop!

## The Problem: The "Two-Vendor" Gap

For years, Elastic has been a world-class "findings" engine. It's fantastic at telling you *what's wrong*:

* **Security:** "We found a malicious IP in your logs!"
* **Observability:** "The ML just found a critical anomaly for your `payment-service`!"

But then what? You have to take that finding, pivot to *another tool* (a separate SOAR, a script, a PagerDuty console), and manually take *action*. This is the "Two-Vendor Problem."

## The Solution: Elastic Workflow

The new **Workflow** feature is designed to bridge this gap. It provides the "hands" to take action *directly inside* the platform.

In this workshop, we will build:

1. **Simple Workflows:** To automate simple tasks.
2. **Robust Workflows:** That use logic, handle errors, and call external APIs.
3. **AI-Powered Workflows:** That orchestrate multiple AI agents to perform complex reasoning.
4. **Business-Critical Automation:** Using ES|QL for fast queries, deterministic logic for reliable decisions, and AI for human-readable explanations.

By the end, you will build two major systems:
- A "self-healing" workflow that auto-remediates service issues
- A "business impact detector" that monitors revenue-critical metrics and scales services automatically

## From Findings to Outcomes

This is the core philosophy of the workshop. Elastic gives you **findings** (alerts, anomalies, detections). Workflows turn those findings into **outcomes** (automated responses, remediation, orchestration).

Think of it this way:

* **Findings**: "What's wrong?" (Search, Observability, Security)
* **Outcomes**: "What do we do about it?" (Workflows, Agents, Actions)

## What You'll Learn

1. **Challenge 2-4:** Build and refine workflows with inputs, steps, error handling, and logic.
2. **Challenge 5:** Orchestrate multiple AI agents in an "assembly line" pattern.
3. **Challenge 6:** Give an AI agent a workflow as a "tool" to perform complex queries.
4. **Challenge 7:** Build an end-to-end self-healing system triggered by a real alert.
5. **Challenge 8:** **Capstone** - Build a business impact detection system from scratch using ES|QL, AI agents, and deterministic logic.
6. **Challenge 9:** Workshop summary and next steps.

## Ready?

Let's get started! Click **"Next"** to build your first workflow.

---

**TODO:** This challenge needs more substantive content (slides, diagrams, or expanded explanations) to properly set the stage for the workshop.
