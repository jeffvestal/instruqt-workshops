#!/bin/bash
set -e

echo "[Force Incident] Injecting anomalous data for payment-service..."

# Validate required env vars
: "${ELASTICSEARCH_URL:?ELASTICSEARCH_URL required}"
: "${ELASTICSEARCH_APIKEY:?ELASTICSEARCH_APIKEY required}"

# Configuration
SERVICE_NAME="${FORCE_INCIDENT_SERVICE:-payment-service}"
ANOMALY_LATENCY="${FORCE_INCIDENT_LATENCY:-2500}"
ERROR_CODE="${FORCE_INCIDENT_ERROR_CODE:-503}"
DOC_COUNT="${FORCE_INCIDENT_COUNT:-10}"

echo "[Force Incident] Config: service=${SERVICE_NAME}, latency=${ANOMALY_LATENCY}ms, status=${ERROR_CODE}, count=${DOC_COUNT}"

for i in $(seq 1 $DOC_COUNT); do
  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)
  
  curl -fsS -X POST "${ELASTICSEARCH_URL}/o11y-heartbeat/_doc" \
    -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" \
    -H "Content-Type: application/json" \
    -d '{
      "@timestamp": "'"${TIMESTAMP}"'",
      "service": {"name": "'"${SERVICE_NAME}"'"},
      "latency_ms": '"${ANOMALY_LATENCY}"',
      "http": {"status_code": '"${ERROR_CODE}"'},
      "log": {"message": "Forced anomaly for workshop demo - high latency detected"}
    }' > /dev/null
  
  echo "  [$i/${DOC_COUNT}] Injected anomalous doc at ${TIMESTAMP}"
  sleep 0.5
done

echo "[Force Incident] Successfully injected ${DOC_COUNT} anomalous documents"
echo "[Force Incident] Alert should trigger within 1-2 minutes"

