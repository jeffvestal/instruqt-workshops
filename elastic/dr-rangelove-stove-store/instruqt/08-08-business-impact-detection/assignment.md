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

1. **Triggers automatically** from an alert rule YOU create
2. **Queries Elasticsearch** to analyze both error rates AND payment transaction metrics
3. **Calls an AI agent** (`agent_business_slo`) to assess business impact
4. **Makes a decision**: If payment drop >30%, trigger auto-scaling
5. **Calls the mock API** (`/scale_service`) to scale up the service
6. **Logs everything** to Elasticsearch for audit and analysis

## Step 1: Create Your Alert Rule

First, you need to create an alert that fires when BOTH conditions are met:
- High error rate (HTTP 5xx status codes)
- AND payment transaction drop

### Alert Requirements

**Rule Type**: `.es-query`

**Query Logic**:
- Filter: `service.name: "payment-service"`
- Condition 1: `http.status_code >= 500` (error rate threshold)
- Condition 2: Count of `transaction.status: "success"` drops significantly

**Time Window**: Compare last 5 minutes vs previous 1 hour baseline

**Tip**: Use Kibana's Alerting UI to create this rule, or use the API. The alert should fire when payment success rate drops below 60% (normal is ~95%).

### Alert Rule Name
Name your alert: `business-impact-payment-degradation`

<details>
<summary>Show Solution: Alert Rule Creation</summary>

### Option 1: Via Kibana UI

1. Navigate to **Observability > Alerts > Rules**
2. Click **Create rule**
3. Select **Elasticsearch query**
4. Configure:
   - **Index**: `o11y-heartbeat`
   - **Time field**: `@timestamp`
   - **Query**:
   ```json
   {
     "bool": {
       "must": [
         {"term": {"service.name": "payment-service"}},
         {"range": {"http.status_code": {"gte": 500}}}
       ],
       "should": [
         {"term": {"transaction.status": "success"}}
       ],
       "minimum_should_match": 1
     }
   }
   ```
   - **Threshold**: Count < 50 (adjust based on your data volume)
   - **Time window**: Last 5 minutes
5. Save as `business-impact-payment-degradation`

### Option 2: Via API

```bash
curl -X POST "${KIBANA_URL}/api/alerting/rule" \
  -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "name": "business-impact-payment-degradation",
    "rule_type_id": ".es-query",
    "consumer": "alerts",
    "schedule": {"interval": "1m"},
    "params": {
      "index": ["o11y-heartbeat"],
      "timeField": "@timestamp",
      "esQuery": "{\"bool\":{\"must\":[{\"term\":{\"service.name\":\"payment-service\"}},{\"range\":{\"http.status_code\":{\"gte\":500}}}]}}",
      "threshold": [50],
      "thresholdComparator": "<",
      "size": 100,
      "timeWindowSize": 5,
      "timeWindowUnit": "m"
    },
    "enabled": true
  }'
```

</details>

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

### Required Steps

Your workflow must include:

1. **Parse alert data** - Extract service name from alert payload
2. **Query error rate** - Elasticsearch query for HTTP 5xx errors for payment-service
3. **Query payment metrics** - Elasticsearch query for successful payment transaction count
4. **AI analysis** - Call `agent_business_slo` with error rate and payment data
5. **Conditional logic** - If payment drop >30%, proceed to scaling
6. **Scale service** - HTTP POST to `http://host-1:3000/scale_service`
7. **Error handling** - Retry logic for API calls
8. **Audit log** - Index decision and results to Elasticsearch

### Step Hints

**Step 1: Parse Service Name**
```yaml
- name: get_service_name
  type: console
  with:
    message: |
      {% assign esQuery = event.alerts[0].rule.parameters.esQuery | json_parse %}
      Service: {{ esQuery.query.bool.must[0].term['service.name'] }}
```

**Step 2 & 3: Elasticsearch Queries**
- Use `elasticsearch.search` step type
- Query `o11y-heartbeat` index
- Filter by `service.name: "payment-service"`
- For payments: Filter by `transaction.status: "success"` and aggregate count
- For errors: Filter by `http.status_code >= 500`

