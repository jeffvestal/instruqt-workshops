---
slug: 08-business-impact-detection
id: business-impact-detection-001
type: challenge
title: 'Capstone: Detect Business Impact with Automation'
teaser: Build a complete workflow from scratch that detects business-critical issues
tabs:
- id: tab-workflows
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: tab-discover
  title: Kibana - Discover
  type: service
  hostname: kubernetes-vm
  path: /app/discover
  port: 30001
- id: tab-terminal
  title: Terminal
  type: terminal
  hostname: host-1
- id: tab-docs
  title: Documentation
  type: website
  url: https://www.elastic.co/guide/en/kibana/current/workflows.html
difficulty: advanced
timelimit: 2400
---

# 📖 Challenge 8: Capstone - Detect Business Impact with Automation

Congratulations! You've learned the fundamentals of workflows, AI orchestration, and alert-driven automation. Now it's time to put it all together and build something **you design from scratch**.

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

## Step 1: Create Your Alert Rule

First, you need to create an alert that fires when `payment-service` is experiencing 5xx errors. This alert is already pre-created for you during the lab setup.

### Alert Rule Name

The alert is named: `business-impact-payment-degradation`

### Inspect the Alert

1. In the [button label="Kibana - Workflows"](tab-0) tab, navigate to **Observability > Alerts > Rules**.
2. Find and click on the `business-impact-payment-degradation` rule.
3. Inspect its configuration. Notice that it's a simple technical alert (looking for 5xx errors on `payment-service`), without any complex business logic.

### Configure the Workflow Action

Now, you need to configure this alert to trigger your workflow:

1. Click **Actions** in the top right, then **Edit**.
2. Scroll down to the **Actions** section and click `Add action`.
3. Select **Workflows**.
4. In the **Select Workflows** dropdown, choose `business_impact_detector`.
5. Scroll down and click **Save rule**.

---

## Step 2: Build Your Workflow

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

### 2.1 ES|QL Building Blocks

To keep the focus on orchestration (not wrestling with aggregations), here are the ES|QL query steps you can use directly in your workflow. Your job is to wire them together, compute the scaling decision deterministically, call the AI agent for explanation, and take action.

#### Step: `get_error_rate`

Add this step to query the error count:

```yaml
- name: get_error_rate
  type: elasticsearch.esql.query
  with:
    query: >
      FROM o11y-heartbeat
      | WHERE service.name == "payment-service"
        AND @timestamp >= NOW() - 5 MINUTES
        AND http.status_code >= 500
      | STATS error_count = COUNT(*)
```

This produces a single row with `error_count`. Access it in later steps as:
- `steps.get_error_rate.output.data[0].error_count`

#### Step: `get_payment_metrics`

Add this step to query current payment transaction metrics:

```yaml
- name: get_payment_metrics
  type: elasticsearch.esql.query
  with:
    query: >
      FROM o11y-heartbeat
      | WHERE service.name == "payment-service"
        AND @timestamp >= NOW() - 5 MINUTES
        AND transaction.status == "success"
      | STATS
          payment_count = COUNT(*),
          total_amount = SUM(transaction.amount)
```

Access the values as:
- `steps.get_payment_metrics.output.data[0].payment_count`
- `steps.get_payment_metrics.output.data[0].total_amount`

#### Step: `get_baseline_metrics`

Add this step to get the baseline payment count from the previous hour (for comparison):

```yaml
- name: get_baseline_metrics
  type: elasticsearch.esql.query
  with:
    query: >
      FROM o11y-heartbeat
      | WHERE service.name == "payment-service"
        AND @timestamp >= NOW() - 65 MINUTES
        AND @timestamp < NOW() - 5 MINUTES
        AND transaction.status == "success"
      | STATS baseline_payment_count = COUNT(*)
```

Access it as:
- `steps.get_baseline_metrics.output.data[0].baseline_payment_count`

### 2.2 Compute the Payment Drop and Decide to Scale

Using the ES|QL results, compute whether the payment drop is significant enough to trigger scaling.

**Concept**: Calculate `payment_drop_pct` as approximately `(1 - current_payment_count / baseline_payment_count) * 100`.

**Decision Logic**: 
- If `payment_drop_pct > 30%`, trigger scaling
- Otherwise, log the incident but don't scale

