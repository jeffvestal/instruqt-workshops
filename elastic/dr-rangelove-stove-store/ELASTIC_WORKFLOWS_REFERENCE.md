# Elastic Workflows and Agent Builder Reference

This document provides comprehensive information about Elastic Workflows and Agent Builder for use in code generation and development.

## Table of Contents

1. [Workflow Structure](#workflow-structure)
2. [Step Types](#step-types)
3. [Liquid Templating](#liquid-templating)
4. [Error Handling](#error-handling)
5. [Agent Builder Integration](#agent-builder-integration)
6. [Common Patterns](#common-patterns)

---

## Workflow Structure

### Basic YAML Structure

Every workflow is defined in YAML format with the following top-level structure:

```yaml
version: "1"
name: workflow_name
description: "Optional description of what the workflow does"
enabled: true

inputs:
  # Input definitions here

consts:
  # Constants here (optional)

triggers:
  # Trigger definitions here

steps:
  # Step definitions here
```

### Required Fields

- **version**: Always `"1"` for current version
- **name**: Unique identifier for the workflow (lowercase, underscores allowed)
- **enabled**: Boolean (`true` or `false`) to enable/disable the workflow

### Input Definitions

Inputs define what data the workflow expects when triggered:

```yaml
inputs:
  - name: service_name
    type: string
    required: true
    description: "The name of the service to triage"
  
  - name: threshold
    type: number
    required: false
    description: "Optional threshold value"
```

**Input Types:**
- `string` - Text values
- `number` - Numeric values
- `boolean` - True/false values
- `array` - Lists of values
- `object` - Complex nested structures

### Constants

Constants are reusable values defined at the workflow level:

```yaml
consts:
  ip_api_base_url: http://ip-api.com/json
  max_retries: 3
  timeout_seconds: 30
```

Access constants in steps using `{{ consts.constant_name }}`.

### Triggers

Triggers define when a workflow executes:

**Manual Trigger:**
```yaml
triggers:
  - type: manual
```

**Alert Trigger:**
```yaml
triggers:
  - type: alert
```

When triggered by an alert, the workflow receives alert data in `event.alerts[0]`:
- `event.alerts[0].id` - Alert ID
- `event.alerts[0].rule.name` - Alert rule name
- `event.alerts[0].rule.parameters.esQuery` - Alert query (JSON string)
- `event.alerts[0]['@timestamp']` - Execution timestamp

---

## Step Types

### Console Step

Outputs messages to the console/logs:

```yaml
steps:
  - name: print_message
    type: console
    with:
      message: "Hello, {{ inputs.username }}!"
```

Multi-line messages:

```yaml
  - name: print_report
    type: console
    with:
      message: |
        Report for {{ inputs.service_name }}:
        - Status: {{ steps.check_status.output }}
        - Count: {{ steps.get_count.output }}
```

### Elasticsearch Search Step

Query Elasticsearch using Query DSL:

```yaml
  - name: get_error_logs
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        bool:
          must:
            - term:
                service.name: "{{ inputs.service_name }}"
            - range:
                http.status_code:
                  gte: 500
      size: 5
```

With aggregations:

```yaml
  - name: get_latency_stats
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        term:
          service.name: "{{ inputs.service_name }}"
      aggs:
        p95_latency:
          percentiles:
            field: "latency_ms"
            percents: [95]
      size: 0
```

**Accessing Results:**
- `steps.step_name.output.hits.total.value` - Total document count
- `steps.step_name.output.hits.hits[0]._source` - First document source
- `steps.step_name.output.response.aggregations.agg_name.values["95.0"]` - Aggregation values

### Elasticsearch ES|QL Query Step

Query using ES|QL (Elasticsearch Query Language):

```yaml
  - name: get_all_metrics
    type: elasticsearch.esql.query
    with:
      query: >
        FROM o11y-heartbeat
        | WHERE service.name == "payment-service"
        | WHERE @timestamp >= "{{ event.alerts[0]['@timestamp'] | date: '%s' | minus: 3660 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}"
          AND @timestamp <= "{{ event.alerts[0]['@timestamp'] }}"
        | EVAL 
            is_error = CASE(http.status_code >= 500, 1, 0),
            is_success = CASE(transaction.status == "success", 1, 0)
        | STATS 
            error_count = SUM(is_error),
            success_count = SUM(is_success)
```

**ES|QL Advantages:**
- More efficient for complex aggregations
- Can compute multiple metrics in a single query
- Better for time-based windowing

**Accessing Results:**
- `steps.step_name.output.values[0][0]` - First row, first column
- `steps.step_name.output.values[0][1]` - First row, second column
- Column order matches STATS clause order

### Elasticsearch Index Step

**⚠️ Note:** The `elasticsearch.index` step type has a bug. Use `elasticsearch.request` with `method: PUT` instead (see below).

### Elasticsearch Request Step

Generic action for advanced Elasticsearch API access. Use this for indexing documents (replacing `elasticsearch.index`), cluster health checks, and other Elasticsearch operations.

**Indexing Documents (PUT):**

```yaml
  - name: log_to_elasticsearch
    type: elasticsearch.request
    with:
      method: PUT
      path: "/workflow_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}/_doc/{{ execution.id }}"
      body:
        timestamp: "{{ execution.startedAt }}"
        workflow_name: "{{ execution.workflow.name }}"
        alert_id: "{{ event.alerts[0].id }}"
        action_taken: "{{ steps.remediate.output.status }}"
```

**Parameters:**
- `method`: HTTP method (GET, POST, PUT, DELETE) - defaults to GET if not specified
- `path`: API endpoint path (e.g., `/_search`, `/_cluster/health`, `/index-name/_doc/id`)
- `body`: JSON request body (required for PUT/POST)
- `query`: URL query string parameters (optional object)

**Dynamic Index Names:**
- Use date filters to create daily indices: `"/index-{{ execution.startedAt | date: '%Y-%m-%d' }}/_doc/{{ execution.id }}"`
- Use execution ID as document ID for deduplication
- Path format: `/index-name/_doc/document-id`

**Other Examples:**

**Cluster Health (GET):**
```yaml
  - name: get_cluster_health
    type: elasticsearch.request
    with:
      method: GET
      path: /_cluster/health
```

**Delete by Query (POST):**
```yaml
  - name: delete_old_documents
    type: elasticsearch.request
    with:
      method: POST
      path: /my-index/_delete_by_query
      body:
        query:
          range:
            "@timestamp":
              lt: "now-30d"
```

### HTTP Step

Make external API calls:

```yaml
  - name: call_remediation_api
    type: http
    with:
      url: "http://host-1:3000/remediate_service"
      method: POST
      headers:
        Content-Type: application/json
      body:
        service_name: "{{ inputs.service_name }}"
        action: "restart"
```

**GET Request:**

```yaml
  - name: get_geolocation
    type: http
    with:
      url: "{{ consts.ip_api_base_url }}/{{ inputs.ip_address }}"
      method: GET
```

**Accessing Response:**
- `steps.step_name.output.data` - Response body (parsed JSON)
- `steps.step_name.output.status` - HTTP status code
- `steps.step_name.output.headers` - Response headers

### AI Agent Step

Call an AI agent:

```yaml
  - name: ai_analysis
    type: ai.agent
    with:
      agent_id: agent_content_creator
      message: |
        Analyze this service incident:
        Service: {{ inputs.service_name }}
        Error count: {{ steps.get_errors.output.count }}
        Please provide remediation recommendations.
```

**Agent Message:**
- Can be a simple string or multi-line message
- Use Liquid templating to inject workflow data
- Agents receive the message and return structured or unstructured responses

**Accessing Agent Response:**
- `steps.step_name.output` - Agent's response (for passing to other steps)
- `steps.step_name.output.response.message` - Agent's text response (for display)
- For JSON responses, parse with `json_parse` filter: `{{ steps.step_name.output | json_parse }}`

### Conditional (If) Step

Conditional branching:

```yaml
  - name: check_threshold
    type: if
    condition: "${{ steps.get_metrics.output.count > 100 }}"
    steps:
      - name: take_action
        type: console
        with:
          message: "Threshold exceeded!"
    else:
      - name: log_normal
        type: console
        with:
          message: "Metrics are normal"
```

**Condition Syntax:**
- Use `${{ }}` for condition evaluation
- Can compare step outputs, inputs, or computed values
- Supports Liquid filters in conditions

**Complex Condition Example:**

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
          body:
            service_name: "payment-service"
```

---

## Liquid Templating

Workflows use Liquid templating syntax for dynamic values and logic.

### Variable Access

**Input Variables:**
```yaml
message: "Hello, {{ inputs.username }}!"
```

**Step Outputs:**
```yaml
message: "Count: {{ steps.get_count.output }}"
message: "First hit: {{ steps.search.output.hits.hits[0]._source.message }}"
message: "Agg value: {{ steps.agg.output.response.aggregations.p95.values['95.0'] }}"
```

**Event Data (Alert Triggers):**
```yaml
message: "Alert ID: {{ event.alerts[0].id }}"
message: "Rule name: {{ event.alerts[0].rule.name }}"
```

**Execution Context:**
```yaml
message: "Execution ID: {{ execution.id }}"
message: "Started at: {{ execution.startedAt }}"
message: "Workflow name: {{ execution.workflow.name }}"
```

### Filters

**Date Formatting:**
```yaml
{{ execution.startedAt | date: '%Y-%m-%d' }}
{{ execution.startedAt | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}
{{ event.alerts[0]['@timestamp'] | date: '%s' }}
```

**Date Math:**
```yaml
{{ event.alerts[0]['@timestamp'] | date: '%s' | minus: 3660 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}
```

**JSON Parsing:**
```yaml
{% assign parsed = steps.ai_response.output.response.message | json_parse %}
{{ parsed.remediation }}
{{ parsed.sentiment }}
```

**Math Operations:**
```yaml
{{ steps.get_count.output | divided_by: 60 }}
{{ steps.get_count.output | times: 0.7 }}
{{ steps.get_count.output | plus: 10 }}
{{ steps.get_count.output | minus: 5 }}
{{ steps.get_count.output | round }}
```

**Default Values:**
```yaml
{{ steps.maybe_missing.output | default: 'N/A' }}
{{ steps.scale_service.output.data.action | default: 'no_action' }}
```

**Array/Object Access:**
```yaml
{{ steps.get_metrics.output.values[0][0] }}
{{ steps.get_metrics.output.values[0][1] }}
{{ steps.parse_json.output.remediation }}
```

### Variable Assignment

Assign values to variables for reuse:

```yaml
message: >-
  {% assign status = steps.get_geolocation.output.data.status %}
  {% assign city = steps.get_geolocation.output.data.city %}
  {% assign country = steps.get_geolocation.output.data.country %}
  
  Location: {{ city }}, {{ country }}
  Status: {{ status }}
```

**Complex Assignments:**

```yaml
message: >-
  {% assign esQuery = event.alerts[0].rule.parameters.esQuery | json_parse %}
  Service: {{ esQuery.query.bool.filter[1].term['service.name'] }}
```

### Conditionals

**If/Else:**

```yaml
message: >-
  {% if steps.get_status.output == "success" %}
    ✅ Operation succeeded
  {% else %}
    ❌ Operation failed
  {% endif %}
```

**Elsif:**

```yaml
message: >-
  {% assign cc = steps.get_geolocation.output.data.countryCode %}
  {% if cc == "US" %}
    🇺🇸 United States
  {% elsif cc == "GB" %}
    🇬🇧 United Kingdom
  {% else %}
    🌍 Other country
  {% endif %}
```

**Contains Check:**

```yaml
message: >-
  {% assign europe = "AL,AD,AT,BA,BE,BG,BY,CH,HR,CY,CZ,DE,DK,EE,ES,FI,FO,FR" %}
  {% assign cc = steps.get_geolocation.output.data.countryCode %}
  {% if europe contains cc %}
    🇪🇺 Europe-based IP
  {% endif %}
```

**Complex Conditions:**

```yaml
message: >-
  {% assign orig = steps.first_check.output.response.message | json_parse %}
  {% assign fin = steps.final_check.output.response.message | json_parse %}
  {% if fin.sentiment == "POSITIVE" %}
    ✅ PASSED: Content sentiment is positive
  {% else %}
    ❌ FAILED: Content still has negative sentiment
  {% endif %}
```

---

## Error Handling

### Retry Logic

Add retry logic to any step:

```yaml
  - name: call_api
    type: http
    with:
      url: "http://example.com/api"
      method: POST
    on-failure:
      retry:
        max-attempts: 2
        delay: 1s
```

**Retry Configuration:**
- `max-attempts`: Number of retry attempts (default: 1)
- `delay`: Time to wait between retries (e.g., `1s`, `5s`, `1m`)

**Common Use Cases:**
- HTTP calls to external APIs
- Agent Builder calls (LLM APIs can be flaky)
- Elasticsearch operations during high load

---

## Agent Builder Integration

### Agent IDs

Agents are identified by their `agent_id`:

```yaml
  - name: call_agent
    type: ai.agent
    with:
      agent_id: agent_content_creator
      message: "Generate content about {{ inputs.topic }}"
```

**Common Agent Patterns:**
- `agent_content_creator` - Content generation
- `agent_sentiment_analyzer` - Sentiment analysis (returns JSON)
- `agent_pr_spin_specialist` - PR/content optimization
- `agent_business_slo` - Business impact analysis

### Message/Output Patterns

**Simple Message:**
```yaml
message: "Write a press release about {{ inputs.topic }}"
```

**Multi-line Message with Context:**
```yaml
message: |
  Here are the current metrics for payment-service:
  - Error count (last 1m): {{ steps.get_all_metrics.output.values[0][0] }}
  - Current successful payments (last 1m): {{ steps.get_all_metrics.output.values[0][1] }}
  - Baseline successful payments: {{ steps.get_all_metrics.output.values[0][3] }}
  
  Calculate the percentage drop and explain the business impact.
```

**Structured Output Parsing:**
```yaml
  - name: parse_ai_response
    type: console
    with:
      message: |-
        {% assign parsed = steps.ai_analysis.output | json_parse %}
        Remediation: {{ parsed.remediation }}
```

### Chaining Agents (Generator-Critic-Remediator Pattern)

A common pattern is to chain multiple agents:

**Step 1: Generator**
```yaml
  - name: draft_content
    type: ai.agent
    with:
      agent_id: agent_content_creator
      message: "Write a short press release about: {{ inputs.topic }}"
```

**Step 2: Critic**
```yaml
  - name: first_check
    type: ai.agent
    with:
      agent_id: agent_sentiment_analyzer
      message: "{{ steps.draft_content.output }}"
```

**Step 3: Remediator**
```yaml
  - name: remediation_spin
    type: ai.agent
    with:
      agent_id: agent_pr_spin_specialist
      message: |
        The following draft was written:
        "{{ steps.draft_content.output }}"
        
        It was analyzed with this sentiment:
        "{{ steps.first_check.output }}"
        
        Please revise this draft to have a strongly positive spin.
```

**Step 4: Final Validation**
```yaml
  - name: final_check
    type: ai.agent
    with:
      agent_id: agent_sentiment_analyzer
      message: "{{ steps.remediation_spin.output }}"
```

---

## Common Patterns

### Pattern 1: Alert-Triggered Remediation

```yaml
version: "1"
name: auto_remediate
enabled: true

inputs: []

triggers:
  - type: alert

steps:
  - name: parse_alert
    type: console
    with:
      message: |
        Alert '{{ event.alerts[0].rule.name }}' fired!
        Alert ID: {{ event.alerts[0].id }}

  - name: ai_decision
    type: ai.agent
    with:
      agent_id: agent_remediation_advisor
      message: |
        Alert: {{ event.alerts[0].rule.name }}
        Please recommend remediation action as JSON: {"action": "..."}
    on-failure:
      retry:
        max-attempts: 2
        delay: 1s

  - name: execute_remediation
    type: if
    condition: "${{ steps.ai_decision.output | json_parse | json: 'action' }} == 'restart'"
    steps:
      - name: call_api
        type: http
        with:
          url: "http://host-1:3000/remediate"
          method: POST
          body:
            action: "restart"
            service: "payment-service"

  - name: audit_log
    type: elasticsearch.request
    with:
      method: PUT
      path: "/remediation_logs-{{ execution.startedAt | date: '%Y-%m-%d' }}/_doc/{{ execution.id }}"
      body:
        timestamp: "{{ execution.startedAt }}"
        alert_id: "{{ event.alerts[0].id }}"
        action: "{{ steps.call_api.output.data.action }}"
```

### Pattern 2: Time-Windowed Metrics Comparison

```yaml
  - name: get_metrics_comparison
    type: elasticsearch.esql.query
    with:
      query: >
        FROM o11y-heartbeat
        | WHERE service.name == "payment-service"
        | WHERE @timestamp >= "{{ event.alerts[0]['@timestamp'] | date: '%s' | minus: 3660 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}"
          AND @timestamp <= "{{ event.alerts[0]['@timestamp'] }}"
        | EVAL 
            is_in_current_window = @timestamp >= "{{ event.alerts[0]['@timestamp'] | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
            is_in_baseline_window = @timestamp < "{{ event.alerts[0]['@timestamp'] | date: '%s' | minus: 60 | date: '%Y-%m-%dT%H:%M:%S.%LZ' }}",
            is_error = CASE(http.status_code >= 500 AND is_in_current_window == true, 1, 0),
            is_current_success = CASE(transaction.status == "success" AND is_in_current_window == true, 1, 0),
            is_baseline_success = CASE(transaction.status == "success" AND is_in_baseline_window == true, 1, 0)
        | STATS 
            error_count = SUM(is_error),
            current_payment_count = SUM(is_current_success),
            baseline_payment_count = SUM(is_baseline_success)
```

### Pattern 3: Conditional Scaling Based on Metrics

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
            Previous instances: {{ steps.scale_service.output.data.previous_instances }}
            New instances: {{ steps.scale_service.output.data.new_instances }}
    else:
      - name: log_no_scaling
        type: console
        with:
          message: |
            ⚠️ No scaling action needed.
            Current: {{ steps.get_all_metrics.output.values[0][1] }}
            Threshold: {% assign baseline = steps.get_all_metrics.output.values[0][3] | plus: 0 %}{{ baseline | divided_by: 60 | times: 0.7 | round }}
```

### Pattern 4: Multi-Step Data Pipeline

```yaml
steps:
  # Step 1: Gather data
  - name: get_error_logs
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        bool:
          must:
            - term:
                service.name: "{{ inputs.service_name }}"
            - range:
                http.status_code:
                  gte: 500
      size: 5

  # Step 2: Get metrics
  - name: get_latency
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      query:
        term:
          service.name: "{{ inputs.service_name }}"
      aggs:
        p95_latency:
          percentiles:
            field: "latency_ms"
            percents: [95]
      size: 0

  # Step 3: Format report
  - name: format_report
    type: console
    with:
      message: |
        Triage Report for {{ inputs.service_name }}:
        - P95 Latency: {{ steps.get_latency.output.response.aggregations.p95_latency.values["95.0"] }} ms
        - Error count: {{ steps.get_error_logs.output.hits.total.value }}
        - Sample error: {{ steps.get_error_logs.output.hits.hits[0]._source.log.message }}

  # Step 4: AI analysis
  - name: ai_analysis
    type: ai.agent
    with:
      agent_id: agent_triage_specialist
      message: |
        {{ steps.format_report.output }}
        
        Please analyze this incident and provide recommendations.
```

---

## Best Practices

1. **Use ES|QL for Complex Aggregations**: When you need multiple metrics or time-windowed comparisons, ES|QL is more efficient than multiple search queries.

2. **Always Include Retry Logic**: External APIs (HTTP, Agent Builder) should have retry logic for resilience.

3. **Audit Important Actions**: Use `elasticsearch.request` with `method: PUT` to log all remediation actions for compliance and debugging.

4. **Parse JSON Responses**: When agents return structured data, use `json_parse` filter to access nested properties.

5. **Use Constants for Reusable Values**: Define URLs, thresholds, and other constants at the workflow level.

6. **Leverage Execution Context**: Use `execution.id` and `execution.startedAt` for audit logging and deduplication.

7. **Test Conditions Carefully**: Complex conditions with computed values should be tested thoroughly - use variable assignment for clarity.

8. **Chain Agents Thoughtfully**: The Generator-Critic-Remediator pattern works well, but ensure each agent has clear instructions and context.

