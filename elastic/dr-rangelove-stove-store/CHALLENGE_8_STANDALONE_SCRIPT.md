# Challenge 8 Standalone Video Script
## Business Impact Detection with Elastic Workflows

**Target Duration:** 5-7 minutes  
**Purpose:** Feature preview/teaser for Elastic Workflows (tech preview early 2025)  
**Audience:** Technical practitioners with basic Elastic knowledge

---

# Section A: Verbal Script

## Opening (0:00-1:00)

### Feature Introduction (0:00-0:30)

"Today I'm excited to show you Elastic Workflows—a powerful new automation capability coming to the Elastic platform.

**Important note:** Elastic Workflows is currently in active development and will enter tech preview in early 2025. Since this feature is still being finalized, some details you see today may change before the official release.

Along with the tech preview, we'll be releasing a comprehensive hands-on workshop to teach you these automation patterns."

### What Workflows Solve (0:30-1:00)

"For years, Elastic has been exceptional at *finding* problems—detecting anomalies, security threats, performance issues. But then what? You have to pivot to other tools—PagerDuty, Kubernetes, custom scripts—to actually *fix* the problem.

This is what I call the 'Two-Vendor Problem': detection happens in Elastic, remediation happens somewhere else. Workflows closes that gap by giving Elastic 'hands'—native automation capabilities that turn alerts into actions, all within a single platform."

### What We're Building Today (1:00-1:00)

"Today I'm going to show you something really powerful: a business impact detector. This isn't just technical monitoring—it's business-aware automation that prevents revenue loss by automatically scaling infrastructure when payment transactions drop.

Let me show you how it works."

---

## The Use Case (1:00-1:30)

### Business Problem

"Imagine your payment service starts experiencing errors. Not just high latency—actual successful transactions are dropping. Revenue is bleeding in real-time.

Traditional monitoring would fire a technical alert: 'Error rate is high.' But that doesn't tell you the business impact. Are you losing $100 an hour? $10,000 an hour? Should you scale immediately, or is this a minor blip?"

### What the Workflow Does

"Our workflow solves this by:

1. Using ES|QL to query multiple metrics in one efficient query—error count, current payment volume, baseline payment volume, transaction amounts
2. Calculating business impact—the percentage drop in successful payments
3. Using deterministic logic to decide if auto-scaling is needed—if payment drop exceeds 30%, scale immediately
4. Calling an AI agent to explain the impact to stakeholders in plain English—'Revenue is at risk due to payment failures. Recommend immediate investigation.'
5. Logging everything to Elasticsearch for a complete audit trail

This is production-ready automation that bridges the gap between observability and business outcomes."

---

## Building the Workflow (1:30-5:30)

### Section 1: Setup (1:30-2:00)

"Let's build this workflow. I'm in Kibana's Workflows UI—this is where you'll create and manage workflows once the tech preview launches.

I'll create a new workflow called `business_impact_detector`. Here's the basic structure—YAML format, with metadata, inputs, triggers, and steps.

To keep this video moving, I'll use solution blocks for the complex parts. The focus is on understanding the pattern, not typing YAML."

### Section 2: ES|QL Multi-Metric Query (2:00-3:00)

"First step: query all the metrics we need. This is where ES|QL really shines.

Instead of running 3 or 4 separate Elasticsearch queries, we can get everything in one query using EVAL and STATS.

Here's the ES|QL query:"

[Show solution block for `get_all_metrics` step]

"Let me break this down:

- We're querying the `o11y-heartbeat` index for payment-service data
- EVAL creates boolean flags: is this an error? Is this a successful payment in the last 5 minutes? Is this a successful payment in the baseline period (60 minutes ago)?
- STATS aggregates these flags into counts: error count, current payment count, baseline payment count, and total transaction amounts

This single query returns 4 metrics. Traditionally, this would be 3-4 separate queries—ES|QL makes it efficient.

To access the results, we use `.output.values[0][0]` for the first metric, `.output.values[0][1]` for the second, and so on. ES|QL returns data as an array of arrays, so we index into the first row and then the column we want."

### Section 3: AI Explanation Layer (3:00-3:45)

"Next, we call an AI agent to explain the business impact. But here's the key: the AI doesn't make the scaling decision—it explains it.

We pass all the metrics to the agent and ask it to explain the business impact in 2-3 sentences for stakeholders. The agent will say something like: 'Payment processing is experiencing significant degradation. Current successful payment rate is 60% below baseline, indicating potential revenue loss of approximately $X per hour. Recommend immediate investigation of payment gateway connectivity.'"

