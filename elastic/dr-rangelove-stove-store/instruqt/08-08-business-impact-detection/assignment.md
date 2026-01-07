---
slug: 08-business-impact-detection
id: eupnushaagfr
type: challenge
title: 'Capstone: Detect Business Impact with Automation'
teaser: Build a complete workflow from scratch that detects business-critical issues
tabs:
- id: yomtiegrqsmi
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: 7wmw8dvh87fw
  title: Kibana - Alerts
  type: service
  hostname: kubernetes-vm
  path: /app/observability/alerts
  port: 30001
- id: jdbzzjvuswqv
  title: Kibana - Discover
  type: service
  hostname: kubernetes-vm
  path: /app/discover
  port: 30001
- id: qh7f07uf14qd
  title: Terminal
  type: terminal
  hostname: kubernetes-vm
- id: esjvv2gabwdg
  title: Documentation
  type: website
  url: https://www.elastic.co/guide/en/kibana/current/workflows.html
difficulty: advanced
timelimit: 2400
enhanced_loading: null
---
# 📖 Challenge 8: Capstone - Build a Business Impact Detection System

Congratulations! You've learned workflows, AI orchestration, and alert-driven automation. Now it's time to **put it all together**.

This challenge is different: instead of copy-pasting complete YAML, you'll **assemble** the workflow using patterns and hints from earlier challenges. This is closer to real-world development.

## The Scenario: Revenue at Risk

Your `payment-service` is experiencing degradation that's affecting your bottom line:

- **Technical symptoms**: Error rates have spiked to 15-20%
- **Business impact**: Successful payment transactions have dropped by 40%
- **Revenue loss**: Average transaction amounts are down 30% (high-value payments failing)

This isn't just a technical alert—it's a **business-critical incident** that requires immediate action.

## Your Mission

Build a workflow that:

1. **Triggers automatically** from an alert on `payment-service` errors
2. **Uses ES|QL** to query Elasticsearch for error rate and payment transaction metrics
3. **Determines, deterministically**, whether payment volume has dropped enough to trigger scaling (e.g., payment_drop_pct > 30%)
4. **Calls an AI Agent Builder agent** (`agent_business_slo`) to **explain the business impact** in human language
5. **Simulates notifying a stakeholder** (e.g., email-style console output)
6. **Indexes an audit record** of what happened

The decision to scale is based on simple numeric thresholds (e.g., payment_drop_pct > 30%) using metrics from Elasticsearch. The AI agent is used to explain the impact and recommended follow-ups, not to make the final scaling decision.

## Step 1: Inspect the Pre-Created Alert

An alert rule has been created for you during lab setup. Let's inspect it to understand what triggers your workflow.

### Alert Rule Name

The alert is named: `business-impact-payment-degradation`

### Inspect the Alert

1. Click the [button label="Kibana - Alerts"](tab-1) tab.
2. Click on **Manage Rules** in the upper right corner.
3. Find and click on the `business-impact-payment-degradation` rule.
4. Inspect its configuration under the **Definition** section.
   - Notice that it's a simple technical alert:
   - It fires when `payment-service` has 5xx errors in the last 5 minutes (the workflow uses a 1-minute window for more precise detection).

This is intentionally simple—the **workflow** will add the business logic.

---

## Step 2: Build Your Workflow

Go back to [button label="Kibana - Workflows"](tab-0) tab.

Create a new workflow named `business_impact_detector`.

### Starter Template

Here's your starting point—fill in the steps:

```yaml
version: "1"
name: business_impact_detector
description: "Detect and respond to business-critical payment service degradation"
enabled: true

inputs: []

triggers:
  - type: alert

steps:
  # TODO: Add your steps here
```

---

### 2.1 Get All Metrics in One Query

Instead of making three separate ES|QL queries, we can efficiently query all the metrics we need in a single query. This demonstrates ES|QL's power to handle multiple time windows and aggregations efficiently.

Create an ES|QL step named `get_all_metrics` that returns:
- Error count (5xx errors in last 1 minute)
- Current payment count (successful payments in last 1 minute)
- Current total amount (sum of successful payment amounts in last 1 minute)
- Baseline payment count (successful payments from 61 minutes ago to 1 minute ago)

