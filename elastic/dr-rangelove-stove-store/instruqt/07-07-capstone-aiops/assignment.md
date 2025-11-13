---
slug: 07-capstone-aiops
id: zykrcepib4on
type: challenge
title: 'Capstone: Build a ''Self-Healing'' Workflow'
teaser: Create an alert-triggered workflow that uses AI and calls external APIs
tabs:
- id: yn8vsudeseix
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: kzygfchylyuh
  title: Alerts
  type: service
  hostname: kubernetes-vm
  path: /app/observability/alerts
  port: 30001
- id: vbu8x6nbakbu
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: advanced
timelimit: 1800
enhanced_loading: null
---

# 📖 Challenge 7: Capstone - Build a "Self-Healing" AIOps Workflow

We will combine what we've learned to build a "self-healing" workflow.

**The Scenario:**

Our data sprayer is injecting live data with periodic anomalies. Our alert (`latency-threshold-alert-critical`) fires when latency spikes are detected.

We will build a workflow that **automatically triggers** from that alert, uses AI to get a remediation plan, and calls our Mock API to "remediate" the faulty service.

## 1. Create the Workflow

1. Create a new workflow named `self_healing_aiops`.
2. Paste this starting block. **Look at the `triggers` block!**

   * `type: alert`: This is the new trigger type.
   * This workflow will now run *automatically* every time any alert fires (we'll filter by alert name in the steps).

```yaml
version: "1"
name: self_healing_aiops
description: "Self-healing workflow triggered by alerts"
enabled: true

inputs: [] # <-- No inputs needed, the alert *is* the input

triggers:
  - type: alert
```

## 2. Add the Steps

Now, paste this entire `steps` block below your `triggers`. Read each step's comments to see how it combines all our concepts.

```yaml
steps:
  # Step 1: Parse service name from the alert query
  - name: get_service_name
    type: console
    with:
      message: |
        {% assign esQuery = event.alerts[0].rule.parameters.esQuery | json_parse %}
        Alert '{{ event.alerts[0].rule.name }}' fired!
        Service: {{ esQuery.query.bool.filter[1].term['service.name'] }}
        Alert ID: {{ event.alerts[0].id }}

  # Step 2: Call AI agent for remediation decision
  - name: ai_analysis
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_content_creator
      input: |
        {% assign esQuery = event.alerts[0].rule.parameters.esQuery | json_parse %}
        A critical latency anomaly was detected for service: {{ esQuery.query.bool.filter[1].term['service.name'] }}
        Respond ONLY with the following JSON:
        {"remediation": "restart_service"}

  # Step 3: Parse and check AI response
  - name: parse_ai_response
    type: console
    with:
      message: |-
        {% assign parsed = steps.ai_analysis.output.response.message | json_parse %}{{ parsed.remediation }}

  - name: check_remediation
    type: if
    condition: "${{ steps.parse_ai_response.output == 'restart_service' }}"
    steps:
      - name: call_remediation_api
        type: http
        with:
          url: "http://host-1:3000/remediate_service"
          method: POST
          headers:
            Content-Type: application/json
          body:
            service_name: "payment-service"
        on-failure:
          retry:
            max-attempts: 2
      
      - name: log_action
        type: console
        with:
          message: "✅ Successfully triggered remediation!"
    else:
      - name: log_no_action
        type: console
        with:
          message: "⚠️ No action taken."

  # Step 4: Index the results back into Elastic for auditing
  - name: log_to_elasticsearch
    type: elasticsearch.index
    with:
      index: "workflow_actions-{{ now() | date('YYYY-MM-DD') }}"
      document:
        timestamp: "{{ now() }}"
        workflow_name: "self_healing_aiops"
        alert_id: "{{ event.alerts[0].id }}"
        alert_name: "{{ event.alerts[0].rule.name }}"
        action_taken: "{{ steps.call_remediation_api.output.data.status }}"
```

## 3. Save and Watch

1. **Save** your workflow.
2. Now... we wait. The data sprayer running in the background injects an anomaly every 60-90 seconds.
3. In a **new Kibana tab**, go to **Observability > Alerts**.
4. Set your time-picker to **"Last 15 minutes"**.
5. Within a few minutes, you should see the `latency-threshold-alert-critical` fire for a service (e.g., `payment-service`).

## 4. Watch the Magic

1. Go back to your **Workflows** tab.
2. Click on your `self_healing_aiops` workflow.
3. You will see a **new run** has *automatically started* (it may take a few seconds after the alert fires).
4. Click the run to inspect it.
5. Watch it execute step-by-step:
   * `get_service_name` (parses service name from alert query)
   * `ai_analysis` (gets `{"remediation": "restart_service"}`)
   * `parse_ai_response` (extracts remediation action)
   * `check_remediation` (condition is `true`)
   * `call_remediation_api` (sends a POST to our mock server)
   * `log_action` (logs success message)
   * `log_to_elasticsearch` (writes the audit log)

## 5. Verify Remediation

In the **Terminal** tab, check the mock API logs:

```bash
pm2 logs mock-api --lines 20
```

You should see a log entry showing the remediation was triggered!

## 6. Check the Audit Log

Go to Kibana **Dev Tools > Console** and run:

```
GET workflow_actions-*/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```

You'll see your workflow's audit trail indexed in Elasticsearch!

## 6. Enhance the Logging (Optional)

The mock remediation API returns rich metadata. Update your `log_action` step to display it:

```yaml
- name: log_action
  type: console
  with:
    message: |
      {{ steps.call_remediation_api.output.data.message }}
      📋 Remediation ID: {{ steps.call_remediation_api.output.data.remediation_id }}
      🔧 Service: {{ steps.call_remediation_api.output.data.service }}
      ⚡ Action: {{ steps.call_remediation_api.output.data.action }}
      ⏱️  Estimated Duration: {{ steps.call_remediation_api.output.data.details.estimated_duration }}
```

Save and trigger another alert to see the enhanced output!

---

## Workshop Complete!

You have successfully built an end-to-end, "self-healing" automation that triggers from a real alert, uses AI to reason, takes external action, and logs its own results back into Elastic.

### What You've Learned

1. **Building Workflows**: Inputs, steps, chaining, error handling, conditionals.
2. **AI Orchestration**: Multi-agent pipelines for generate-critique-remediate patterns.
3. **Bidirectional Integration**: Workflows call agents, agents use workflows as tools.
4. **AIOps**: Alert-triggered automation with AI-driven decision-making.

### Next Steps

* Explore ML-based anomaly detection (set `USE_ML_AD=true` and update `alert_ids` to `ml-anomaly-alert-critical`).
* Add more sophisticated AI agents for multi-step reasoning.
* Integrate with real remediation APIs (Kubernetes, cloud providers, ticketing systems).
* Build approval workflows with Slack/Teams integrations.

**Congratulations!** 🎉