[Show solution block for `ai_business_summary` step]

"This gives you human-readable summaries for executives and stakeholders. The AI is great at communication—but we don't let it make critical decisions. That's where deterministic logic comes in."

### Section 4: Deterministic Decision Logic (3:45-4:30)

"Now for the scaling decision. This is deterministic—no AI guessing.

We calculate the payment drop percentage using Liquid templating. If the drop exceeds 30%, we auto-scale. Otherwise, we log the incident but don't scale."

[Show solution block for `check_scaling_needed` step]

"Here's the logic:

- We normalize the baseline to a 5-minute equivalent (baseline was 60 minutes, so divide by 12)
- Calculate the drop percentage: `(normalized_baseline - current) / normalized_baseline * 100`
- If drop >= 30%, execute the scaling steps
- Otherwise, log that no scaling was needed

This is the hybrid pattern: deterministic logic for reliability, AI for explainability. The workflow makes the decision based on numbers. The AI explains that decision in human language."

[Show the `if` condition and nested `scale_service` HTTP call]

"When scaling is needed, we POST to a scaling API—in production, this might be Kubernetes, AWS Auto Scaling, or your cloud provider's API. The workflow handles retries if the API call fails."

### Section 5: Audit Logging (4:30-5:00)

"Finally, we log everything to Elasticsearch for a complete audit trail."

[Show solution block for `log_to_elasticsearch` step]

"Every automated action is logged: the metrics, the AI explanation, the scaling decision, the results. This gives you full observability of your automation—you can query these logs, build dashboards, track trends over time.

This is essential for compliance and debugging. When something goes wrong, you can see exactly what the workflow did and why."

---

## Testing & Wrap-Up (5:00-6:30)

### Quick Test (5:00-5:45)

"Let me trigger a business incident to show this in action."

[Switch to Terminal tab]

"I'll run a script that simulates a payment service degradation—error rate spikes, successful transactions drop by 60%, transaction amounts drop by 50%."

[Run trigger script, fast-forward through 1-2 minute wait]

"Now let's check the workflow execution."

[Switch back to Kibana Workflows UI]

"Here's the execution history. The workflow ran automatically when the alert fired. Let me expand the steps:

- `get_all_metrics`: Retrieved error count, current payments, baseline payments
- `ai_business_summary`: AI explained the impact—'Revenue is at risk due to payment failures...'
- `check_scaling_needed`: Condition evaluated to true—drop exceeded 30%
- `scale_service`: Mock API returned 'Scaled from 2 to 4 instances'
- `log_to_elasticsearch`: Complete audit log indexed

This all happened automatically. No human intervention. The workflow detected the business impact, decided to scale, and logged everything."

### Key Takeaways (5:45-6:15)

"Here's what makes this powerful:

1. **Business-aware automation**—not just technical monitoring. This workflow understands revenue impact, not just error rates.

2. **Hybrid pattern**—ES|QL for efficiency, deterministic logic for reliability, AI for communication. Each technology does what it's best at.

3. **Production-ready**—error handling, retry logic, audit logging. This is a real pattern you can adapt to any business-critical metric: checkout conversion, order fulfillment, API billing—whatever matters to your revenue."

### Call to Action (6:15-6:30)

"Elastic Workflows enters tech preview in early 2025. We're building a comprehensive hands-on workshop to teach you these patterns—9 progressive challenges from hello world to production-ready systems like this.

Follow us for updates—links are in the description. Questions? Drop them in the comments. Thanks for watching!"

---

# Section C: Full Demo Flow with Timestamps

## 0:00-0:30 - Feature Intro and Disclaimer

**On-screen text (first 10 seconds):**
```
⚠️ PREVIEW CONTENT
Elastic Workflows is in active development
Features shown may change before tech preview (Q1 2025)
```

**Verbal:**
- "Today I'm excited to show you Elastic Workflows—a powerful new automation capability coming to the Elastic platform."
- "Important note: Elastic Workflows is currently in active development and will enter tech preview in early 2025. Since this feature is still being finalized, some details you see today may change before the official release."
- "Along with the tech preview, we'll be releasing a comprehensive hands-on workshop to teach you these automation patterns."

**Visual:**
- Show Kibana UI with Workflows tab visible
- Optionally show Elastic logo or workshop preview image

---

## 0:30-1:00 - Two-Vendor Problem & What We're Building

