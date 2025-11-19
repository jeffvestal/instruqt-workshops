# Elastic Workflows & AI Agent Workshop

**"From Findings to Outcomes: Automating with Elastic Workflows & Agents"**

[![Instruqt](https://img.shields.io/badge/Launch-Instruqt%20Workshop-00BFB3?style=for-the-badge)](https://play.instruqt.com/elastic/tracks/workflows-agents-alerts)

## Overview

This hands-on Instruqt workshop teaches users how to build, test, and orchestrate automated workflows and AI agents in Elastic. Participants progress from simple automation to building complete production-ready systems including a self-healing AIOps workflow and a business impact detector that combines ES|QL queries, AI agents, and deterministic logic.

**Workshop Details:**
- **Track Slug:** `workflows-agents-alerts`
- **Track ID:** `tvu7yvg32vsk`
- **Duration:** 4 hours
- **Difficulty:** Basic to Advanced progression
- **Theme:** Modern Dark (enabled automatically)

## Workshop Philosophy: From Findings to Outcomes

Elastic has long been a world-class "findings" engine—exceptional at detecting problems through search, observability, and security. But what happens after detection? The traditional approach requires pivoting to external tools (SOAR platforms, custom scripts, runbooks) to take action. This is the **"Two-Vendor Problem"**.

**Elastic Workflows** closes this gap by providing native automation capabilities within the platform, enabling you to transform findings into outcomes without leaving Elastic.

## What You'll Build

By the end of this workshop, you will have created two complete automation systems:

1. **Self-Healing Observability System** - Alert-triggered workflow that detects service anomalies, uses AI to analyze root cause, and automatically calls remediation APIs
2. **Business Impact Detector** - Revenue-aware automation that monitors payment metrics with ES|QL, calculates business impact, uses AI for explanations, and auto-scales services to prevent revenue loss

## Workshop Structure

### 9 Hands-On Challenges

#### 1. The "Why": From Findings to Outcomes (5 min)
Introduction to the Two-Vendor Problem and how Workflows solve it. Understand the core philosophy of turning insights into automated actions.

#### 2. Building Your First Workflow (15 min)
Create a simple workflow with inputs and console output. Learn YAML workflow structure, input parameters, and basic step execution.

**Key Concepts:** Workflow anatomy, inputs, console steps, manual execution

#### 3. Chaining Steps (20 min)
Build workflows that chain HTTP calls with data transformation. Make API requests, extract data, and pass it between steps using Liquid templating.

**Key Concepts:** HTTP steps, output references, Liquid syntax, data transformation

**Solution:** IP geolocation workflow with chained API calls

#### 4. Making it Robust (25 min)
Add retry logic and conditional branching to handle failures gracefully. Learn error handling patterns and implement if/else logic.

**Key Concepts:** `on-failure` retry, fallback steps, conditional `if` steps, error handling patterns

**Solution:** Robust IP geolocation with comprehensive error handling

#### 5. The AI "Assembly Line" (30 min)
Orchestrate multiple AI agents in a generator-critic-remediator pattern. Chain AI agents to create sophisticated multi-step reasoning.

**Key Concepts:** Multi-agent orchestration, `kibana.post_agent_builder_converse` step, chaining AI outputs

**Solution:** Press release workflow (generator → sentiment analyzer → spin specialist)

#### 6. The "Full Circle": AI Agent Tools (30 min)
Give an AI agent a workflow as a tool. Enable AI agents to execute workflows for complex queries, creating a conversational interface to automation.

**Key Concepts:** Agent tools, workflow-as-tool pattern, ES queries in workflows, AI-driven orchestration

**Solution:** SRE Triage Bot with observability query workflow

#### 7. Self-Healing AI (45 min)
Build an end-to-end alert-triggered automation system. Create a workflow that responds to ML anomaly alerts, analyzes the issue with AI, and calls external remediation APIs.

**Key Concepts:** Alert triggers, `elasticsearch.search` steps, alert data access, external API integration

**Solution:** Complete self-healing workflow triggered by payment-service anomalies

#### 8. Capstone: Business Impact Detection (60 min)
Build a production-ready business-critical automation system from scratch. Combine ES|QL for fast multi-metric queries, deterministic logic for reliable decisions, and AI for human-readable explanations.

**Key Concepts:** 
- `elasticsearch.esql.query` for efficient data retrieval
- Multi-value ES|QL queries with EVAL and STATS
- Deterministic scaling decisions based on numeric thresholds
- AI agents for business impact explanation
- Complete audit logging with `elasticsearch.index`

**Solution:** Payment service business impact detector with auto-scaling

**What Makes This Special:**
- Single ES|QL query retrieves error count, current payments, baseline payments, and transaction amounts
- Deterministic logic calculates payment drop percentage and decides on scaling (no AI guessing)
- AI agent explains business impact in human language for stakeholders
- Complete observability with audit logs indexed to Elasticsearch

#### 9. Workshop Summary (10 min)
Recap of patterns learned, production considerations, and next steps for extending to real environments.

## Architecture

### Infrastructure

The workshop runs on two VMs in Instruqt:

#### kubernetes-vm (16 CPU, 16GB RAM)
- **Elasticsearch** - Port 30920 (backend)
- **Kibana** - Port 30001 (user-facing)
- **k3s** - Lightweight Kubernetes running ECK operators
- **Elastic Stack Components:**
  - Elasticsearch with full API access
  - Kibana with Workflows UI enabled
  - Agent Builder with 4 pre-configured AI agents

#### host-1 (4 CPU, 8GB RAM)
- **Mock Remediation API** - Port 3000 (Express.js)
- **Data Generator** - Python async data sprayer
- **PM2 Process Manager** - Keeps services running
- **Workshop Scripts** - Validation and helper scripts

### Workshop Assets

All workshop assets are stored in GitHub and cloned during sandbox setup:

```
workshop-assets/
├── data_generator/
│   ├── data_sprayer.py          # Python async data generator
│   ├── scenarios.json            # Anomaly and business incident scenarios
│   └── setup.py                  # Package dependencies
└── setup_scripts/
    ├── 01-create-agents.sh       # Create 4 AI agents
    ├── 02-create-alert.sh        # Create technical & business alerts
    ├── 03-mock-api-service.sh    # Start Express remediation API
    ├── 04-force-incident.sh      # Inject technical anomaly
    ├── 05-restore-snapshot.sh    # Optional snapshot restore
    ├── 06-trigger-business-incident.sh  # Inject business incident
    └── solve-08-business-impact-detection  # Challenge 8 validator
```

## Data Generator

The workshop includes a production-grade Python data generator with two modes:

### Backfill Mode (`--backfill`)
- Generates 7 days of historical observability data
- Parallel generation using multiprocessing (3-5x speedup)
- Bulk ingestion with batching and retry logic
- Progress tracking with ETA calculations
- Resume capability if interrupted

### Live Mode (`--live`)
- Continuous real-time data generation
- Periodic anomaly injection (every 60-90 seconds)
- Business incident simulation (flag-based activation)
- Multi-service synthetic observability data

### Services & Data

**Four microservices:**
- `market-data-feed` - P99 latency ~85ms
- `trade-service` - P99 latency ~150ms
- `payment-service` - P99 latency ~300ms (has transaction fields)
- `order-processor` - P99 latency ~70ms

**Normal Data:**
- Status codes: 200 (85%), 201 (10%), 204 (5%)
- Latency: Gaussian distribution around healthy baselines
- Transaction status (payment-service): success (95%), failed (4%), cancelled (1%)
- Transaction amounts: $10-$500 depending on type

**Anomaly Scenarios (from scenarios.json):**
1. Market Data Latency Spike - L2 cache exhaustion (3500ms, 15s duration)
2. Payment Gateway Timeout - Upstream latency (5000ms, 503 errors, 15s duration)
3. Trade Service DB Pool Exhaustion - Connection pool saturated (2800ms, 500 errors, 15s duration)
4. Order Processor Memory Pressure - GC pauses (1200ms, 15s duration)
5. **Business Impact: Payment Processing Failure** - Revenue-affecting incident (300s duration)
   - 60% drop in successful transactions
   - 50% reduction in transaction amounts
   - Used for Challenge 8 testing

### Robustness Features

**Three-stage bailout mechanism** prevents sandbox hangs on slow Elasticsearch:
1. **Stage 1 (3 min):** Warning if no batches completed
2. **Stage 2 (5 min):** Fatal error and exit if no batches completed
3. **Stage 3 (First batch):** Check ingestion rate - abort if < 500 docs/sec

**GitHub clone retry logic** in setup scripts handles transient 500 errors:
- 3 retry attempts with 5-second delays
- Cleanup of partial clones between attempts
- Clear error messaging directing users to restart sandbox

## Setup Flow

### 1. Track Script: setup-kubernetes-vm

Runs first on kubernetes-vm to prepare the Elastic environment:

```bash
1. Wait for k3s and Elasticsearch to be ready
   - Two-stage retry: initial 5-min wait, then restart k3s if needed
   - Wait up to 3 more minutes after restart

2. Configure Kibana publicBaseUrl for ingress

3. Wait for Kibana to be ready (up to 60 retries)

4. Enable workflows feature flag + dark mode theme
   - POST /api/kibana/settings with "workflows:ui:enabled": true and "theme:darkMode": true

5. Download workshop assets from GitHub
   - Clone with sparse checkout (only workshop-assets directory)
   - Retry logic: 3 attempts with 5s delays for transient errors
   - Copy to /opt/workshop-assets/

6. Install Python dependencies for data generator
   - Create venv, install elasticsearch, aiohttp

7. Run data generator in backfill mode
   - Generate 7 days of historical data (~2.5M documents)
   - Parallel generation, async bulk ingestion

8. Start data generator in live mode (background)
   - Continuous data stream with periodic anomalies
   - Listens for /tmp/business_incident_active flag

9. Create 4 AI agents via Agent Builder API
   - agent_content_creator: Press release generator (negative tone)
   - agent_sentiment_analyzer: JSON sentiment analysis
   - agent_pr_spin_specialist: Positive spin remediator
   - agent_business_slo: Business impact explainer

10. Create alert rules
    - payment-service-latency-spike: Technical alert (5xx errors, 5m window)
    - business-impact-payment-degradation: Business alert (5xx errors, 5m window)

11. Export environment variables for other scripts
```

### 2. Track Script: setup-host-1

Runs second on host-1 to prepare mock services:

```bash
1. Pull environment variables from kubernetes-vm (port 9000 HTTP server)

2. Clone workshop assets from GitHub (same sparse checkout as kubernetes-vm)

3. Install Node.js 20.x LTS

4. Install PM2 process manager globally

5. Create and start mock remediation API
   - Express.js server on port 3000
   - Endpoints: /remediate_service, /scale_service, /health
   - Logs all requests for verification

6. Verify API is responding
```

## AI Agents

Four pre-configured AI agents are created during setup:

### 1. agent_content_creator
- **Role:** Press Release Generator
- **Purpose:** Generate initial content (intentionally negative)
- **Instructions:** Write 1-2 sentence press releases with a negative tone, no spin
- **Avatar:** PC (teal)
- **Used in:** Challenge 5 (AI Assembly Line)

### 2. agent_sentiment_analyzer
- **Role:** Sentiment Critic
- **Purpose:** Analyze content and return structured JSON sentiment
- **Instructions:** Return only JSON with sentiment, score, evidence, and explanations
- **Avatar:** SA (pink)
- **Used in:** Challenge 5 (AI Assembly Line)

### 3. agent_pr_spin_specialist
- **Role:** Content Remediator
- **Purpose:** Rewrite content with positive corporate spin
- **Instructions:** Transform negative content into optimistic press releases
- **Avatar:** PS (yellow)
- **Used in:** Challenge 5 (AI Assembly Line)

### 4. agent_business_slo
- **Role:** Business Impact Explainer
- **Purpose:** Translate technical metrics into business impact for stakeholders
- **Instructions:** Explain revenue impact, suggest investigations, 2-3 sentences
- **Avatar:** BS (blue)
- **Used in:** Challenge 8 (Business Impact Capstone)

### 5. sre_triage_bot
- **Role:** Observability Triage Assistant
- **Purpose:** Accept workflow tools for querying observability data
- **Instructions:** Help SREs investigate incidents by calling provided workflow tools
- **Avatar:** ST (orange)
- **Used in:** Challenge 6 (AI Agent Tools)

## Workflow Concepts

### Step Types

| Step Type | Purpose | Example Use Case |
|-----------|---------|------------------|
| `console` | Print messages or data | Debugging, notifications |
| `http` | Make HTTP API calls | Call external APIs, webhooks |
| `elasticsearch.search` | Query with Query DSL | Complex aggregations, legacy queries |
| `elasticsearch.esql.query` | Query with ES\|QL | Fast multi-metric queries |
| `elasticsearch.index` | Index documents | Audit logs, results storage |
| `kibana.post_agent_builder_converse` | Call AI agents | AI reasoning, explanations |
| `if` | Conditional branching | Decision logic, error handling |

### Data Access Patterns

**Liquid Templating:**
```yaml
# Access workflow inputs
{{ inputs.service_name }}

# Access constants
{{ consts.api_key }}

# Access step outputs
{{ steps.query_data.output.hits.total.value }}

# Access ES|QL results (array of arrays)
{{ steps.esql_query.output.values[0][0] }}  # First row, first column

# Access alert trigger data
{{ event.alerts[0].rule.name }}
{{ event.alerts[0].id }}

# Built-in functions
{{ now() }}
{{ steps.value.output.count | plus: 10 }}
{{ steps.baseline.output.total | divided_by: 12.0 }}
```

### Error Handling Patterns

**Retry with exponential backoff:**
```yaml
on-failure:
  retry:
    max-attempts: 3
    delay: 2s
```

**Fallback steps:**
```yaml
on-failure:
  fallback:
    - name: log_error
      type: console
      with:
        message: "Error: {{ steps.api_call.error }}"
```

**Conditional error handling:**
```yaml
- name: check_result
  type: if
  condition: "{{ steps.api_call.output.status == 200 }}"
  steps:
    - name: success_path
      type: console
      with:
        message: "Success!"
  else:
    - name: error_path
      type: console
      with:
        message: "Failed with status {{ steps.api_call.output.status }}"
```

## Key Technical Patterns

### ES|QL Multi-Metric Queries

Challenge 8 demonstrates efficient data retrieval with a single ES|QL query:

```esql
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

**Benefits:**
- Single query replaces 3-4 separate queries
- Demonstrates ES|QL's EVAL and CASE capabilities
- Shows time-windowed aggregations
- Efficient for workflow step chaining

**Accessing results:**
```yaml
{{ steps.get_all_metrics.output.values[0][0] }}  # error_count
{{ steps.get_all_metrics.output.values[0][1] }}  # current_payment_count
{{ steps.get_all_metrics.output.values[0][2] }}  # current_total_amount
{{ steps.get_all_metrics.output.values[0][3] }}  # baseline_payment_count
```

### Deterministic + AI Hybrid Pattern

Challenge 8 demonstrates the recommended pattern for production automation:

1. **Deterministic Logic** makes the decision
   - Calculate metrics (payment drop percentage)
   - Compare against thresholds (> 30% drop)
   - Trigger actions (scale service)

2. **AI Layer** explains the decision
   - Provide context to stakeholders
   - Suggest follow-up investigations
   - Generate human-readable summaries

This pattern ensures reliability (no AI hallucinations in critical decisions) while maintaining explainability.

### Alert-Triggered Workflows

**Alert trigger type:**
```yaml
triggers:
  - type: alert
```

**Accessing alert data:**
```yaml
# Alert metadata
{{ event.alerts[0].id }}
{{ event.alerts[0].rule.name }}
{{ event.alerts[0].rule.id }}

# Alert timestamp
{{ event.alerts[0].timestamp }}

# Alert context (depends on rule type)
{{ event.alerts[0].context.service_name }}
```

## Testing & Validation

### Manual Workflow Testing

1. Navigate to Kibana → Management → Workflows
2. Create workflow (paste YAML or build in UI)
3. Click "Run" → Provide inputs
4. View execution history and step outputs

### Alert-Triggered Testing

**Wait for natural anomaly:**
```bash
# Data generator injects anomalies every 60-90 seconds
# Check Observability → Alerts for fired alerts
# View workflow executions in Workflows UI
```

**Force immediate incident:**
```bash
# Technical incident (Challenge 7)
bash /opt/workshop-assets/setup_scripts/04-force-incident.sh

# Business incident (Challenge 8)
bash /opt/workshop-assets/setup_scripts/06-trigger-business-incident.sh
```

### Validation Scripts

**Challenge 8 validator:**
```bash
/opt/workshop-assets/setup_scripts/solve-08-business-impact-detection
```

Checks:
- ✓ Workflow exists with correct name
- ✓ Alert trigger configured
- ✓ Required step types present (esql.query, agent_builder_converse, if, http, index)
- ✓ Expected step names (get_all_metrics, ai_business_summary, check_scaling_needed)
- ✓ Alert rule created

### Mock API Verification

```bash
# Check API logs
pm2 logs mock-api --lines 20

# Test remediation endpoint
curl -X POST http://localhost:3000/remediate_service \
  -H "Content-Type: application/json" \
  -d '{"service_name": "payment-service"}'

# Test scaling endpoint
curl -X POST http://localhost:3000/scale_service \
  -H "Content-Type: application/json" \
  -d '{"service_name": "payment-service"}'

# Check health
curl http://localhost:3000/health
```

### Audit Log Queries

Check workflow execution logs in Elasticsearch:

```json
GET workflow_actions-*/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}],
  "query": {
    "match": {
      "workflow_name": "business_impact_detector"
    }
  }
}
```

Check business action logs (Challenge 8):

```json
GET business_actions-*/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```

## Troubleshooting

### Kibana Not Ready

```bash
# Check Kibana status
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  http://kubernetes-vm:30001/api/status

