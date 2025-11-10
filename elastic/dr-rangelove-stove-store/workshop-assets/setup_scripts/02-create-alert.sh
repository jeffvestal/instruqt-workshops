#!/bin/bash
set -e

echo "[Alerting] Creating alert rule..."

# Validate required env vars
: "${KIBANA_URL:?KIBANA_URL required}"
: "${ELASTICSEARCH_APIKEY:?ELASTICSEARCH_APIKEY required}"

# Configuration with defaults
USE_ML_AD="${USE_ML_AD:-false}"
LATENCY_THRESHOLD="${LATENCY_THRESHOLD:-800}"
ERROR_THRESHOLD="${ERROR_THRESHOLD:-3}"
LOOKBACK="${LOOKBACK:-1m}"

# Common curl options
CURL_OPTS=(-fsS -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" -H "kbn-xsrf: true" -H "Content-Type: application/json")

if [[ "$USE_ML_AD" == "true" ]]; then
  echo "[Alerting] Creating ML anomaly detection rule..."
  
  curl "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/alerting/rule" -d '{
    "name": "ml-anomaly-alert-critical",
    "rule_type_id": ".ml",
    "consumer": "ml",
    "schedule": {"interval": "1m"},
    "params": {
      "jobSelection": {"jobIds": ["o11y_latency_job"]},
      "anomalyScore": 90,
      "lookbackInterval": "1h",
      "resultType": "bucket"
    },
    "actions": [],
    "notify_when": "onActiveAlert",
    "enabled": true
  }' > /dev/null 2>&1 && echo "  ✓ ml-anomaly-alert-critical created" || echo "  ⚠️  Alert may already exist"
  
else
  echo "[Alerting] Creating threshold-based ES query rule (latency >= ${LATENCY_THRESHOLD}ms)..."
  
  # Build ES query with threshold
  ES_QUERY='{"query":{"bool":{"filter":[{"range":{"latency_ms":{"gte":'${LATENCY_THRESHOLD}'}}},{"term":{"service.name":"payment-service"}}]}}}'
  
  curl "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/alerting/rule" -d '{
    "name": "latency-threshold-alert-critical",
    "rule_type_id": ".es-query",
    "consumer": "alerts",
    "schedule": {"interval": "1m"},
    "params": {
      "index": ["o11y-heartbeat"],
      "timeField": "@timestamp",
      "esQuery": "'"${ES_QUERY}"'",
      "threshold": [1],
      "thresholdComparator": ">=",
      "size": 100,
      "timeWindowSize": 1,
      "timeWindowUnit": "m"
    },
    "actions": [],
    "notify_when": "onActiveAlert",
    "enabled": true
  }' > /dev/null 2>&1 && echo "  ✓ latency-threshold-alert-critical created" || echo "  ⚠️  Alert may already exist"
  
fi

echo "[Alerting] Alert rule creation complete"