**Verbal:**
- Explain Two-Vendor Problem (30 seconds)
- "Today I'm going to show you something really powerful: a business impact detector."

**Visual:**
- Optionally show diagram: Alert → Human → Multiple Tools vs. Alert → Workflow → Action
- Transition to Kibana Workflows UI

---

## 1:00-1:30 - Business Use Case Explanation

**Verbal:**
- "Imagine your payment service starts experiencing errors..."
- Explain the business problem and what the workflow does

**Visual:**
- Show payment service metrics (mockup or actual data)
- Optionally show revenue impact visualization

---

## 1:30-2:00 - Kibana UI, Create Workflow

**Verbal:**
- "Let's build this workflow. I'm in Kibana's Workflows UI..."
- "I'll create a new workflow called `business_impact_detector`."
- "To keep this video moving, I'll use solution blocks for the complex parts."

**Visual:**
- Navigate to Kibana → Management → Workflows
- Click "Create Workflow"
- Show blank YAML editor
- Paste starter template:
```yaml
version: "1"
name: business_impact_detector
description: "Detect and respond to business-critical payment service degradation"
enabled: true

inputs: []

triggers:
  - type: alert

steps:
  # TODO: Add steps here
```

---

## 2:00-3:00 - ES|QL Query (Expand Solution, Explain Pattern)

**Verbal:**
- "First step: query all the metrics we need. This is where ES|QL really shines."
- Explain EVAL and STATS
- "This single query returns 4 metrics. Traditionally, this would be 3-4 separate queries."
- Explain `.output.values[0][0]` access pattern

**Visual:**
- Expand/collapse solution block for `get_all_metrics` step
- Paste the ES|QL query:
```yaml
- name: get_all_metrics
  type: elasticsearch.esql.query
  with:
    query: >
      FROM o11y-heartbeat
      | WHERE service.name == "payment-service"
      | EVAL 
          is_error = CASE(http.status_code >= 500 AND @timestamp >= NOW() - 5 MINUTES, 1, 0),
          is_current_success = CASE(transaction.status == "success" AND @timestamp >= NOW() - 5 MINUTES, 1, 0),
          is_baseline_success = CASE(transaction.status == "success" AND @timestamp >= NOW() - 65 MINUTES AND @timestamp < NOW() - 5 MINUTES, 1, 0),
          current_amount = CASE(is_current_success == 1, transaction.amount, 0)
      | STATS 
          error_count = SUM(is_error),
          current_payment_count = SUM(is_current_success),
          current_total_amount = SUM(current_amount),
          baseline_payment_count = SUM(is_baseline_success)
```
- Highlight EVAL and STATS sections
- Show comment: "Access results as `.output.values[0][0]` to `[0][3]`"

---

## 3:00-3:45 - AI Explanation (Expand Solution, Show Prompt)

**Verbal:**
- "Next, we call an AI agent to explain the business impact."
- "The AI doesn't make the scaling decision—it explains it."
- "This gives you human-readable summaries for stakeholders."

**Visual:**
- Expand/collapse solution block for `ai_business_summary` step
- Paste the AI step:
```yaml
- name: ai_business_summary
  type: kibana.post_agent_builder_converse
  with:
    agent_id: agent_business_slo
    input: |
      Here are the current metrics for payment-service:
      - Error count (last 5m): {{ steps.get_all_metrics.output.values[0][0] }}
      - Current successful payments (last 5m): {{ steps.get_all_metrics.output.values[0][1] }}
      - Baseline successful payments (previous 60m total): {{ steps.get_all_metrics.output.values[0][3] }}
      
      Your job is to explain the business impact in 2–3 sentences for an SRE and business audience.
      Do not decide whether to scale; only explain impact and suggest follow-up checks.
```
- Highlight the prompt structure
- Show how metrics are passed via Liquid templating

---

## 3:45-4:30 - Deterministic Logic (Expand Solution, Highlight Condition)

**Verbal:**
- "Now for the scaling decision. This is deterministic—no AI guessing."
- Explain the calculation logic
- "This is the hybrid pattern: deterministic logic for reliability, AI for explainability."

