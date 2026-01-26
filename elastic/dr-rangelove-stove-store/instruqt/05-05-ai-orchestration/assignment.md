---
slug: 05-ai-orchestration
id: dikdylbhyer2
type: challenge
title: The AI 'Assembly Line'
teaser: Orchestrate multiple AI agents in a generator-critic-remediator pattern
tabs:
- id: 07caoimvmlzk
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: gcmmeeyjp6yg
  title: Agent Builder
  type: service
  hostname: kubernetes-vm
  path: /app/agent_builder/agents
  port: 30001
- id: xwppo2qxixmd
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: intermediate
timelimit: 1200
enhanced_loading: null
---

# 📖 Challenge 5: The AI "Assembly Line"

A workflow's true power is orchestrating a *team* of specialized AI agents. You can build an "assembly line" to generate, validate, and remediate content. This is the "Generator-Critic-Remediator" pattern.

## Review the Agents

Before we build the workflow, let's look at the specialized agents available in this environment.

1. Click on the [button label="Agent Builder"](tab-1) tab.
2. Review the list of agents.

You will see five custom agents created for this workshop:

* **agent_content_creator** (Press Release Content Creator): A creative agent designed to draft initial press release content based on a provided topic. It acts as the "Generator" in our pattern.
* **agent_sentiment_analyzer** (Sentiment Analyzer): An analytical agent that evaluates text and returns a structured JSON response indicating the sentiment. It acts as the "Critic".
* **agent_pr_spin_specialist** (PR Spin Specialist): A "remediator" agent that takes negative content and rewrites it to be more positive.
* **sre_triage_bot** (SRE Triage Bot): An agent designed to triage services using a workflow tool. *We will use this in a later challenge.*
* **agent_business_slo** (Business SLO Analyst): An agent that analyzes business metrics and SLOs to recommend actions. *We will use this in a later challenge.*

These agents demonstrate how specialized, single-purpose agents can be combined to solve complex tasks.

Let's build a workflow that uses the first three.

## 1. Create a New Workflow

1. Click on the [button label="Kibana - Workflows"](tab-0) tab.
2. Click on **Create a new workflow**
3. Paste this as your starting block (replace the placeholder text).
   - Our `input` is just a `topic`.

```yaml
version: "1"
name: ai_content_chain
description: "Orchestrate AI agents to generate, analyze, and improve content"
enabled: true

inputs:
  - name: topic
    type: string
    required: true
    description: "The topic for the press release"

triggers:
  - type: manual

steps:
  # Steps will go here
```

## 2. Step 1: The "Generator"

Add your first step. This calls the `agent_content_creator`.

```yaml
  - name: draft_content
    type: ai.agent
    with:
      agent_id: agent_content_creator
      message: "Write a short, 1-2 sentence press release about this topic: {{ inputs.topic }}"
```

## 3. Step 2: The "Critic"

Now, let's *check* the work of the first agent. Add this step, which feeds the *output* of Step 1 into our `agent_sentiment_analyzer`.

```yaml
  - name: first_check
    type: ai.agent
    with:
      agent_id: agent_sentiment_analyzer
      message: "{{ steps.draft_content.output }}"
```

## 3.5. Step 2.5: Parse the JSON Response

The `agent_sentiment_analyzer` returns a JSON string. We need to parse it to access the `sentiment` property. Add this step:

```yaml
  - name: first_check_parsed
    type: console
    with:
      message: ${{steps.first_check.output|json_parse}}
```

**Note:** This step demonstrates explicit JSON parsing. You could also use `{% assign %}` in the next step, but this shows both approaches.

## 4. Step 3: The "Remediator" (The "Spin Doctor")

Now for the magic. We'll call the `agent_pr_spin_specialist`, but we'll give it *both* the original draft *and* the bad sentiment.

```yaml
  - name: remediation_spin
    type: ai.agent
    with:
      agent_id: agent_pr_spin_specialist
      message: |
        The following draft was written:
        "{{ steps.draft_content.output }}"

        It was analyzed with this sentiment:
        "{{ steps.first_check_parsed.output.sentiment}}"

        Please revise this draft to have a strongly positive spin.
```

