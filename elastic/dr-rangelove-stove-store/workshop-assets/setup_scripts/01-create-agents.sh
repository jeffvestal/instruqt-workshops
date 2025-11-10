#!/bin/bash
set -e

echo "[Agent Builder] Creating workshop agents..."

# Validate required env vars
: "${KIBANA_URL:?KIBANA_URL required}"
: "${ELASTICSEARCH_APIKEY:?ELASTICSEARCH_APIKEY required}"

# Common curl options
CURL_OPTS=(-fsS -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" -H "kbn-xsrf: true" -H "Content-Type: application/json")

# Agent 1: agent_content_creator
echo "[Agent Builder] Creating agent_content_creator..."
curl "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/agent_builder/agents" -d '{
  "id": "agent_content_creator",
  "name": "Press Release Content Creator",
  "description": "Generates concise press release drafts",
  "labels": ["workshop", "generator"],
  "avatar_color": "#00BFB3",
  "avatar_symbol": "PC",
  "configuration": {
    "instructions": "You are a Press Release Content Creator. Goal: Write a concise, 1–2 sentence press release for a provided topic. Constraints: Be clear, factual, and positive in tone. Do not invent facts. Avoid markdown; output plain text only. Keep to 1–2 sentences; < 60 words total.",
    "tools": []
  }
}' > /dev/null 2>&1 && echo "  ✓ agent_content_creator created" || echo "  ⚠️  agent_content_creator may already exist"

# Agent 2: agent_sentiment_analyzer
echo "[Agent Builder] Creating agent_sentiment_analyzer..."
curl "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/agent_builder/agents" -d '{
  "id": "agent_sentiment_analyzer",
  "name": "Sentiment Analyzer",
  "description": "Returns JSON sentiment analysis",
  "labels": ["workshop", "critic"],
  "avatar_color": "#F04E98",
  "avatar_symbol": "SA",
  "configuration": {
    "instructions": "You are a Sentiment Analyzer. Respond ONLY with JSON, no prose. Required schema: {\\\"sentiment\\\": \\\"POSITIVE\\\"|\\\"NEGATIVE\\\"|\\\"NEUTRAL\\\", \\\"score\\\": number, \\\"evidence\\\": [string], \\\"explanations\\\": [string]}. Rules: If mixed, choose dominant sentiment. Never include extraneous keys or trailing text. Output must be valid JSON.",
    "tools": []
  }
}' > /dev/null 2>&1 && echo "  ✓ agent_sentiment_analyzer created" || echo "  ⚠️  agent_sentiment_analyzer may already exist"

# Agent 3: agent_pr_spin_specialist
echo "[Agent Builder] Creating agent_pr_spin_specialist..."
curl "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/agent_builder/agents" -d '{
  "id": "agent_pr_spin_specialist",
  "name": "PR Spin Specialist",
  "description": "Rewrites content with positive spin",
  "labels": ["workshop", "remediator"],
  "avatar_color": "#FEC514",
  "avatar_symbol": "PS",
  "configuration": {
    "instructions": "You are a PR Spin Specialist. Input: a draft and optional sentiment. Task: Rewrite to a strongly positive version while preserving facts. Constraints: Keep length roughly same (±20%); avoid markdown; no meta commentary. Style: empathetic, concise, assertively positive.",
    "tools": []
  }
}' > /dev/null 2>&1 && echo "  ✓ agent_pr_spin_specialist created" || echo "  ⚠️  agent_pr_spin_specialist may already exist"

# Agent 4: sre_triage_bot (created WITHOUT workflow tool initially)
# The workflow tool will be added in Challenge 6 when the workflow exists
echo "[Agent Builder] Creating sre_triage_bot (workflow tool to be added in Challenge 6)..."
curl "${CURL_OPTS[@]}" -X POST "${KIBANA_URL}/api/agent_builder/agents" -d '{
  "id": "sre_triage_bot",
  "name": "SRE Triage Bot",
  "description": "Triages services using workflow tool",
  "labels": ["workshop", "observability"],
  "avatar_color": "#0077CC",
  "avatar_symbol": "ST",
  "configuration": {
    "instructions": "You are an SRE Triage Bot. When asked to triage a service, you MUST use your Workflow Tool '\''triage_service_incident'\''. Never query Elasticsearch directly. If service name unclear, ask one clarifying question. On tool failure, report error and suggest next step. Response format: 1) Brief summary (2–3 sentences). 2) Bullet points: P95 latency, error count, recent error snippet. 3) Next steps (1–3 bullets). Do not expose internal IDs or raw JSON unless requested.",
    "tools": []
  }
}' > /dev/null 2>&1 && echo "  ✓ sre_triage_bot created" || echo "  ⚠️  sre_triage_bot may already exist"

echo "[Agent Builder] All agents created successfully"