**Visual:**
- Expand/collapse solution block for `check_scaling_needed` step
- Paste the conditional step:
```yaml
- name: check_scaling_needed
  type: if
  condition: |
    {% assign current = steps.get_all_metrics.output.values[0][1] | plus: 0 %}
    {% assign baseline_total = steps.get_all_metrics.output.values[0][3] | plus: 0 %}
    {% assign normalized_baseline = baseline_total | divided_by: 12.0 %}
    {% assign drop_pct = normalized_baseline | minus: current | times: 100.0 | divided_by: normalized_baseline %}
    {% if drop_pct >= 30 %}true{% else %}false{% endif %}
  steps:
    - name: scale_service
      type: http
      with:
        url: "http://host-1:3000/scale_service"
        method: POST
        headers:
          Content-Type: application/json
        body:
          service_name: "payment-service"
```
- Highlight the condition calculation
- Show the nested `scale_service` HTTP step
- Point out retry logic in `on-failure` block

---

## 4:30-5:00 - Audit Logging (Expand Solution Briefly)

**Verbal:**
- "Finally, we log everything to Elasticsearch for a complete audit trail."
- "Every automated action is logged: the metrics, the AI explanation, the scaling decision, the results."

**Visual:**
- Expand/collapse solution block for `log_to_elasticsearch` step
- Paste briefly:
```yaml
- name: log_to_elasticsearch
  type: elasticsearch.index
  with:
    index: "business_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}"
    document:
      timestamp: "{{ execution.startedAt }}"
      workflow_name: "business_impact_detector"
      error_count: "{{ steps.get_all_metrics.output.values[0][0] }}"
      ai_explanation: "{{ steps.ai_business_summary.output.response.message }}"
      action_taken: "{{ steps.scale_service.output.data.action | default: 'no_action' }}"
```
- Highlight key fields being logged

---

## 5:00-5:45 - Trigger Incident, Show Results

**Verbal:**
- "Let me trigger a business incident to show this in action."
- "I'll run a script that simulates a payment service degradation..."
- "Now let's check the workflow execution."

**Visual:**
- Switch to Terminal tab
- Run: `bash /opt/workshop-assets/setup_scripts/06-trigger-business-incident.sh`
- Show script output: "Business incident triggered..."
- Fast-forward indicator: "Waiting 1-2 minutes for alert to fire..."
- Switch back to Kibana Workflows UI
- Navigate to `business_impact_detector` → Executions tab
- Show automatic execution (green checkmark)
- Expand steps one by one:
  - `get_all_metrics`: Show output values (error_count: 45, current_payment_count: 120, etc.)
  - `ai_business_summary`: Show AI response: "Payment processing is experiencing significant degradation..."
  - `check_scaling_needed`: Show condition evaluated to TRUE
  - `scale_service`: Show API response: "Scaled from 2 to 4 instances"
  - `log_to_elasticsearch`: Show success message

---

## 5:45-6:15 - Key Takeaways

**Verbal:**
- "Here's what makes this powerful..."
- List 3 key takeaways

**Visual:**
- Optionally show bullet points on screen:
  - Business-aware automation
  - Hybrid pattern (ES|QL + Deterministic + AI)
  - Production-ready (error handling, audit logging)
- Show final workflow execution summary

---

## 6:15-6:30 - CTA (Tech Preview Timing, Workshop Coming Soon)

**Verbal:**
- "Elastic Workflows enters tech preview in early 2025."
- "We're building a comprehensive hands-on workshop..."
- "Follow us for updates—links are in the description."
- "Questions? Drop them in the comments. Thanks for watching!"

**Visual:**
- Show end card with:
  - Elastic Workflows logo/text
  - "Tech Preview: Early 2025"
  - "Workshop Coming Soon"
  - Social links / subscribe button
- Optionally show workshop preview image

---

## Production Notes

**Pacing:**
- Move quickly through UI navigation
- Slow down for code explanation (ES|QL query, Liquid templates)
- Use time-lapse or fast-forward for waiting periods (alert firing, AI agent response)

**Visual Enhancements:**
- Use cursor highlighting or zoom for small UI elements
- Add text overlays for key concepts (e.g., "ES|QL Multi-Metric Query", "Deterministic Logic", "AI Explanation")
- Consider split-screen showing code and execution results side-by-side

**Audio:**
- Clear, enthusiastic tone
- Pause briefly after key concepts for emphasis
- Background music optional but keep it subtle

**Editing:**
- Add chapter markers in YouTube:
  - 0:00 - Introduction
  - 1:00 - Use Case
  - 2:00 - ES|QL Query
  - 3:00 - AI Explanation
  - 3:45 - Deterministic Logic
  - 5:00 - Demo
  - 6:15 - Wrap-Up

**Description Box:**
- Include disclaimer about tech preview
- Link to Elastic Workflows documentation (when available)
- Link to workshop signup/updates
- Timestamps for each section
- Related videos (if available)