You can implement this in one of two ways:
1. **Compute in Liquid** (in a console step): Calculate the percentage and store it in a variable
2. **Use a simple threshold in an `if` condition**: Compare `current_payment_count` directly to `baseline_payment_count` (e.g., `current_payment_count < 0.7 * baseline_payment_count`)

The scaling decision should be **deterministic** based on these numeric thresholds, not based on AI output.

### 2.3 Add AI Explanation of Business Impact

After computing the metrics and making the scaling decision, call the AI agent to explain the business impact in human language:

```yaml
- name: ai_business_summary
  type: kibana.post_agent_builder_converse
  with:
    agent_id: agent_business_slo
    input: |
      Here are the current metrics for payment-service:
      - Error count (last 5m): {{ steps.get_error_rate.output.data[0].error_count }}
      - Current successful payments (last 5m): {{ steps.get_payment_metrics.output.data[0].payment_count }}
      - Baseline successful payments (previous hour): {{ steps.get_baseline_metrics.output.data[0].baseline_payment_count }}

      The workflow will decide whether to scale based on numeric thresholds.
      Your job is to explain the business impact in 2–3 sentences for an SRE and business audience.
      Do not decide whether to scale; only explain impact and suggest follow-up checks.
```

**Important**: The AI agent is used for **explanation only**. The workflow makes the scaling decision deterministically based on the numeric thresholds you computed.

### 2.4 Simulate Sending a Notification

You can add a console step that simulates sending an email notification to stakeholders:

```yaml
- name: notify_stakeholder
  type: console
  with:
    message: |
      [EMAIL] To: sre-team@example.com
      Subject: Payment service impact detected

      {{ steps.ai_business_summary.output.response.message }}
```

This is just for demonstration. In production, you would use an email or Slack connector.

### 2.5 Wire It All Together

We've given you the ES|QL building blocks for metrics. Your job is to wire them together: compute whether the drop is big enough to scale (using deterministic thresholds), call the AI agent for explanation, call the mock API to scale if needed, and log everything to Elasticsearch for auditing.

**Required Steps Summary**:

1. **Parse alert data** - Extract service name from alert payload
2. **Query error rate** - Use the `get_error_rate` ES|QL step above
3. **Query payment metrics** - Use the `get_payment_metrics` ES|QL step above
4. **Query baseline metrics** - Use the `get_baseline_metrics` ES|QL step above
5. **Compute scaling decision** - Deterministically decide if scaling is needed
6. **AI explanation** - Call `agent_business_slo` to explain business impact
7. **Conditional logic** - If scaling needed, proceed to API call
8. **Scale service** - HTTP POST to `http://host-1:3000/scale_service` (if needed)
9. **Error handling** - Retry logic for API calls
10. **Audit log** - Index decision and results to Elasticsearch

## Step 3: Test Your Workflow

1. **Trigger the incident**:
   ```bash
   bash /opt/workshop-assets/setup_scripts/06-trigger-business-incident.sh
   ```

2. **Wait for alert to fire** (check Observability > Alerts)

3. **Verify workflow execution**:
   - Check workflow execution history
   - Verify scaling action was logged
   - Check mock API logs: `pm2 logs mock-api --lines 20`

4. **Check audit log**:
   - In Kibana Discover, search index: `business_actions-*`
   - Verify your workflow action was logged

## Step 4: Validate Your Solution

Run the check script to validate your implementation:

```bash
/opt/workshop-assets/solve-08-business-impact-detection
```

