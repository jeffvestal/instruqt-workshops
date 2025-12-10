#!/bin/bash
# Trigger Business Impact Incident
# Creates a flag file that the data sprayer monitors to inject business-critical degradation
# NOTE: This script must be run on kubernetes-vm (where the data sprayer runs)

set -euo pipefail

FLAG_FILE="/tmp/business_incident_active"
DURATION_MINUTES=5

echo "=========================================="
echo "💼 Triggering Business Impact Incident"
echo "=========================================="
echo ""
echo "This will simulate a payment service degradation affecting revenue:"
echo "  - Error rate increases to 15-20%"
echo "  - Successful payment transactions drop by 40%"
echo "  - Average payment amounts reduced by 30%"
echo ""
echo "Duration: ${DURATION_MINUTES} minutes"
echo ""

# Create flag file
touch "$FLAG_FILE"
echo "✅ Business incident flag created: $FLAG_FILE"
echo ""
echo "The data sprayer will now inject degraded payment service data."
echo "You can monitor the impact in Kibana Discover or via your alert rule."
echo ""
echo "To end the incident early, run:"
echo "  rm $FLAG_FILE"
echo ""
echo "The incident will auto-end after ${DURATION_MINUTES} minutes."
echo ""

