# Instruqt Track Development Reference

This document provides comprehensive information about Instruqt track structure, configuration, and development patterns for creating educational tracks.

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [Track Configuration](#track-configuration)
3. [Challenge Structure](#challenge-structure)
4. [Setup Scripts](#setup-scripts)
5. [Best Practices](#best-practices)

---

## Directory Structure

### Standard Track Layout

```
track-name/
├── track.yml                 # Main track configuration
├── config.yml                # Infrastructure and secrets configuration
├── track_scripts/            # Setup scripts per VM hostname
│   ├── setup-host-1
│   └── setup-kubernetes-vm
├── assets/                   # Track-level assets (images, shared files)
│   └── *.png
├── 01-01-intro/             # Challenge folders (XX-slug format)
│   ├── assignment.md
│   └── assets/
│       └── solution.yml
├── 02-02-hello-world/
│   ├── assignment.md
│   └── assets/
│       └── solution.yml
└── ...
```

### Key Directories

**`track_scripts/`**
- Contains setup scripts that run on specific VMs
- Script names should match VM hostnames from `config.yml`
- Example: `setup-host-1` runs on VM named `host-1`
- Example: `setup-kubernetes-vm` runs on VM named `kubernetes-vm`

**`assets/` (Track-level)**
- Shared images and resources used across multiple challenges
- Referenced in assignments using relative paths: `../assets/image.png`

**`XX-slug-name/assets/` (Challenge-level)**
- Challenge-specific solution files
- Typically contains `solution.yml` or other reference implementations
- May contain challenge-specific images

### Challenge Naming Convention

Challenges follow the pattern: `XX-slug-name`

- `XX` - Two-digit sequential number (01, 02, 03, etc.)
- `slug` - Short identifier (matches slug in assignment.md)
- `name` - Descriptive name (kebab-case)

Examples:
- `01-01-intro`
- `02-02-hello-world`
- `08-08-business-impact-detection`

---

## Track Configuration

### track.yml

The main track configuration file defines metadata, timing, and UI settings.

**Required Fields:**

```yaml
slug: workflows-agents-alerts
id: tvu7yvg32vsk
title: 'From Findings to Outcomes: Automating with Elastic Workflows & Agents'
teaser: Transform alerts into automated actions. Build workflows that chain steps,
  orchestrate Agent Builder agents, and create self-healing systems—all within Elastic.
description: Learn to build, test, and orchestrate automated workflows and AI agents
  in Elastic. Build a self-healing system from scratch.
```

**Optional Metadata:**

```yaml
icon: ""                    # Icon URL or path
tags:                       # Array of tags for categorization
  - ai
  - aiops
  - workflows
  - agents
  - automation
owner: elastic              # Track owner
developers:                 # Array of developer emails
  - jeff.vestal@elastic.co
```

**Timing Configuration:**

```yaml
show_timer: true            # Show countdown timer in UI
idle_timeout: 14400        # Seconds before idle timeout (4 hours)
timelimit: 14400           # Total time limit for track (4 hours)
```

**Lab Configuration:**

```yaml
lab_config:
  extend_ttl: 10800        # TTL extension in seconds (3 hours)
  sidebar_enabled: true    # Show sidebar navigation
  feedback_recap_enabled: true   # Show feedback recap
  feedback_tab_enabled: false    # Show feedback tab
  loadingMessages: true    # Show loading messages
  theme:
    name: modern-dark      # UI theme (modern-dark, modern-light, etc.)
  override_challenge_layout: false
  hideStopButton: false
```

**Complete Example:**

```yaml
slug: workflows-agents-alerts
id: tvu7yvg32vsk
title: 'From Findings to Outcomes: Automating with Elastic Workflows & Agents'
teaser: Transform alerts into automated actions. Build workflows that chain steps,
  orchestrate Agent Builder agents, and create self-healing systems—all within Elastic.
description: Learn to build, test, and orchestrate automated workflows and AI agents
  in Elastic. Build a self-healing system from scratch.
icon: ""
tags:
  - ai
  - aiops
  - workflows
  - agents
  - automation
owner: elastic
developers:
  - jeff.vestal@elastic.co
show_timer: true
idle_timeout: 14400
timelimit: 14400
lab_config:
  extend_ttl: 10800
  sidebar_enabled: true
  feedback_recap_enabled: true
  feedback_tab_enabled: false
  loadingMessages: true
  theme:
    name: modern-dark
  override_challenge_layout: false
  hideStopButton: false
checksum: "17476444101118246146"
enhanced_loading: false
```

### config.yml

Defines virtual machines, environment variables, and secrets.

**Version:**

```yaml
version: "3"
```

**Virtual Machines:**

```yaml
virtualmachines:
  - name: host-1                    # VM hostname (must match setup script name)
    image: elastic-security-education/pk-instruqt-gcp-worker-9-3-0-main-v1-1-1-14-g725f878
    shell: /bin/bash
    memory: 8192                     # Memory in MB
    cpus: 4                          # CPU count
    allow_external_ingress:          # Ports to expose externally
      - https
    provision_ssl_certificate: true  # Auto-provision SSL certs

  - name: kubernetes-vm
    image: elastic-security-education/pk-instruqt-gcp-elastic-9-3-0-main-v1-1-1-14-g725f878
    shell: /bin/bash
    environment:                     # Environment variables for this VM
      INSTRUQT: "true"
      LLM_KEY_DURATION: 1d
      LLM_KEY_MAX_BUDGET: "25"
      LLM_MODELS: '["gpt-3.5-turbo","gpt-4.1","gpt-4o","gpt-4o-westus","eval-gpt-4o","anthropic","cohere","gemini-1.0","claude-sonnet-4"]'
      LLM_PROXY_URL: litellm-proxy-service-1059491012611.us-central1.run.app
    memory: 16384
    cpus: 16
    allow_external_ingress:
      - https
    provision_ssl_certificate: true
```

**Secrets:**

```yaml
secrets:
  - name: SA_LLM_PROXY_BEARER_TOKEN
  - name: GCSKEY_ELASTIC_SA
  - name: GCSKEY_EDEN_WORKSHOP
  - name: GCS_KEY_EDUCATION
  - name: GCSKEY
  - name: KIBANA_SMTP_USER
  - name: KIBANA_SMTP_PASS
  - name: GCSKEY_CE_INFRA_CONTAINERS
```

**Complete Example:**

```yaml
version: "3"
virtualmachines:
  - name: host-1
    image: elastic-security-education/pk-instruqt-gcp-worker-9-3-0-main-v1-1-1-14-g725f878
    shell: /bin/bash
    memory: 8192
    cpus: 4
    allow_external_ingress:
      - https
    provision_ssl_certificate: true
  - name: kubernetes-vm
    image: elastic-security-education/pk-instruqt-gcp-elastic-9-3-0-main-v1-1-1-14-g725f878
    shell: /bin/bash
    environment:
      INSTRUQT: "true"
      LLM_KEY_DURATION: 1d
      LLM_KEY_MAX_BUDGET: "25"
      LLM_MODELS: '["gpt-3.5-turbo","gpt-4.1","gpt-4o","gpt-4o-westus","eval-gpt-4o","anthropic","cohere","gemini-1.0","claude-sonnet-4"]'
      LLM_PROXY_URL: litellm-proxy-service-1059491012611.us-central1.run.app
    memory: 16384
    cpus: 16
    allow_external_ingress:
      - https
    provision_ssl_certificate: true
secrets:
  - name: SA_LLM_PROXY_BEARER_TOKEN
  - name: GCSKEY_ELASTIC_SA
  - name: GCSKEY_EDEN_WORKSHOP
  - name: GCS_KEY_EDUCATION
  - name: GCSKEY
  - name: KIBANA_SMTP_USER
  - name: KIBANA_SMTP_PASS
  - name: GCSKEY_CE_INFRA_CONTAINERS
```

---

## Challenge Structure

### assignment.md

Each challenge has an `assignment.md` file with YAML frontmatter and markdown content.

**YAML Frontmatter:**

```yaml
---
slug: 02-hello-world
id: sunyyx6xqswh
type: challenge
title: Building Your First Workflow
teaser: Create a simple workflow with inputs and console output
tabs:
  - id: rtyf1nawuqkv
    title: Kibana - Workflows
    type: service
    hostname: kubernetes-vm
    path: /app/workflows
    port: 30001
  - id: kjq04qixcpft
    title: Terminal
    type: terminal
    hostname: host-1
difficulty: basic
timelimit: 600
enhanced_loading: null
---
```

**Frontmatter Fields:**

- `slug` - Challenge identifier (should match directory name suffix)
- `id` - Unique challenge ID (generated by Instruqt)
- `type` - Always `challenge`
- `title` - Display title
- `teaser` - Short description shown in challenge list
- `tabs` - Array of tab definitions (see below)
- `difficulty` - `basic`, `intermediate`, or `advanced`
- `timelimit` - Time limit in seconds
- `enhanced_loading` - Usually `null`

**Tab Types:**

**Service Tab (Kibana/Web UI):**
```yaml
tabs:
  - id: unique-tab-id
    title: Kibana - Workflows
    type: service
    hostname: kubernetes-vm      # VM name from config.yml
    path: /app/workflows          # Application path
    port: 30001                   # Port number
```

**Terminal Tab:**
```yaml
tabs:
  - id: unique-tab-id
    title: Terminal
    type: terminal
    hostname: host-1              # VM name from config.yml
```

**Code Tab:**
```yaml
tabs:
  - id: unique-tab-id
    title: Code Editor
    type: code
    hostname: host-1
    path: /path/to/file
```

**Markdown Content:**

After the frontmatter, use standard markdown with Instruqt-specific features:

**Button Links:**
```markdown
In the [button label="Kibana"](tab-0) tab:
```

**Images:**
```markdown
![Image description](../assets/CleanShot%202025-11-13%20at%2011.12.10%402x.png)
```

**Code Blocks:**
```markdown
```yaml
version: "1"
name: hello_world
```
```

**Collapsible Sections:**
```markdown
<details>
  <summary>Click to see Full YAML</summary>

```yaml
# Full code here
```

</details>
```

**Complete Example:**

```markdown
---
slug: 02-hello-world
id: sunyyx6xqswh
type: challenge
title: Building Your First Workflow
teaser: Create a simple workflow with inputs and console output
tabs:
  - id: rtyf1nawuqkv
    title: Kibana - Workflows
    type: service
    hostname: kubernetes-vm
    path: /app/workflows
    port: 30001
  - id: kjq04qixcpft
    title: Terminal
    type: terminal
    hostname: host-1
difficulty: basic
timelimit: 600
enhanced_loading: null
---

# 📖 Challenge 2: Building Your First Workflow

Let's start with the "Hello, World!" of automation. We will build a simple workflow that takes a user's name as input and prints a greeting to the console.

## 1. Find the Workflow UI

In the [button label="Kibana"](tab-0) tab:

You should be in the **Workflows** UI. If you switched out of it:
   1. Go to the main menu (the "hamburger" icon).
   2. Navigate to **Management > Workflows**.
   3. This opens the Workflows UI (a new Tech Preview feature).

## 2. Create a New Workflow

1. Click **"Create a new workflow"**.
    ![CleanShot 2025-11-13 at 11.12.10@2x.png](../assets/CleanShot%202025-11-13%20at%2011.12.10%402x.png)
2. This will open the YAML editor. Delete all the boilerplate text.

## 3. Define the Inputs

```yaml
version: "1"
name: hello_world
enabled: true

inputs:
  - name: username
    type: string
    required: true
    description: "The name of the user to greet"
```

## 4. Define the Steps

```yaml
triggers:
  - type: manual

steps:
  - name: print_greeting
    type: console
    with:
      message: "Hello, {{ inputs.username }}!"
```

**Click "Next" to continue.**
```

---

## Setup Scripts

### Script Naming Convention

Setup scripts must be named to match VM hostnames from `config.yml`:
- VM `host-1` → script `setup-host-1`
- VM `kubernetes-vm` → script `setup-kubernetes-vm`

### Standard Script Structure

**1. Bootstrap Wait Pattern:**

```bash
#!/bin/bash

echo "Wait for the Instruqt host bootstrap to finish"
# Wait for the Instruqt host bootstrap to finish
while [ ! -f /opt/instruqt/bootstrap/host-bootstrap-completed ]
do
    echo "Waiting for Instruqt to finish booting the virtual machine"
    sleep 1
done

# explicitly source env vars
source /etc/profile.d/instruqt-env.sh
```

**2. Environment Variable Checks:**

```bash
####################################################################### ENV CHECK

export GCSKEY_CE_INFRA_CONTAINERS=$GCSKEY_CE_INFRA_CONTAINERS

if [[ -z "$GCSKEY_CE_INFRA_CONTAINERS" ]]; then
    echo "GCSKEY_CE_INFRA_CONTAINERS is null"
    exit 1
fi
```

**3. Workshop Assets Download:**

```bash
####################################################################### DOWNLOAD WORKSHOP ASSETS

echo "[Workshop] Downloading workshop assets..."
cd /opt
rm -rf workshop-assets

git clone --depth 1 --filter=blob:none --no-checkout \
  https://github.com/jeffvestal/instruqt-workshops.git temp-repo
cd temp-repo
git sparse-checkout set elastic/dr-rangelove-stove-store/workshop-assets
git checkout
mv elastic/dr-rangelove-stove-store/workshop-assets /opt/
cd /opt
rm -rf temp-repo

chmod +x /opt/workshop-assets/setup_scripts/*.sh
```

**4. Service Setup:**

```bash
####################################################################### INSTALL NODE.JS AND PM2

echo "[Workshop] Installing Node.js and pm2..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs
npm install -g pm2

####################################################################### SETUP MOCK API

echo "[Workshop] Setting up mock remediation API..."
bash /opt/workshop-assets/setup_scripts/03-mock-api-service.sh

# Configure pm2 to start on boot
pm2 startup systemd -u root --hp /root
pm2 save --force

echo "[Workshop] Mock API ready on port 3000"
```

**5. Kubernetes-Specific Setup:**

For Kubernetes VMs, additional patterns:

```bash
####################################################################### WAIT FOR K3S API

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

wait_for_api() {
  local timeout="$1"
  echo "[k3s] Waiting for API server readiness (timeout ${timeout}s)..."
  for i in $(seq 1 "$timeout"); do
    if kubectl get --raw='/readyz' >/dev/null 2>&1; then
      echo "[k3s] API server is responding"
      return 0
    fi
    sleep 1
  done
  return 1
}

if ! wait_for_api 300; then
  echo "[k3s] API not ready after first wait; restarting k3s once..."
  sudo systemctl restart k3s || true
  sleep 5
  if ! wait_for_api 180; then
    echo "[k3s] ERROR: API server not ready after restart"
    exit 1
  fi
fi

echo "[k3s] Waiting for nodes to become Ready..."
kubectl wait --for=condition=Ready node --all --timeout=300s
```

**6. Kibana Configuration:**

```bash
####################################################################### CONFIGURE KIBANA

echo "[Workshop] Configuring Kibana publicBaseUrl..."
kubectl patch kibana kibana -n default --type=merge -p '{
  "spec": {
    "config": {
      "server.publicBaseUrl": "http://kubernetes-vm:30001"
    }
  }
}' 2>/dev/null || echo "[Workshop] ⚠️  Could not patch Kibana config"

####################################################################### WAIT FOR KIBANA AND ENABLE WORKFLOWS FEATURE FLAG

echo "[Workshop] Waiting for Kibana to be ready..."
MAX_RETRIES=60
RETRY_COUNT=0

KIBANA_URL_UI="${KIBANA_URL_UI:-${KIBANA_URL:-http://localhost:30001}}"
ELASTICSEARCH_APIKEY="${ELASTICSEARCH_APIKEY:-${ELASTIC_API_KEY}}"

until curl -fsS -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" "${KIBANA_URL_UI}/api/status" >/dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "[Workshop] ERROR: Kibana did not become ready in time"
    exit 1
  fi
  echo "  ... waiting for Kibana (attempt ${RETRY_COUNT}/${MAX_RETRIES})"
  sleep 5
done

echo "[Workshop] ✓ Kibana is ready"

# Enable workflows feature flag and dark mode
echo "[Workshop] Enabling workflows feature flag and dark mode..."
FEATURE_FLAG_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${KIBANA_URL_UI}/api/kibana/settings" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -H "x-elastic-internal-origin: featureflag" \
  -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" \
  -d '{
    "changes": {
      "workflows:ui:enabled": true,
      "theme:darkMode": true
    }
  }')

HTTP_CODE=$(echo "$FEATURE_FLAG_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
  echo "[Workshop] ✓ Workflows feature flag and dark mode enabled (HTTP $HTTP_CODE)"
else
  echo "[Workshop] ⚠️  Warning: Feature flag API returned HTTP $HTTP_CODE"
fi
```

**7. API Calls with Retry Logic:**

```bash
# Helper function for Kibana API calls
kibana_post() {
  local endpoint="$1"
  local body="$2"
  curl -s -w "\n%{http_code}" -X POST "${KIBANA_URL_UI}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "kbn-xsrf: true" \
    -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" \
    -d "$body"
}

# Create connector with retry logic
CONNECTOR_ID=""
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "[Workshop] Attempting to create connector (attempt ${RETRY_COUNT}/${MAX_RETRIES})..."
  
  RESPONSE=$(kibana_post "/api/actions/connector" '{
    "name": "Elastic Proxy LLM",
    "config": {
      "apiProvider": "OpenAI",
      "apiUrl": "https://'"${LLM_PROXY_URL}"'/v1/chat/completions",
      "defaultModel": "gpt-4.1"
    },
    "secrets": {
      "apiKey": "'"${LLM_APIKEY}"'"
    },
    "connector_type_id": ".gen-ai"
  }')
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  BODY=$(echo "$RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    CONNECTOR_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$CONNECTOR_ID" ]; then
      echo "[Workshop] ✓ Connector created successfully (ID: ${CONNECTOR_ID})"
      break
    fi
  elif [ "$HTTP_CODE" = "409" ]; then
    echo "[Workshop] Connector already exists, discovering existing connector..."
    # Discovery logic here
    break
  else
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
      echo "[Workshop] Retrying in 2 seconds..."
      sleep 2
    else
      echo "[Workshop] ERROR: Failed after ${MAX_RETRIES} attempts"
      exit 1
    fi
  fi
done
```

**8. Completion Message:**

```bash
####################################################################### COMPLETE

echo "========================================="
echo "[Workshop] setup-host-1 complete"
echo "========================================="
echo "Services:"
echo "  - Mock API: http://host-1:3000"
echo "========================================="
```

### Script Best Practices

1. **Always wait for bootstrap**: Use the bootstrap wait pattern at the start
2. **Source environment variables**: Always source `/etc/profile.d/instruqt-env.sh`
3. **Check required variables**: Validate that required secrets/env vars are set
4. **Use retry logic**: For API calls and service readiness checks
5. **Provide clear logging**: Use `[Workshop]` prefix for workshop-specific messages
6. **Handle errors gracefully**: Check exit codes and provide helpful error messages
7. **Use section headers**: Use `#######################################################################` comments to separate sections
8. **Make scripts executable**: Ensure scripts have `chmod +x` or set in git

---

## Best Practices

### Track Organization

1. **Consistent Naming**: Use consistent challenge naming (`XX-slug-name`)
2. **Sequential Progression**: Challenges should build on each other logically
3. **Clear Dependencies**: Document what needs to be set up before challenges
4. **Solution Files**: Always include solution files in `assets/` for reference

### Challenge Design

1. **Clear Instructions**: Break down complex tasks into numbered steps
2. **Visual Aids**: Include screenshots showing expected UI state
3. **Code Examples**: Provide code snippets learners can copy/paste
4. **Progressive Disclosure**: Use collapsible sections for advanced/optional content
5. **Time Estimates**: Set realistic `timelimit` values based on complexity

### Setup Scripts

1. **Idempotency**: Scripts should be safe to run multiple times
2. **Error Handling**: Check for failures and exit with clear error messages
3. **Resource Cleanup**: Clean up temporary files and directories
4. **Logging**: Provide clear progress indicators
5. **Dependency Management**: Install dependencies before using them

### Configuration

1. **Resource Sizing**: Allocate appropriate CPU/memory for VMs based on workload
2. **Time Limits**: Set reasonable timeouts for track and individual challenges
3. **Theme Consistency**: Use consistent theme across track
4. **Secret Management**: Reference secrets by name, never hardcode values

### Testing

1. **Test Each Challenge**: Verify each challenge works end-to-end
2. **Test Setup Scripts**: Ensure setup scripts complete successfully
3. **Test Dependencies**: Verify challenges work in sequence
4. **Test Edge Cases**: Handle missing data, API failures, etc.

### Documentation

1. **README**: Include track-level README with overview and prerequisites
2. **Comments**: Comment complex setup script sections
3. **Solution Files**: Include well-commented solution files
4. **Troubleshooting**: Document common issues and solutions

---

## Common Patterns

### Pattern 1: Multi-VM Track

Track with separate VMs for different purposes:

```yaml
# config.yml
virtualmachines:
  - name: host-1              # Worker VM for services
    image: worker-image
    memory: 8192
    cpus: 4
  
  - name: kubernetes-vm       # Kubernetes cluster VM
    image: k8s-image
    memory: 16384
    cpus: 16
```

```bash
# track_scripts/setup-host-1
#!/bin/bash
# Setup worker services, APIs, etc.

# track_scripts/setup-kubernetes-vm
#!/bin/bash
# Setup Kubernetes, Kibana, Elasticsearch, etc.
```

### Pattern 2: Feature Flag Configuration

Enable Kibana feature flags via API:

```bash
curl -s -w "\n%{http_code}" -X POST "${KIBANA_URL}/api/kibana/settings" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -H "x-elastic-internal-origin: featureflag" \
  -H "Authorization: ApiKey ${ELASTICSEARCH_APIKEY}" \
  -d '{
    "changes": {
      "workflows:ui:enabled": true,
      "theme:darkMode": true
    }
  }'
```

### Pattern 3: Git Sparse Checkout

Download only specific directories from a large repo:

```bash
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TMP_DIR"
cd "$TMP_DIR"
git sparse-checkout set "path/to/subdirectory"
# Use files from subdirectory
```

### Pattern 4: Service Readiness Wait

Wait for a service to become ready:

```bash
MAX_RETRIES=60
RETRY_COUNT=0

until curl -fsS "${SERVICE_URL}/api/status" >/dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: Service did not become ready"
    exit 1
  fi
  echo "Waiting for service (attempt ${RETRY_COUNT}/${MAX_RETRIES})"
  sleep 5
done
```

### Pattern 5: Background Process Management

Start and manage background processes:

```bash
# Start background process
PYTHONUNBUFFERED=1 nohup python3 -u script.py > /var/log/script.log 2>&1 &
PROCESS_PID=$!

# Verify it started
sleep 1
if ps -p $PROCESS_PID > /dev/null 2>&1; then
    echo "✓ Process started (PID: ${PROCESS_PID})"
else
    echo "⚠️  Process failed to start"
    tail -20 /var/log/script.log
fi
```

---

## Troubleshooting

### Common Issues

**Issue: Setup script fails with "command not found"**
- Solution: Ensure dependencies are installed before use
- Check: Verify package installation commands succeeded

**Issue: Kibana feature flag not enabling**
- Solution: Use `x-elastic-internal-origin: featureflag` header
- Check: Verify Kibana is fully ready before making API calls

**Issue: Challenge tabs not loading**
- Solution: Verify VM hostnames match between `config.yml` and tab definitions
- Check: Ensure services are running on specified ports

**Issue: Secrets not available**
- Solution: Verify secret names match between `config.yml` and script usage
- Check: Secrets must be configured in Instruqt platform, not in code

**Issue: Git clone fails**
- Solution: Add retry logic for transient GitHub errors
- Check: Verify network connectivity and repository access

**Issue: Kubernetes API not ready**
- Solution: Implement wait loops with timeout and restart logic
- Check: Verify k3s service status and logs

---

## Additional Resources

- Instruqt Documentation: https://docs.instruqt.com
- YAML Reference: https://yaml.org/spec/
- Bash Best Practices: https://mywiki.wooledge.org/BashGuide