This will verify:
- ✅ Workflow exists with correct name
- ✅ Alert trigger configured
- ✅ Required steps present
- ✅ Alert rule created
- ✅ Workflow executes successfully

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
  # Step 1: Parse service name from alert
  - name: get_service_name
    type: console
    with:
      message: |
        {% assign esQuery = event.alerts[0].rule.parameters.esQuery | json_parse %}
        Alert '{{ event.alerts[0].rule.name }}' fired!
        Service: {{ esQuery.query.bool.must[0].term['service.name'] }}
        Alert ID: {{ event.alerts[0].id }}

  # Step 2: Query error rate using ES|QL
  - name: get_error_rate
    type: elasticsearch.esql.query
    with:
      query: >
        FROM o11y-heartbeat
        | WHERE service.name == "payment-service"
          AND @timestamp >= NOW() - 5 MINUTES
          AND http.status_code >= 500
        | STATS error_count = COUNT(*)

  # Step 3: Query payment transaction metrics using ES|QL
  - name: get_payment_metrics
    type: elasticsearch.esql.query
    with:
      query: >
        FROM o11y-heartbeat
        | WHERE service.name == "payment-service"
          AND @timestamp >= NOW() - 5 MINUTES
          AND transaction.status == "success"
        | STATS
            payment_count = COUNT(*),
            total_amount = SUM(transaction.amount)

  # Step 4: Get baseline for comparison (previous hour) using ES|QL
  - name: get_baseline_metrics
    type: elasticsearch.esql.query
    with:
      query: >
        FROM o11y-heartbeat
        | WHERE service.name == "payment-service"
          AND @timestamp >= NOW() - 65 MINUTES
          AND @timestamp < NOW() - 5 MINUTES
          AND transaction.status == "success"
        | STATS baseline_payment_count = COUNT(*)

  # Step 5: Compute payment drop percentage deterministically
  - name: compute_payment_drop
    type: console
    with:
      message: |-
        {% assign current = steps.get_payment_metrics.output.data[0].payment_count %}
        {% assign baseline = steps.get_baseline_metrics.output.data[0].baseline_payment_count %}
        {% assign drop_pct = baseline | minus: current | times: 100.0 | divided_by: baseline %}
        Payment drop: {{ drop_pct | round: 2 }}%
        Current: {{ current }}, Baseline: {{ baseline }}

  # Step 6: Call AI agent for business impact explanation
  - name: ai_business_summary
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_business_slo
      input: |
        Here are the current metrics for payment-service:
        - Error count (last 5m): {{ steps.get_error_rate.output.data[0].error_count }}
        - Current successful payments (last 5m): {{ steps.get_payment_metrics.output.data[0].payment_count }}
        - Baseline successful payments (previous hour): {{ steps.get_baseline_metrics.output.data[0].baseline_payment_count }}

        The workflow will decide whether to scale based on numeric thresholds.
        Your job is to explain the business impact in 2–3 sentences for an SRE and business audience.
        Do not decide whether to scale; only explain impact and suggest follow-up checks.
    on-failure:
      retry:
        max-attempts: 2
        delay: 1s

  # Step 7: Simulate notification (optional)
  - name: notify_stakeholder
    type: console
    with:
      message: |
        [EMAIL] To: sre-team@example.com
        Subject: Payment service impact detected

        {{ steps.ai_business_summary.output.response.message }}

  # Step 8: Conditional logic - check if scaling needed (deterministic decision)
  - name: check_scaling_needed
    type: if
    condition: "${{ steps.get_payment_metrics.output.data[0].payment_count < steps.get_baseline_metrics.output.data[0].baseline_payment_count * 0.7 }}"
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
          message: "⚠️ AI recommended no scaling action. Manual investigation may be needed."

  # Step 8: Audit log to Elasticsearch
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
        error_count: "{{ steps.get_error_rate.output.data[0].error_count }}"
        current_payment_count: "{{ steps.get_payment_metrics.output.data[0].payment_count }}"
        baseline_payment_count: "{{ steps.get_baseline_metrics.output.data[0].baseline_payment_count }}"
        ai_explanation: "{{ steps.ai_business_summary.output.response.message }}"
        action_taken: "{{ steps.scale_service.output.data.action | default: 'no_action' }}"
        scaling_result: "{{ steps.scale_service.output.data.new_instances | default: 'N/A' }}"
```

</details>

## What You've Built

Congratulations! You've created a complete **business-critical automation system** that:

- ✅ Uses ES|QL to query technical AND business metrics efficiently
- ✅ Makes deterministic scaling decisions based on numeric thresholds
- ✅ Uses AI to explain business impact in human language
- ✅ Takes automated remediation actions when needed
- ✅ Maintains a complete audit trail

This is real-world automation that bridges the gap between observability and business outcomes, using ES|QL for fast data access and AI for clear communication.

**Click "Next" to see a summary of everything you've learned!**