**ES|QL Query:**
```esql
FROM o11y-heartbeat
| WHERE service.name == "payment-service"
| WHERE @timestamp >= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 3660 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}"
  AND @timestamp <= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp }}"
| EVAL
    is_in_current_window = @timestamp >= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
    is_in_baseline_window = @timestamp < "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
    is_error = CASE(http.status_code >= 500 AND is_in_current_window == true, 1, 0),
    is_current_success = CASE(transaction.status == "success" AND is_in_current_window == true, 1, 0),
    is_baseline_success = CASE(transaction.status == "success" AND is_in_baseline_window == true, 1, 0),
    current_amount = CASE(is_current_success == 1, transaction.amount, 0)
| STATS
    error_count = SUM(is_error),
    current_payment_count = SUM(is_current_success),
    current_total_amount = SUM(current_amount),
    baseline_payment_count = SUM(is_baseline_success)
```

**How ES|QL works here:**
- `EVAL` creates boolean flags for each time window and condition
- `CASE` expressions evaluate to 1 (match) or 0 (no match) for each document
- `STATS` sums these flags to get counts across all documents
- This single query efficiently processes multiple time windows without separate queries

**Access results:**
- `steps.get_all_metrics.output.values[0][0]` = error_count
- `steps.get_all_metrics.output.values[0][1]` = current_payment_count
- `steps.get_all_metrics.output.values[0][2]` = current_total_amount
- `steps.get_all_metrics.output.values[0][3]` = baseline_payment_count

**Pattern:** All ES|QL results are in `.output.values` as an array of arrays. The first result's columns are accessed as `[0][0]`, `[0][1]`, `[0][2]`, `[0][3]`.

<details>
<summary>Click here for the solution to this step</summary>

```yaml
- name: get_all_metrics
  type: elasticsearch.esql.query
  with:
    query: >
      FROM o11y-heartbeat
      | WHERE service.name == "payment-service"
      | WHERE @timestamp >= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 3660 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}"
        AND @timestamp <= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp }}"
      | EVAL
          is_in_current_window = @timestamp >= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
          is_in_baseline_window = @timestamp < "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
          is_error = CASE(http.status_code >= 500 AND is_in_current_window == true, 1, 0),
          is_current_success = CASE(transaction.status == "success" AND is_in_current_window == true, 1, 0),
          is_baseline_success = CASE(transaction.status == "success" AND is_in_baseline_window == true, 1, 0),
          current_amount = CASE(is_current_success == 1, transaction.amount, 0)
      | STATS
          error_count = SUM(is_error),
          current_payment_count = SUM(is_current_success),
          current_total_amount = SUM(current_amount),
          baseline_payment_count = SUM(is_baseline_success)
```

</details>

---

### 2.2 Explain Impact and Notify Stakeholders

Call an AI agent to explain the business impact in human language, then simulate sending a notification email.

**Part 1: AI Explanation**

Call the `agent_business_slo` agent to explain the impact. The AI doesn't make the scaling decision—it just summarizes the impact for stakeholders.

- Step type: `onechat.runAgent`
- Agent ID: `agent_business_slo`
- Message: Pass the metrics from `get_all_metrics` (error count, current payment count, baseline payment count) and ask the agent to explain the impact in 2–3 sentences.
- Add retry logic: `on-failure: retry:` with `max-attempts: 2` and `delay: 1s`

**Part 2: Notification**

Add a `console` step that simulates sending an email with the AI's explanation.

**Accessing the AI response:**
`steps.<your_step_name>.output.response.message`

**Important**: The AI agent is used for **explanation only**. Your workflow makes the scaling decision deterministically.

<details>
<summary>Click here for the solution to this step</summary>

```yaml
- name: ai_business_summary
  type: kibana.post_agent_builder_converse
  with:
    agent_id: agent_business_slo
    input: |
      Here are the current metrics for payment-service:
      - Error count (last 1m): {{ steps.get_all_metrics.output.values[0][0] }}
      - Current successful payments (last 1m): {{ steps.get_all_metrics.output.values[0][1] }}
      - Baseline successful payments (previous 60m total): {{ steps.get_all_metrics.output.values[0][3] }}

      For context: The baseline covers 60 minutes, so to compare to the 1-minute current window,
      the normalized baseline rate would be approximately {{ steps.get_all_metrics.output.values[0][3] | divided_by: 60 | round }} payments per minute.

      Calculate the percentage drop: if current is significantly below the normalized baseline (drop >= 30%),
      this indicates a business-critical issue affecting revenue.

      Your job is to explain the business impact in 2–3 sentences for an SRE and business audience.
      Focus on: Is revenue at risk? What might be the cause? What should teams investigate?
      Do not decide whether to scale; only explain impact and suggest follow-up checks.
  on-failure:
    retry:
      max-attempts: 2
      delay: 1s

- name: notify_stakeholder
  type: console
  with:
    message: |
      [EMAIL] To: sre-team@example.com
      Subject: Payment service impact detected

      {{ steps.ai_business_summary.output.response.message }}
```

