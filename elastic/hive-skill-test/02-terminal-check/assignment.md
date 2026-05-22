---
slug: terminal-check
id: vhc6gxybtori
type: challenge
title: Query Elasticsearch from the Terminal
teaser: Use curl to query the Elasticsearch cluster and check what's running
notes:
- type: text
  contents: |
    ## Elasticsearch from the Command Line

    Elasticsearch exposes a REST API. You can query it directly using `curl`
    from the terminal — no UI required.

    In this challenge, you'll check cluster health and list available indices.
tabs:
- id: todrutkpjr8y
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: basic
timelimit: 600
enhanced_loading: null
---

## Overview

Your Elastic cluster is running on `kubernetes-vm`. In this challenge you'll use the
Terminal tab to run a few `curl` commands against Elasticsearch.

## What You'll Do

- Check the cluster health status
- List the available indices
- Run a simple search query

## Steps

### 1. Check Cluster Health

In the **Terminal** tab, run:

```bash
curl -s "${ELASTICSEARCH_URL}/_cluster/health" \
  -H "Authorization: Basic ${ELASTICSEARCH_AUTH_BASE64}" | jq .
```

You should see a JSON response with `"status": "green"` or `"yellow"`.

> **Hint**: All env vars (`ELASTICSEARCH_URL`, `ELASTICSEARCH_AUTH_BASE64`, etc.) are loaded from the preset at track start. Run `env | grep ELASTIC` to see them.

### 2. List Indices

```bash
curl -s "${ELASTICSEARCH_URL}/_cat/indices?v" \
  -H "Authorization: Basic ${ELASTICSEARCH_AUTH_BASE64}"
```

This returns a table of all indices with their document counts and sizes.

### 3. Run a Search Query

```bash
curl -s "${ELASTICSEARCH_URL}/_search?pretty" \
  -H "Authorization: Basic ${ELASTICSEARCH_AUTH_BASE64}" \
  -H "Content-Type: application/json" \
  -d '{"query": {"match_all": {}}, "size": 3}'
```

## Verify

After running the cluster health check, you should see a JSON response containing a `"status"` field.
The `_cat/indices` output should show at least one index (Kibana creates several on startup).

<details>
<summary>Not seeing output? Expand for troubleshooting</summary>

If `ELASTICSEARCH_URL` is empty, the env bootstrap may still be running. Load manually:

```bash
export $(curl -s http://kubernetes-vm:9000/env | xargs)
```

</details>
