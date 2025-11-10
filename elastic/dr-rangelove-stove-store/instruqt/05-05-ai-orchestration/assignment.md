---
slug: 05-ai-orchestration
id: y6tmjjd8ywgm
type: challenge
title: The AI 'Assembly Line'
teaser: Orchestrate multiple AI agents in a generator-critic-remediator pattern
tabs:
- id: rlermfgmfouy
  title: Kibana
  type: service
  hostname: kubernetes-vm
  path: /app/management/kibana/workflows
  port: 30001
- id: cxdzbwrqjkrx
  title: Agent Builder
  type: service
  hostname: kubernetes-vm
  path: /app/ai_agent_builder
  port: 30001
- id: 6gwx3dqsdxch
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: intermediate
timelimit: 1200
enhanced_loading: null
---

# 📖 Challenge 5: The AI "Assembly Line"

A workflow's true power is orchestrating a *team* of specialized AI agents. You can build an "assembly line" to generate, validate, and remediate content. This is the "Generator-Critic-Remediator" pattern.

Our setup script has pre-built 3 agents for you:

* `agent_content_creator` (The "Generator")
* `agent_sentiment_analyzer` (The "Critic" - returns JSON)
* `agent_pr_spin_specialist` (The "Remediator")

Let's build a workflow that uses all three.

## 1. Create a New Workflow

1. Create a new workflow named `ai_content_chain`.
2. Paste this as your starting block. Our `input` is just a `topic`.

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
    enabled: true

steps:
  # Steps will go here
```

## 2. Step 1: The "Generator"

Add your first step. This calls the `agent_content_creator`.

```yaml
  - name: draft_content
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_content_creator
      input: "Write a short, 1-2 sentence press release about this topic: {{ inputs.topic }}"
```

## 3. Step 2: The "Critic"

Now, let's *check* the work of the first agent. Add this step, which feeds the *output* of Step 1 into our `agent_sentiment_analyzer`.

```yaml
  - name: first_check
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_sentiment_analyzer
      input: "{{ steps.draft_content.output.response.message }}"
```

## 4. Step 3: The "Remediator" (The "Spin Doctor")

Now for the magic. We'll call the `agent_pr_spin_specialist`, but we'll give it *both* the original draft *and* the bad sentiment.

```yaml
  - name: remediation_spin
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_pr_spin_specialist
      input: |
        The following draft was written:
        "{{ steps.draft_content.output.response.message }}"
        
        It was analyzed with this sentiment:
        "{{ steps.first_check.output.response.message.sentiment }}"
        
        Please revise this draft to have a strongly positive spin.
```

## 5. Step 4 & 5: Final Check & Report

Finally, let's check the "spun" draft and print a final report.

```yaml
  - name: final_check
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_sentiment_analyzer
      input: "{{ steps.remediation_spin.output.response.message }}"

  - name: final_report
    type: console
    with:
      message: |
        ---
        Original Draft: {{ steps.draft_content.output.response.message }}
        Original Sentiment: {{ steps.first_check.output.response.message.sentiment }}
        ---
        Revised Draft: {{ steps.remediation_spin.output.response.message }}
        Final Sentiment: {{ steps.final_check.output.response.message.sentiment }}
        ---
        
        {% if steps.final_check.output.response.message.sentiment == "POSITIVE" %}
        ✅ Content is approved and ready to send.
        {% else %}
        ❌ FAILED: Content still has negative sentiment after remediation.
        {% endif %}
```

## 6. Run and Analyze

1. **Save** your workflow.
2. **Run** it.
3. For the `topic`, enter something negative: `Our servers had an outage`.
4. Run the workflow and inspect the `final_report` step. You'll see the full chain: the negative first draft, the "NEGATIVE" sentiment, the new "spun" draft, and (hopefully) the "POSITIVE" final sentiment.

You just built an AI assembly line!

**Click "Next" for the final piece of the puzzle.**