</details>

---

### 2.3 Make Scaling Decision and Act

Use conditional logic to check if scaling is needed, then call the scaling API if the payment drop exceeds the threshold.

Create an `if` step that checks if the current payment count is below 70% of the normalized baseline. The baseline covers 60 minutes, so normalize it to a 1-minute equivalent for comparison.

**Decision Logic:**
- Normalize baseline: `baseline_total / 60` (60 minutes ÷ 1 minute = 60)
- Calculate threshold: `normalized_baseline * 0.7` (70% of baseline)
- If `current_payment_count < threshold`, trigger scaling
- Otherwise, log that no scaling action was taken

**Inside the `if` block:**
- Call the scaling API: HTTP POST to `http://host-1:3000/scale_service` with `service_name: "payment-service"` in the body
- Add retry logic: `on-failure: retry:` with `max-attempts: 2` and `delay: 1s`
- Log the scaling action with a console step showing the scaling result

**In the `else` block:**
- Log that no scaling action was taken

**Hints:**
- From Challenge 7: You know how to call HTTP APIs with retry logic
- From Challenge 4: You know how to use `if` conditions for branching logic
- Use `steps.get_all_metrics.output.values[0][1]` for current payment count
- Use `steps.get_all_metrics.output.values[0][3]` for baseline payment count

<details>
<summary>Click here for the solution to this step</summary>

```yaml
- name: check_scaling_needed
  type: if
  condition: "steps.get_all_metrics.output.values.0.1 < {% assign baseline = steps.get_all_metrics.output.values[0][3] | plus: 0 %}{% assign threshold = baseline | divided_by: 60 | times: 0.7 | round %}{{ threshold }}"
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
      on-failure:
        retry:
          max-attempts: 2
          delay: 1s

    - name: log_scaling_action
      type: console
      with:
        message: |
          ✅ Auto-scaling triggered!
          {{ steps.scale_service.output.data.message }}
          Previous instances: {{ steps.scale_service.output.data.previous_instances }}
          New instances: {{ steps.scale_service.output.data.new_instances }}
  else:
    - name: log_no_scaling
      type: console
      with:
        message: |
          ⚠️ No scaling action needed. Manual investigation may be required.

          📊 Debug Info:
          - Current payments (1m): {{ steps.get_all_metrics.output.values[0][1] }}
          - Baseline payments (60m): {{ steps.get_all_metrics.output.values[0][3] }}
          - Threshold (70% of baseline/min): {% assign baseline = steps.get_all_metrics.output.values[0][3] | plus: 0 %}{{ baseline | divided_by: 60 | times: 0.7 | round }}
```

</details>

---

### 2.4 Write Audit Log

Index a complete audit record of the workflow execution to Elasticsearch for compliance and analysis.

Create an `elasticsearch.index` step that writes all the key metrics, AI explanation, and action taken to an index named `business_actions-<date>`.

**Index name pattern:** Use `business_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}`

**Document should include:**
- Timestamp, workflow name, alert info
- Error count, payment counts (current and baseline)
- AI explanation
- Action taken and scaling result

**Hints:**
- From Challenge 6: You know how to index audit logs to Elasticsearch
- Use `{{ execution.id }}` as the document ID
- Use `default: 'no_action'` or `default: 'N/A'` for fields that might not exist if scaling didn't happen
- Reference metrics from `steps.get_all_metrics.output.values[0][X]`:
  - `[0][0]` = error_count
  - `[0][1]` = current_payment_count
  - `[0][3]` = baseline_payment_count

<details>
<summary>Click here for the solution to this step</summary>

```yaml
- name: log_to_elasticsearch
  type: elasticsearch.index
  with:
    index: "business_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}"
    id: "{{ execution.id }}"
    document:
      timestamp: "{{ execution.startedAt }}"
      workflow_name: "business_impact_detector"
      alert_id: "{{ event.alerts[0].id }}"
      alert_name: "{{ event.alerts[0].rule.name }}"
      service_name: "payment-service"
      error_count: "{{ steps.get_all_metrics.output.values[0][0] }}"
      current_payment_count: "{{ steps.get_all_metrics.output.values[0][1] }}"
      baseline_payment_count: "{{ steps.get_all_metrics.output.values[0][3] }}"
      ai_explanation: "{{ steps.ai_business_summary.output.response.message }}"
      action_taken: "{{ steps.scale_service.output.data.action | default: 'no_action' }}"
      scaling_result: "{{ steps.scale_service.output.data.new_instances | default: 'N/A' }}"
```