# View Kibana pod logs
kubectl logs -n elastic-system $(kubectl get pods -n elastic-system -l app=kibana -o name)
```

### Data Generator Issues

```bash
# Check data sprayer logs
tail -f /var/log/data-sprayer.log

# Verify index exists
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  http://kubernetes-vm:30920/o11y-heartbeat/_count

# Check recent data
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  "http://kubernetes-vm:30920/o11y-heartbeat/_search?size=5&sort=@timestamp:desc"

# Restart data sprayer if needed
pkill -f data_sprayer.py
cd /opt/workshop-assets/data_generator
nohup python3 data_sprayer.py --live > /var/log/data-sprayer.log 2>&1 &
```

### Alert Not Firing

```bash
# List all alert rules
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  -H "kbn-xsrf: true" \
  "http://kubernetes-vm:30001/api/alerting/rules/_find"

# Check specific alert
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  -H "kbn-xsrf: true" \
  "http://kubernetes-vm:30001/api/alerting/rules/_find?search=payment"

# Force incident
bash /opt/workshop-assets/setup_scripts/04-force-incident.sh
```

### Agent Builder Issues

```bash
# List all agents
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  "http://kubernetes-vm:30001/api/agent_builder/agents"

# Test agent conversation
curl -X POST -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  "http://kubernetes-vm:30001/api/agent_builder/converse" \
  -d '{
    "agent_id": "agent_business_slo",
    "input": "Test message"
  }'
