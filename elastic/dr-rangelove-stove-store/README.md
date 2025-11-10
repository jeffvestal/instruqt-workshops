# Elastic Workflow & AI Agent Workshop

**"From Insights to Outcomes: Automating with Elastic Workflows & AI"**

## Overview

This hands-on Instruqt workshop teaches users how to build, test, and orchestrate automated workflows and AI agents in Elastic. Participants progress from simple automation to building a complete self-healing AIOps system.

## Workshop Structure

### Challenges

1. **The "Why": From Insights to Outcomes** - Introduction to the "Two-Vendor Problem" and how Workflows solve it
2. **Building Your First Workflow** - Create a simple workflow with inputs and console output
3. **Chaining Steps** - Build workflows that chain HTTP calls with data transformation
4. **Making it Robust** - Add retry logic and conditional branching
5. **The AI "Assembly Line"** - Orchestrate multiple AI agents in generator-critic-remediator pattern
6. **The "Full Circle": AI Agent Tools** - Give an AI agent a workflow as a tool
7. **Capstone: Build a "Self-Healing" Workflow** - Create alert-triggered automation with AI and external APIs

## Architecture

### VMs

- **kubernetes-vm**: Runs Elastic stack (ES + Kibana), hosts Agent Builder agents and workflows
  - Elasticsearch: port 30920
  - Kibana: port 30001
  - Env server: port 9000
- **host-1**: Runs Docker containers and mock API
  - Mock Remediation API: port 3000

### Setup Flow

1. `track_scripts/setup-kubernetes-vm` runs first:
   - Starts Elastic Stack
   - Exposes env vars via HTTP server on port 9000
   - Creates `o11y-heartbeat` index and generates data
   - Creates 4 AI agents via Agent Builder API
   - Creates alert rule (threshold or ML-based)
   - Optionally forces an incident for testing

2. `track_scripts/setup-host-1` runs second:
   - Pulls env vars from kubernetes-vm
   - Installs Node.js 20.x and pm2
   - Starts mock remediation API on port 3000

## Configuration

### Environment Variables

Set these in the Instruqt track or via secrets:

