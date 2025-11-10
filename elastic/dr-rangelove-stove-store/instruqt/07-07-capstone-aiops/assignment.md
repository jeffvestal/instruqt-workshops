---
slug: 07-capstone-aiops
id: zykrcepib4on
type: challenge
title: 'Capstone: Build a ''Self-Healing'' Workflow'
teaser: Create an alert-triggered workflow that uses AI and calls external APIs
tabs:
- id: otj5bdykvl85
  title: Kibana
  type: service
  hostname: kubernetes-vm
  path: /app/management/kibana/workflows
  port: 30001
- id: wm6a1m2sw8u1
  title: Alerts
  type: service
  hostname: kubernetes-vm
  path: /app/observability/alerts
  port: 30001
- id: wkwheg8hlckj
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: advanced
timelimit: 1800
enhanced_loading: null
---

# 📖 Challenge 7: Capstone - Build a "Self-Healing" AIOps Workflow

This is the "boss level." We will combine *everything* we've learned to build a "self-healing" workflow.

**The Scenario:**

Our data sprayer is injecting live data with periodic anomalies. Our alert (`latency-threshold-alert-critical`) fires when latency spikes are detected.

We will build a workflow that **automatically triggers** from that alert, uses AI to get a remediation plan, and calls our Mock API to "remediate" the faulty service.

## 1. Create the Workflow

1. Create a new workflow named `self_healing_aiops`.
2. Paste this starting block. **Look at the `triggers` block!**

   * `type: alert`: This is the new trigger type.
   * `alert_ids:`: This links it to the `latency-threshold-alert-critical` alert our setup script created.
   * This workflow will now run *automatically* every time that alert fires.

```yaml
version: "1"
name: self_healing_aiops
description: "Self-healing workflow triggered by alerts"
enabled: true

inputs: [] # <-- No inputs needed, the alert *is* the input

triggers:
  - type: alert
    enabled: true
    params:
      alert_ids: ["latency-threshold-alert-critical"] # <-- Our threshold alert
```

## 2. Add the Steps

Now, paste this entire `steps` block below your `triggers`. Read each step's comments to see how it combines all our concepts.

```yaml
steps:
  # Step 1: Extract the service name from the alert payload
  - name: get_service_name
    type: console
    with:
      # For threshold alerts, service name is in the matched documents
      message: "Alert detected for service: {{ trigger.data.context.hits[0]._source.service.name }}"

  # Step 2: Call an AI agent to decide what to do
  - name: ai_analysis
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_content_creator # <-- We'll reuse this agent
      input: |
        A critical latency anomaly was detected for service: {{ trigger.data.context.hits[0]._source.service.name }}
        Respond ONLY with the following JSON:
        {"remediation": "restart_service"}

  # Step 3: Use an "if" condition to check the AI's response
  - name: check_remediation
    type: if
    with:
      condition: "{{ steps.ai_analysis.output.response.message.remediation == 'restart_service' }}"
      # "then" runs this list of steps if the condition is true
      then:
        - name: call_remediation_api
          type: http
          with:
            url: "http://host-1:3000/remediate_service" # <-- Our mock API!
            method: POST
            headers:
              Content-Type: application/json
            body:
              service_name: "{{ trigger.data.context.hits[0]._source.service.name }}"
          on-failure:
            retry:
              max-attempts: 2
        
        - name: log_action
          type: console
          with:
            message: "✅ Successfully triggered remediation for {{ trigger.data.context.hits[0]._source.service.name }}"

  # Step 4: Index the results back into Elastic for auditing
  - name: log_to_elasticsearch
    type: elasticsearch.index
    with:
      index: "workflow_actions-{{ now() | date('YYYY-MM-DD') }}"
      document:
        timestamp: "{{ now() }}"
        workflow_name: "self_healing_aiops"
        service: "{{ trigger.data.context.hits[0]._source.service.name }}"
        alert_id: "{{ trigger.data.alert.id }}"
        action_taken: "{{ steps.call_remediation_api.response.status }}"
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
   * `get_service_name` (gets `payment-service`)
   * `ai_analysis` (gets `{"remediation": "restart_service"}`)
   * `check_remediation` (condition is `true`)
   * `call_remediation_api` (sends a POST to our mock server)
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