```

### Workflow Execution Issues

```bash
# List all workflows
curl -X POST -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  -H "kbn-xsrf: true" \
  -H "x-elastic-internal-origin: kibana" \
  -H "Content-Type: application/json" \
  "http://kubernetes-vm:30001/api/workflows/search" \
  -d '{"limit":100,"page":1,"query":""}'

# View workflow execution history in Kibana UI:
# Kibana → Management → Workflows → [workflow name] → Executions tab
```

### Sandbox Startup Issues

**Slow Elasticsearch ingestion:**
- The data sprayer has a 3-stage bailout (3min warning, 5min abort, rate check)
- If you see bailout errors, restart the sandbox
- This is usually caused by unhealthy Elasticsearch instances in the Instruqt infrastructure

**GitHub clone failures:**
- The setup script retries GitHub clones 3 times
- If all retries fail, restart the sandbox
- Usually caused by transient GitHub 500 errors

**k3s not starting:**
- The setup script has a two-stage retry mechanism
- Initial 5-minute wait, then restart k3s and wait 3 more minutes
- If k3s still fails after retry, this is an Instruqt platform issue - contact support

## File Structure

```
dr-rangelove-stove-store/         # Development/test track
├── README.md                      # This file
├── WORKSHOP_MARKETING.md          # Marketing 1-pager (2 versions)
├── YOUTUBE_TALKING_POINTS.md      # Video talking points
└── workshop-assets/               # Shared assets (cloned during setup)
    ├── data_generator/
    │   ├── data_sprayer.py
    │   ├── scenarios.json
    │   └── setup.py
    └── setup_scripts/
        ├── 01-create-agents.sh
        ├── 02-create-alert.sh
        ├── 03-mock-api-service.sh
        ├── 04-force-incident.sh
        ├── 05-restore-snapshot.sh
        ├── 06-trigger-business-incident.sh
        └── solve-08-business-impact-detection