</details>

---

## Step 3: Configure the Alert to Trigger Your Workflow

Now that your workflow exists, wire it to the alert:

1. Click the [button label="Kibana - Alerts"](tab-1) tab.
2. Find the `business-impact-payment-degradation` rule and click it.
3. Click **Actions** (top right), then **Edit**.
4. Scroll to **Actions** section and click **Add action**
5. Select **Workflows**
6. Choose `business_impact_detector` from the dropdown
7. Click **Save rule**

Your workflow is now connected to the alert!

---

## Step 4: Test Your Workflow

Before triggering a real incident, test your workflow using Kibana's test feature.

1. In the [button label="Kibana - Workflows"](tab-0) tab, open your `business_impact_detector` workflow
2. Click the **Run** button (top right)
3. Select **"Test with alert data"** from the dropdown
4. Choose one of the recent alert instances from the list (you should see `business-impact-payment-degradation` alerts)
5. Click **Run**
6. Watch the execution and verify:
   - ✅ All ES|QL queries return data
   - ✅ Payment drop percentage is calculated
   - ✅ AI explanation is generated
   - ✅ Scaling decision is made correctly
   - ✅ Audit log is written

If any step fails, review the error message and fix your workflow YAML.
> [!NOTE]
> We haven't triggered an incident, yet. So it is ok if the decision is to NOT scale up.

---

## Step 5: Validate Your Solution

1. Open the [button label="Terminal"](tab-3) tab
2. click `▶️ run` on the code box below
    - This will run the check script to validate your implementation:

```bash,run
/opt/workshop-assets/setup_scripts/solve-08-business-impact-detection
```

This will verify:
- ✅ Workflow exists with correct name
- ✅ Alert trigger configured
- ✅ Required steps present
- ✅ Alert rule created
- ✅ Workflow structure is correct

---

## Step 6: Test End-to-End (Optional)

Want to see the full automation in action with real data? Trigger a business incident!

1. Open the [button label="Terminal"](tab-3) tab
2. click `▶️ run` on the code box below
1. **Trigger the incident**:
   ```bash,run
   bash /opt/workshop-assets/setup_scripts/06-trigger-business-incident.sh
   ```
2. **Wait for alert to fire** (~1-2 minutes) - check [button label="Kibana - Alerts"](tab-1)
3. **Verify workflow was triggered automatically**:
   - Check workflow execution history in [button label="Kibana - Workflows"](tab-0)
   - Verify scaling action was logged

4. **Check the mock API** (optional):
   ```bash
   # Check if the mock API received the scaling request
   curl -s http://host-1:3000/health | jq .
   ```
   > **Note**: The mock API runs on `host-1`. If you want to see pm2 logs, SSH to host-1: `ssh host-1` then run `pm2 logs mock-api --lines 20`

5. **View the audit trail**:
   - In [button label="Kibana - Discover"](tab-2), search index: `business_actions-*`
   - Verify your workflow action was logged with all metrics

---

<details>
<summary>Show Solution: Complete Workflow</summary>

