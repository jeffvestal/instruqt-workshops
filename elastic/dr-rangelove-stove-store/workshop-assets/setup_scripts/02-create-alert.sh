#!/bin/bash
set -e

echo "[Alerting] Creating alert rule(s)..."

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
  
  ALERT_NAME="ml-anomaly-alert-critical"
  RESPONSE=$(curl -s -w "\n%{http_code}" "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/alerting/rule" -d '{
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
  }')
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "  ✓ ${ALERT_NAME} created successfully"
  else
    echo "  ✗ ERROR: Alert creation failed (HTTP ${HTTP_CODE})"
    echo "  Response: ${BODY}"
    exit 1
  fi
  
else
  echo "[Alerting] Creating threshold-based ES query rule (latency >= ${LATENCY_THRESHOLD}ms)..."
  echo "[Alerting] Using Kibana URL: ${KIBANA_URL}"
  
  ALERT_NAME="latency-threshold-alert-critical"
  
  # Check if alert already exists
  echo "[Alerting] Checking for existing alert..."
  CHECK_RESPONSE=$(curl -s -w "\n%{http_code}" "${CURL_OPTS[@]}" -X GET "${KIBANA_URL}/api/alerting/rules/_find?search=${ALERT_NAME}")
  CHECK_HTTP_CODE=$(echo "$CHECK_RESPONSE" | tail -n1)
  CHECK_BODY=$(echo "$CHECK_RESPONSE" | sed '$d')
  
  if [ "$CHECK_HTTP_CODE" = "200" ]; then
    EXISTING_COUNT=$(echo "$CHECK_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))" 2>/dev/null || echo "0")
    if [ "$EXISTING_COUNT" -gt 0 ]; then
      echo "[Alerting] Alert already exists, deleting old version..."
      EXISTING_ID=$(echo "$CHECK_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data'][0]['id'] if data.get('data') else '')" 2>/dev/null)
      if [ -n "$EXISTING_ID" ]; then
        curl -s "${CURL_OPTS[@]}" -X DELETE "${KIBANA_URL}/api/alerting/rule/${EXISTING_ID}" > /dev/null 2>&1
        echo "[Alerting] Deleted existing alert (ID: ${EXISTING_ID})"
        sleep 2
      fi
    fi
  fi
  
  # Build ES query with threshold
  ES_QUERY='{"query":{"bool":{"filter":[{"range":{"latency_ms":{"gte":'${LATENCY_THRESHOLD}'}}},{"term":{"service.name":"payment-service"}}]}}}'
  
  echo "[Alerting] Creating new alert rule..."
  
  # Use jq to build the JSON payload properly (avoids JSON escaping issues)
  PAYLOAD=$(jq -n \
    --arg esQuery "$ES_QUERY" \
    '{
    "name": "latency-threshold-alert-critical",
    "rule_type_id": ".es-query",
    "consumer": "alerts",
    "schedule": {"interval": "1m"},
    "params": {
      "index": ["o11y-heartbeat"],
      "timeField": "@timestamp",
        "esQuery": $esQuery,
      "threshold": [1],
      "thresholdComparator": ">=",
      "size": 100,
      "timeWindowSize": 1,
      "timeWindowUnit": "m"
    },
    "actions": [],
    "notify_when": "onActiveAlert",
    "enabled": true
    }')
  
  RESPONSE=$(curl -s -w "\n%{http_code}" "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/alerting/rule" -d "$PAYLOAD")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    ALERT_ID=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "  ✓ ${ALERT_NAME} created successfully (ID: ${ALERT_ID})"
  else
    echo "  ✗ ERROR: Alert creation failed (HTTP ${HTTP_CODE})"
    echo "  Response: ${BODY}"
    echo "  Kibana URL: ${KIBANA_URL}"
    echo "  API Key present: $([ -n "${ELASTICSEARCH_APIKEY}" ] && echo 'yes' || echo 'no')"
    exit 1
  fi
  
fi