instruqt/                          # Production track
├── track.yml                      # Main Instruqt track definition
├── config.yml                     # VM configuration
├── track_scripts/
│   ├── setup-kubernetes-vm        # Primary setup script
│   └── setup-host-1               # Secondary setup script
└── [01-09]-*/                     # 9 challenge directories
    ├── assignment.md              # Challenge instructions
    └── assets/
        └── solution.yml           # Solution workflow YAML
```

## Production Considerations

### Security

When deploying workflows in production:

1. **API Keys:** Use restrictive API keys with minimum required privileges
2. **Secrets Management:** Store sensitive data in Kibana secrets, not workflow constants
3. **Input Validation:** Validate and sanitize all workflow inputs
4. **Network Policies:** Restrict workflow HTTP steps to approved endpoints
5. **Audit Logging:** Always log workflow actions for compliance

### Scalability

1. **ES|QL over Query DSL:** Use ES|QL for better performance on large datasets
2. **Batch Operations:** Use bulk APIs when indexing multiple documents
3. **Async Patterns:** Chain steps efficiently to avoid blocking
4. **Rate Limiting:** Add delays or throttling for external API calls
5. **Error Budgets:** Set appropriate retry limits to prevent cascade failures

### Monitoring

1. **Workflow Execution Metrics:** Monitor execution times, success rates, failure patterns
2. **Alert Fatigue:** Tune alert thresholds to reduce noise
3. **AI Agent Costs:** Track LLM token usage if using external providers
4. **Audit Trail:** Query workflow action indexes regularly for compliance
5. **Runbook Integration:** Link workflows to incident response runbooks

## Next Steps

### For Workshop Participants

After completing the workshop:

1. **Extend to Real Services:** Connect workflows to your actual infrastructure APIs (K8s, AWS, GCP, Azure)
2. **Security Use Cases:** Build SOAR workflows for security incident response
3. **Advanced AI Patterns:** Experiment with multi-agent reasoning and tool use
4. **Production Deployment:** Apply security, monitoring, and governance practices
5. **Share Your Work:** Contribute workflow patterns back to the community

### For Instructors

To customize this workshop:

1. **Adjust Thresholds:** Modify `LATENCY_THRESHOLD`, `ERROR_THRESHOLD` in setup scripts
2. **Add Services:** Extend `SERVICES` array in data_sprayer.py
3. **Create Custom Agents:** Add new AI agents with specific personas for your use cases
4. **New Scenarios:** Add scenarios to scenarios.json for different incident types
5. **Integration Examples:** Add challenges for specific external services (PagerDuty, ServiceNow, Slack)

### Advanced Topics

Explore these topics for deeper understanding:

1. **ML Anomaly Detection:** Enable `USE_ML_AD=true` for ML-based alerts instead of threshold alerts
2. **Snapshot Restore:** Use `ES_SNAPSHOT_ID` to restore pre-built datasets
3. **Multi-Region Workflows:** Coordinate actions across multiple Elasticsearch clusters
4. **Approval Workflows:** Add human-in-the-loop approval steps with Slack/Teams
5. **Workflow Composition:** Build reusable workflow libraries and import patterns

## Resources

### Documentation

- [Elastic Workflows Documentation](https://www.elastic.co/guide/en/kibana/current/workflows.html)
- [Agent Builder API Reference](https://www.elastic.co/docs/solutions/search/agent-builder/kibana-api)
- [ES|QL Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html)
- [Instruqt Documentation](https://docs.instruqt.com/)

### Community

- **GitHub:** [jeffvestal/instruqt-workshops](https://github.com/jeffvestal/instruqt-workshops)
- **Elastic Community:** [discuss.elastic.co](https://discuss.elastic.co)
- **Contact:** jeff.vestal@elastic.co

### Related Content

- [Elastic AI Assistant Documentation](https://www.elastic.co/guide/en/security/current/ai-assistant.html)
- [Elastic Observability](https://www.elastic.co/observability)
- [Elastic SIEM](https://www.elastic.co/security/siem)

## License

Copyright © 2025 Elasticsearch B.V. All Rights Reserved.

## Acknowledgments

Special thanks to the Elastic Workflows and Agent Builder teams for building these powerful automation capabilities, and to the Instruqt team for providing an excellent platform for hands-on learning.