```yaml
version: "1"
name: business_impact_detector
description: "Detect and respond to business-critical payment service degradation"
enabled: true

inputs: []

triggers:
  - type: alert

steps:
  # Step 1: Get all metrics in one efficient ES|QL query
  # Uses deterministic time windows based on alert execution timestamp
  - name: get_all_metrics
    type: elasticsearch.esql.query
    with:
      query: >
        FROM o11y-heartbeat
        | WHERE service.name == "payment-service"
        | WHERE @timestamp >= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 3660 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}"
          AND @timestamp <= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp }}"
        | EVAL
            is_in_current_window = @timestamp >= "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
            is_in_baseline_window = @timestamp < "{{ event.alerts[0].kibana.alert.rule.execution.timestamp | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
            is_error = CASE(http.status_code >= 500 AND is_in_current_window == true, 1, 0),
            is_current_success = CASE(transaction.status == "success" AND is_in_current_window == true, 1, 0),
            is_baseline_success = CASE(transaction.status == "success" AND is_in_baseline_window == true, 1, 0),
            current_amount = CASE(is_current_success == 1, transaction.amount, 0)
        | STATS
            error_count = SUM(is_error),
            current_payment_count = SUM(is_current_success),
            current_total_amount = SUM(current_amount),
            baseline_payment_count = SUM(is_baseline_success)

  # Step 2: Call AI agent for business impact explanation
  - name: ai_business_summary
    type: onechat.runAgent
    with:
      agent_id: agent_business_slo
      message: |
        Here are the current metrics for payment-service:
        - Error count (last 1m): {{ steps.get_all_metrics.output.values[0][0] }}
        - Current successful payments (last 1m): {{ steps.get_all_metrics.output.values[0][1] }}
        - Baseline successful payments (previous 60m total): {{ steps.get_all_metrics.output.values[0][3] }}

        For context: The baseline covers 60 minutes, so to compare to the 1-minute current window,
        the normalized baseline rate would be approximately {{ steps.get_all_metrics.output.values[0][3] | divided_by: 60 | round }} payments per minute.

        Calculate the percentage drop: if current is significantly below the normalized baseline (drop >= 30%),
        this indicates a business-critical issue affecting revenue.

        Your job is to explain the business impact in 2–3 sentences for an SRE and business audience.
        Focus on: Is revenue at risk? What might be the cause? What should teams investigate?
        Do not decide whether to scale; only explain impact and suggest follow-up checks.
    on-failure:
      retry:
        max-attempts: 2
        delay: 1s

  # Step 3: Simulate notification
  - name: notify_stakeholder
    type: console
    with:
      message: |
        [EMAIL] To: sre-team@example.com
        Subject: Payment service impact detected

        {{ steps.ai_business_summary.output.response.message }}

  # Step 4: Conditional logic - check if scaling needed (deterministic decision)
  # Uses KQL field comparison with computed threshold (70% of normalized baseline)
  - name: check_scaling_needed
    type: if
    condition: "steps.get_all_metrics.output.values.0.1 < {% assign baseline = steps.get_all_metrics.output.values[0][3] | plus: 0 %}{% assign threshold = baseline | divided_by: 60 | times: 0.7 | round %}{{ threshold }}"
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
        on-failure:
          retry:
            max-attempts: 2
            delay: 1s

      - name: log_scaling_action
        type: console
        with:
          message: |
            ✅ Auto-scaling triggered!
            {{ steps.scale_service.output.data.message }}
            Previous instances: {{ steps.scale_service.output.data.previous_instances }}
            New instances: {{ steps.scale_service.output.data.new_instances }}
    else:
      - name: log_no_scaling
        type: console
        with:
          message: |
            ⚠️ No scaling action needed. Manual investigation may be required.

            📊 Debug Info:
            - Current payments (1m): {{ steps.get_all_metrics.output.values[0][1] }}
            - Baseline payments (60m): {{ steps.get_all_metrics.output.values[0][3] }}
            - Threshold (70% of baseline/min): {% assign baseline = steps.get_all_metrics.output.values[0][3] | plus: 0 %}{{ baseline | divided_by: 60 | times: 0.7 | round }}

  # Step 5: Audit log to Elasticsearch
  - name: log_to_elasticsearch
    type: elasticsearch.index
    with:
      index: "business_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}"
      id: "{{ execution.id }}"
      document:
        timestamp: "{{ execution.startedAt }}"
        workflow_name: "business_impact_detector"
        alert_id: "{{ event.alerts[0].id }}"
        alert_name: "{{ event.alerts[0].rule.name }}"
        service_name: "payment-service"
        error_count: "{{ steps.get_all_metrics.output.values[0][0] }}"
        current_payment_count: "{{ steps.get_all_metrics.output.values[0][1] }}"
        baseline_payment_count: "{{ steps.get_all_metrics.output.values[0][3] }}"
        ai_explanation: "{{ steps.ai_business_summary.output.response.message }}"
        action_taken: "{{ steps.scale_service.output.data.action | default: 'no_action' }}"
        scaling_result: "{{ steps.scale_service.output.data.new_instances | default: 'N/A' }}"
```

</details>

---

## What You've Built

Congratulations! You've **designed and built from scratch** a complete **business-critical automation system** that:

- ✅ Uses ES|QL to query technical AND business metrics efficiently
- ✅ Makes deterministic scaling decisions based on numeric thresholds
- ✅ Uses AI to explain business impact in human language
- ✅ Takes automated remediation actions when needed
- ✅ Maintains a complete audit trail

This is **real-world automation** that bridges the gap between observability and business outcomes, combining ES|QL for fast data access, deterministic logic for reliable decisions, and AI for clear stakeholder communication.

You've gone from "copy-paste learning" in earlier challenges to **designing and assembling** a complete production-ready workflow. Well done!

**Click "Next" to see a summary of everything you've learned!**