# Verify primary alert rule exists
echo "[Alerting] Verifying primary alert rule exists..."
VERIFY_RESPONSE=$(curl -s -w "\n%{http_code}" "${CURL_OPTS[@]}" -X GET "${KIBANA_URL}/api/alerting/rules/_find?search=${ALERT_NAME}")
VERIFY_HTTP_CODE=$(echo "$VERIFY_RESPONSE" | tail -n1)
VERIFY_BODY=$(echo "$VERIFY_RESPONSE" | sed '$d')

if [ "$VERIFY_HTTP_CODE" = "200" ]; then
  RULE_COUNT=$(echo "$VERIFY_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', [])))" 2>/dev/null || echo "0")
  if [ "$RULE_COUNT" -gt 0 ]; then
    echo "  ✓ Verified: ${ALERT_NAME} exists in Kibana"
  else
    echo "  ⚠️  Warning: Alert rule not found in verification query"
  fi
else
  echo "  ⚠️  Warning: Could not verify alert rule (HTTP ${VERIFY_HTTP_CODE})"
fi

echo "[Alerting] Ensuring business impact alert rule exists..."
BUSINESS_ALERT_NAME="business-impact-payment-degradation"

# Check if the business impact alert already exists
BUSINESS_CHECK_RESPONSE=$(curl -s -w "\n%{http_code}" "${CURL_OPTS[@]}" -X GET "${KIBANA_URL}/api/alerting/rules/_find?search=${BUSINESS_ALERT_NAME}")
BUSINESS_CHECK_HTTP_CODE=$(echo "$BUSINESS_CHECK_RESPONSE" | tail -n1)
BUSINESS_CHECK_BODY=$(echo "$BUSINESS_CHECK_RESPONSE" | sed '$d')

BUSINESS_EXISTING_COUNT="0"
if [ "$BUSINESS_CHECK_HTTP_CODE" = "200" ]; then
  BUSINESS_EXISTING_COUNT=$(echo "$BUSINESS_CHECK_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))" 2>/dev/null || echo "0")
fi

if [ "$BUSINESS_EXISTING_COUNT" -gt 0 ]; then
  echo "  ✓ ${BUSINESS_ALERT_NAME} already exists"
else
  echo "[Alerting] Creating business impact alert rule..."

  BUSINESS_ES_QUERY='{"query":{"bool":{"filter":[{"range":{"http.status_code":{"gte":500}}},{"term":{"service.name":"payment-service"}}]}}}'

  BUSINESS_PAYLOAD=$(jq -n \
    --arg esQuery "$BUSINESS_ES_QUERY" \
    '{
    "name": "business-impact-payment-degradation",
    "rule_type_id": ".es-query",
    "consumer": "alerts",
    "schedule": {"interval": "1m"},
    "params": {
      "index": ["o11y-heartbeat"],
      "timeField": "@timestamp",
      "esQuery": $esQuery,
      "threshold": [1],
      "thresholdComparator": ">=",
      "size": 100,
      "timeWindowSize": 5,
      "timeWindowUnit": "m"
    },
    "actions": [],
    "notify_when": "onActiveAlert",
    "enabled": true
    }')

  BUSINESS_RESPONSE=$(curl -s -w "\n%{http_code}" "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/alerting/rule" -d "$BUSINESS_PAYLOAD")

  BUSINESS_HTTP_CODE=$(echo "$BUSINESS_RESPONSE" | tail -n1)
  BUSINESS_BODY=$(echo "$BUSINESS_RESPONSE" | sed '$d')

  if [ "$BUSINESS_HTTP_CODE" = "200" ] || [ "$BUSINESS_HTTP_CODE" = "201" ]; then
    BUSINESS_ALERT_ID=$(echo "$BUSINESS_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get(\"id\", \"unknown\"))" 2>/dev/null || echo "unknown")
    echo "  ✓ ${BUSINESS_ALERT_NAME} created successfully (ID: ${BUSINESS_ALERT_ID})"
  else
    echo "  ✗ ERROR: Business impact alert creation failed (HTTP ${BUSINESS_HTTP_CODE})"
    echo "  Response: ${BUSINESS_BODY}"
  fi
fi

echo "[Alerting] Alert rule creation complete"

