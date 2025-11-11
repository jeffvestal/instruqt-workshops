---
slug: 01-intro
id: dr4d5kdosqjd
type: challenge
title: 'The ''Why'': From Insights to Outcomes'
teaser: Understand the 'Two-Vendor Problem' and how Workflows solve it
notes:
- type: text
  contents: |
    # Welcome to the Elastic Workflow & AI Agent Workshop!

    In this hands-on workshop, you'll learn to build powerful automation that bridges the gap between insights and outcomes.

    We'll start with simple workflows and progress to building a complete self-healing AIOps system.
tabs:
- id: c9pr996sb31a
  title: Kibana
  type: service
  hostname: kubernetes-vm
  path: /
  port: 30001
- id: e0z8qrkti9bn
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: basic
timelimit: 300
enhanced_loading: null
---

# 📖 Challenge 1: The "Why" - From Insights to Outcomes

Welcome to the workshop!

## The Problem: The "Two-Vendor" Gap

For years, Elastic has been a world-class "insights" engine. It's fantastic at telling you *what's wrong*:

* **Security:** "We found a malicious IP in your logs!"
* **Observability:** "The ML just found a critical anomaly for your `payment-service`!"

But then what? You have to take that insight, pivot to *another tool* (a separate SOAR, a script, a PagerDuty console), and manually take *action*. This is the "Two-Vendor Problem."

## The Solution: Elastic Workflow

The new **Workflow** feature is designed to bridge this gap. It provides the "hands" to take action *directly inside* the platform.

In this workshop, we will build:

1. **Simple Workflows:** To automate simple tasks.
2. **Robust Workflows:** That use logic, handle errors, and call external APIs.
3. **AI-Powered Workflows:** That orchestrate multiple AI agents to perform complex reasoning.

By the end, you will build a "self-healing" workflow that triggers from a **real alert**, uses AI to decide on a fix, and calls an API to "remediate" the faulty service—all without human intervention.

## From Insights to Outcomes

This is the core philosophy of the workshop. Elastic gives you **insights** (alerts, anomalies, detections). Workflows turn those insights into **outcomes** (automated responses, remediation, orchestration).

Think of it this way:

* **Insights**: "What's wrong?" (Elasticsearch, ML, Security)
* **Outcomes**: "What do we do about it?" (Workflows, Agents, Actions)

## What You'll Learn

1. **Challenge 2-4:** Build and refine workflows with inputs, steps, error handling, and logic.
2. **Challenge 5:** Orchestrate multiple AI agents in an "assembly line" pattern.
3. **Challenge 6:** Give an AI agent a workflow as a "tool" to perform complex queries.
4. **Challenge 7:** Build an end-to-end self-healing system triggered by a real alert.

## Ready?

Let's get started! Click **"Next"** to build your first workflow.