**Step 4: AI Agent**
- Use `kibana.post_agent_builder_converse`
- Agent ID: `agent_business_slo`
- Input: Error rate, payment count, and ask for recommendation

**Step 5: Conditional Logic**
- Use `if` step type
- Condition: Check if payment drop percentage > 30%
- Use KQL syntax: `steps.ai_analysis.output.response.message: "*scale_up*"`

**Step 6: Scale Service**
- Use `http` step type
- URL: `http://host-1:3000/scale_service`
- Method: POST
- Body: `{"service_name": "payment-service"}`
- Add retry logic with `on-failure`

**Step 7: Audit Log**
- Use `elasticsearch.index` step type
- Index: `business_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}`
- Document: Include service name, action taken, AI recommendation, timestamp

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

  # Step 2: Query error rate
  - name: get_error_rate
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        bool:
          must:
            - term:
                service.name: "payment-service"
            - range:
                http.status_code:
                  gte: 500
          filter:
            - range:
                "@timestamp":
                  gte: "now-5m"
      size: 0
      aggs:
        error_count:
          value_count:
            field: "_id"

  # Step 3: Query payment transaction metrics
  - name: get_payment_metrics
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        bool:
          must:
            - term:
                service.name: "payment-service"
            - term:
                transaction.status: "success"
          filter:
            - range:
                "@timestamp":
                  gte: "now-5m"
      size: 0
      aggs:
        payment_count:
          value_count:
            field: "_id"
        total_amount:
          sum:
            field: "transaction.amount"

  # Step 4: Get baseline for comparison (previous hour)
  - name: get_baseline_metrics
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        bool:
          must:
            - term:
                service.name: "payment-service"
            - term:
                transaction.status: "success"
          filter:
            - range:
                "@timestamp":
                  gte: "now-1h"
                  lt: "now-5m"
      size: 0
      aggs:
        baseline_payment_count:
          value_count:
            field: "_id"

  # Step 5: Call AI agent for business impact analysis
  - name: ai_business_analysis
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_business_slo
      input: |
        Payment service degradation detected:
        - Current 5-minute error count: {{ steps.get_error_rate.output.response.aggregations.error_count.value }}
        - Current 5-minute successful payments: {{ steps.get_payment_metrics.output.response.aggregations.payment_count.value }}
        - Baseline (previous hour) successful payments: {{ steps.get_baseline_metrics.output.response.aggregations.baseline_payment_count.value }}
        
        Calculate the payment drop percentage and recommend an action.
        Respond ONLY with JSON:
        {"recommendation": "scale_up" | "investigate" | "no_action", "payment_drop_pct": <number>}
    on-failure:
      retry:
        max-attempts: 2
        delay: 1s

  # Step 6: Parse AI response
  - name: parse_ai_response
    type: console
    with:
      message: |-
        {% assign parsed = steps.ai_business_analysis.output.response.message | json_parse %}
        Recommendation: {{ parsed.recommendation }}
        Payment Drop: {{ parsed.payment_drop_pct }}%

  # Step 7: Conditional logic - check if scaling needed
  - name: check_scaling_needed
    type: if
    condition: "${{ steps.parse_ai_response.output contains 'scale_up' }}"
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
        error_count: "{{ steps.get_error_rate.output.response.aggregations.error_count.value }}"
        current_payment_count: "{{ steps.get_payment_metrics.output.response.aggregations.payment_count.value }}"
        baseline_payment_count: "{{ steps.get_baseline_metrics.output.response.aggregations.baseline_payment_count.value }}"
        ai_recommendation: "{{ steps.parse_ai_response.output }}"
        action_taken: "{{ steps.scale_service.output.data.action | default: 'no_action' }}"
        scaling_result: "{{ steps.scale_service.output.data.new_instances | default: 'N/A' }}"
```

</details>

## What You've Built

Congratulations! You've created a complete **business-critical automation system** that:

- ✅ Detects technical AND business metrics
- ✅ Uses AI to make intelligent decisions
- ✅ Takes automated remediation actions
- ✅ Maintains a complete audit trail

This is real-world automation that bridges the gap between observability and business outcomes.

**Click "Next" to see a summary of everything you've learned!**