## 5. Step 4 & 5: Final Check & Report

Finally, let's check the "spun" draft and print a final report.

```yaml
  - name: final_check
    type: ai.agent
    with:
      agent_id: agent_sentiment_analyzer
      message: "{{ steps.remediation_spin.output }}"

  - name: final_report
    type: console
    with:
      message: >-
        {% assign orig = steps.first_check.output | json_parse %}
        {% assign fin = steps.final_check.output | json_parse %}

        ***
        Original Draft: {{ steps.draft_content.output.response.message }}
        Original Sentiment: {{ orig.sentiment }}
        ***
        Revised Draft: {{ steps.remediation_spin.output.response.message }}
        Final Sentiment: {{ fin.sentiment }}
        ***
        {% if fin.sentiment == "POSITIVE" %}
        ✅ PASSED: Content sentiment is positive after remediation.
        {% else %}
        ❌ FAILED: Content still has negative sentiment after remediation.
        {% endif %}
```

<details>
  <summary>Click here to expand full workflow YAML</summary>

  <pre><code>
version: "1"
name: ai_content_chain
description: "Orchestrate AI agents to generate, analyze, and improve content"
enabled: true

inputs:
  - name: topic
    type: string
    required: true
    description: "The topic for the press release"

triggers:
  - type: manual

steps:
  - name: draft_content
    type: ai.agent
    with:
      agent_id: agent_content_creator
      message: "Write a short, 1-2 sentence press release about this topic: {{ inputs.topic }}"

  - name: first_check
    type: ai.agent
    with:
      agent_id: agent_sentiment_analyzer
      message: "{{ steps.draft_content.output }}"

  - name: first_check_parsed
    type: console
    with:
      message: ${{steps.first_check.output|json_parse}}

  - name: remediation_spin
    type: ai.agent
    with:
      agent_id: agent_pr_spin_specialist
      message: |
        The following draft was written:
        "{{ steps.draft_content.output }}"

        It was analyzed with this sentiment:
        "{{ steps.first_check_parsed.output.sentiment}}"

        Please revise this draft to have a strongly positive spin.

  - name: final_check
    type: ai.agent
    with:
      agent_id: agent_sentiment_analyzer
      message: "{{ steps.remediation_spin.output }}"

  - name: final_report
    type: console
    with:
      message: >-
        {% assign orig = steps.first_check.output | json_parse %}
        {% assign fin = steps.final_check.output | json_parse %}

        ***
        Original Draft: {{ steps.draft_content.output.response.message }}
        Original Sentiment: {{ orig.sentiment }}
        ***
        Revised Draft: {{ steps.remediation_spin.output.response.message }}
        Final Sentiment: {{ fin.sentiment }}
        ***
        {% if fin.sentiment == "POSITIVE" %}
        ✅ PASSED: Content sentiment is positive after remediation.
        {% else %}
        ❌ FAILED: Content still has negative sentiment after remediation.
        {% endif %}

</code></pre>
</details>

## 6. Run and Analyze

1. **Save** your workflow.
2. **Run** it.
3. For the `topic`, enter something (in the `input Data` JSON) negative:
    ```
    Our servers had an outage
    ```
    ![CleanShot 2025-11-13 at 13.51.06@2x.png](../assets/CleanShot%202025-11-13%20at%2013.51.06%402x.png)
4. Run the workflow click on each step to see what happens
- `draft_conten` - The short status message is created based on your input.
- `first_check` - the sentiment comes back `NEGATIVE` (assuming you put in the negative example).
- `remediation_spin` - This agent puts a nice PR positive spin on a response that would be sent out after the issue is remediated.
- `final_check` - We ensure the spin was positive.
- `final_report` - We a PR friendly incident report

![CleanShot 2025-11-13 at 14.11.45@2x.png](../assets/CleanShot%202025-11-13%20at%2014.11.45%402x.png)

You just built an AI assembly line!

**Click "Next" for the final piece of the puzzle.**