- `KIBANA_URL` - Kibana URL (default: http://localhost:30001)
- `ELASTICSEARCH_URL` - Elasticsearch URL (default: http://localhost:30920)
- `ELASTICSEARCH_APIKEY` - API key with full privileges
- `USE_ML_AD` - Use ML anomaly detection (default: false, uses threshold alert)
- `FORCE_INCIDENT` - Inject spike on startup (default: false)
- `LATENCY_THRESHOLD` - Latency threshold in ms (default: 800)
- `ERROR_THRESHOLD` - Error count threshold (default: 3)
- `LOOKBACK` - Alert time window (default: 1m)
- `ES_SNAPSHOT_ID` - Optional snapshot to restore

### Toggles

#### Threshold vs ML Anomaly Detection

**Default (Threshold-based):**
```bash
export USE_ML_AD=false
export LATENCY_THRESHOLD=800
```

Creates `.es-query` alert that triggers when `latency_ms >= 800` for `payment-service`.

**ML-based (Optional):**
```bash
export USE_ML_AD=true
```

Creates `.ml` alert that triggers on ML anomaly score >= 90 for `o11y_latency_job`.

#### Force Incident

```bash
export FORCE_INCIDENT=true
```

Injects 10 high-latency/5xx documents immediately to trigger alert for testing.

## Setup Scripts

### Helper Scripts (`setup_scripts/`)

- `01-create-agents.sh` - Creates 4 AI agents:
  - `agent_content_creator` - Press release generator
  - `agent_sentiment_analyzer` - JSON sentiment analysis
  - `agent_pr_spin_specialist` - Content remediation
  - `sre_triage_bot` - Observability triage (accepts workflow tool in Challenge 6)

- `02-create-alert.sh` - Creates alert rule (threshold or ML based on `USE_ML_AD`)

- `03-mock-api-service.sh` - Creates Express server with `/remediate_service` endpoint

- `04-force-incident.sh` - Injects anomalous data (optional, controlled by `FORCE_INCIDENT`)

- `05-restore-snapshot.sh` - Placeholder for snapshot restore (awaiting `ES_SNAPSHOT_ID`)

### Track Scripts (`track_scripts/`)

- `setup-kubernetes-vm` - Full Elastic stack setup, data generation, agents, alerts
- `setup-host-1` - Node.js installation and mock API setup

## Data Generator

The workshop includes a minimal Python-based data generator that:

- Creates `o11y-heartbeat` index with proper mappings
- Backfills 90 days of historical data
- Runs live data stream with periodic anomalies
- Services: `payment-service`, `checkout-service`, `cart-service`, `user-service`
- Normal latency: 50-300ms, status codes: 200/201/204
- Anomaly latency: 1500-3000ms, status codes: 500/502/503/504
- Anomaly injection: Every ~60 seconds for `payment-service`

## Workflow Examples

All workflow solutions are provided in `challenges/*/assets/solution.yml`:

- `hello_world.yml` - Simple input/output
- `ip_geolocator.yml` - HTTP API calls with chaining
- `ip_geolocator` (robust).yml - Error handling and conditionals
- `ai_content_chain.yml` - Multi-agent orchestration
- `triage_service_incident.yml` - Elasticsearch queries for observability
- `self_healing_aiops.yml` - Alert-triggered automation with AI and external API calls

## Key Workflow Concepts

### Step Types

- `console` - Print messages
- `http` - HTTP requests
- `elasticsearch.search` - Query Elasticsearch
- `elasticsearch.index` - Index documents
- `kibana.post_agent_builder_converse` - Call AI agents
- `if` - Conditional branching

### Data Access

- `{{ inputs.name }}` - Workflow inputs
- `{{ consts.name }}` - Constants
- `{{ steps.step_name.output.field }}` - Step outputs
- `{{ trigger.data.* }}` - Alert trigger data
- `{{ now() }}` - Current timestamp

### Error Handling

```yaml
on-failure:
  retry:
    max-attempts: 2
    delay: 1s
  fallback:
    - name: fallback_step
      type: console
      with:
        message: "Error: {{ steps.step_name.error }}"
```

## Testing

### Manual Workflow Testing

1. Go to Kibana > Management > Dev Tools > Workflows
2. Create workflow from solution YAMLs
3. Click "Run" and provide inputs
4. Inspect step outputs in UI

### Alert-Triggered Workflow Testing

1. Wait for live data sprayer to inject anomalies (~60s intervals)
2. Check Observability > Alerts for fired alerts
3. Go to Workflows UI and view automatic runs
4. Or force immediately: `bash setup_scripts/04-force-incident.sh`

### Verify Mock API

```bash
# Check logs
pm2 logs mock-api --lines 20

# Manual test
curl -X POST http://localhost:3000/remediate_service \
  -H "Content-Type: application/json" \
  -d '{"service_name": "payment-service"}'
```

### Check Workflow Audit Logs

```
GET workflow_actions-*/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```

## Troubleshooting

### Kibana Not Ready

```bash
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" $KIBANA_URL/api/status
```

### Data Generator Issues

```bash
# Check data generator logs
tail -f /var/log/data-sprayer.log

# Verify index exists
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" $ELASTICSEARCH_URL/o11y-heartbeat/_count

# Check for recent data
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  "$ELASTICSEARCH_URL/o11y-heartbeat/_search?size=5&sort=@timestamp:desc"
```

### Alert Not Firing

```bash
# Check alert status via Kibana API
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" -H "kbn-xsrf: true" \
  "$KIBANA_URL/api/alerting/rules/_find"

# Force incident manually
bash /opt/workshop/setup_scripts/04-force-incident.sh
```

### Agent Builder Issues

```bash
# List all agents
curl -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  "$KIBANA_URL/api/agent_builder/agents"

# Test agent conversation
curl -X POST -H "Authorization: ApiKey $ELASTICSEARCH_APIKEY" \
  -H "kbn-xsrf: true" -H "Content-Type: application/json" \
  "$KIBANA_URL/api/agent_builder/converse" \
  -d '{"agent_id": "agent_content_creator", "input": "Hello"}'
```

## File Structure

```
dr-rangelove-stove-store/
├── track.yml                              # Main Instruqt track definition
├── config.yml                             # Track configuration
├── README.md                              # This file
├── track_scripts/
│   ├── setup-kubernetes-vm                # k8s VM setup script
│   └── setup-host-1                       # host-1 VM setup script
├── setup_scripts/
│   ├── 01-create-agents.sh                # Create 4 AI agents
│   ├── 02-create-alert.sh                 # Create alert rule
│   ├── 03-mock-api-service.sh             # Start mock API
│   ├── 04-force-incident.sh               # Inject anomalies
│   └── 05-restore-snapshot.sh             # Snapshot restore (placeholder)
└── challenges/
    ├── 01-intro/
    │   └── assignment.md
    ├── 02-hello-world/
    │   ├── assignment.md
    │   └── assets/solution.yml
    ├── 03-chaining-steps/
    │   ├── assignment.md
    │   └── assets/solution.yml
    ├── 04-robust-workflows/
    │   ├── assignment.md
    │   └── assets/solution.yml
    ├── 05-ai-orchestration/
    │   ├── assignment.md
    │   └── assets/solution.yml
    ├── 06-observability-bot/
    │   ├── assignment.md
    │   └── assets/workflow-solution.yml
    └── 07-capstone-aiops/
        ├── assignment.md
        └── assets/solution.yml
```

## Next Steps

### For Users

After completing the workshop:

1. Explore ML-based anomaly detection (`USE_ML_AD=true`)
2. Build more sophisticated multi-step AI reasoning
3. Integrate with real remediation APIs (K8s, cloud providers)
4. Add approval workflows with Slack/Teams
5. Expand to security use cases (SOAR workflows)

### For Instructors

To customize the workshop:

1. Modify `LATENCY_THRESHOLD` to adjust sensitivity
2. Add new services in data generator `SERVICES` array
3. Create additional AI agents with different personas
4. Add new workflow step types as they become available
5. Integrate with external services (PagerDuty, ServiceNow, etc.)

## References

- [Elastic Agent Builder Kibana APIs](https://www.elastic.co/docs/solutions/search/agent-builder/kibana-api)
- [Elastic Workflows Documentation](https://www.elastic.co/guide/en/kibana/current/workflows.html) (when available)
- [Instruqt Documentation](https://docs.instruqt.com/)

## Support

For issues or questions about this workshop:

1. Check the troubleshooting section above
2. Review setup script logs on kubernetes-vm and host-1
3. Contact: jeff.vestal@elastic.co

## License

Copyright © 2025 Elasticsearch B.V. All Rights Reserved.

