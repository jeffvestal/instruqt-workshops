# YouTube Video Talking Points
## Elastic Workflows & AI Agent Workshop

---

# Challenge 1: The "Why" - From Findings to Outcomes
**Target Duration:** 3-5 minutes

## Section A: Verbal Script

### Intro (0:00-0:45)
"Welcome to the Elastic Workflows and AI Agent workshop! I'm excited to show you how Elastic is closing the gap between finding problems and fixing them. In this series, we're going to build real automation—from simple workflows all the way up to a complete self-healing system that combines AI agents with deterministic logic.

But first, we need to understand *why* this matters. Let's talk about what I call the 'Two-Vendor Problem.'"

### Key Points (0:45-2:30)

**The Problem:**
- "For years, Elastic has been exceptional at *finding* problems. Your security team detects a malicious IP. Your observability stack spots a latency spike. But then what?"
- "In most organizations, detection happens in one tool, and response happens in another. You pivot to PagerDuty, dig through runbooks, run some kubectl commands, maybe call an API. This context-switching wastes time and increases MTTR."
- "This is the Two-Vendor Problem: Great at findings, but you need a second vendor—or a bunch of custom scripts—to actually *do* something about it."

**The Solution:**
- "Elastic Workflows changes this by giving Elastic 'hands.' Native automation capabilities right inside the platform."
- "Detection and response in one place. Alerts trigger workflows. Workflows query Elasticsearch, call AI agents, hit external APIs, and index audit logs—all without leaving Elastic."

**What We'll Build:**
- "In this workshop, we're building two major systems: First, a self-healing workflow that automatically remediates service issues when alerts fire. Second, a business impact detector that monitors payment metrics, calculates revenue risk, and auto-scales your infrastructure."
- "We'll start simple—hello world workflows—and progress to production-ready patterns you can use in your own environment."

### Wrap-Up (2:30-3:00)
"By the end of this workshop, you'll understand workflow orchestration, AI agent chaining, ES|QL queries, alert triggers, and error handling patterns. Most importantly, you'll know how to turn your alerts into automated actions.

Alright, let's jump into the lab and start building!"

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:15** - Show workshop splash screen in Instruqt
- "Here's the workshop landing page. 9 challenges, 4 hours total."

**0:15-0:45** - Navigate to Challenge 1
- Click "Start" button
- Show challenge title and teaser
- Brief pan of tabs (Kibana, Terminal)

**0:45-2:30** - Present the Two-Vendor Problem
- Use whiteboard/slides or verbal explanation
- Optionally show diagram: Alert → Human → Tool 1 → Tool 2 → Fix (slow) vs. Alert → Workflow → Fix (fast)

**2:30-2:45** - Preview Kibana Workflows UI
- Switch to Kibana tab
- Click hamburger menu → Management → Workflows
- "This is where all the magic happens. Right now it's empty, but by Challenge 8, you'll have multiple production-ready workflows here."

**2:45-3:00** - Wrap up and transition
- "In the next video, we'll create our first workflow. See you there!"

---

# Challenge 2: Building Your First Workflow
**Target Duration:** 3-5 minutes

## Section A: Verbal Script

### Intro (0:00-0:30)
"Welcome back! In this challenge, we're building our first workflow. It's going to be simple—just a 'hello world'—but it teaches you the fundamental structure of every workflow: inputs, steps, and outputs.

Think of workflows like recipes. You have ingredients (inputs), instructions (steps), and a finished dish (outputs). Let's build one."

### Key Points (0:30-3:30)

**Workflow Anatomy:**
- "Every workflow is written in YAML. Don't worry if you're not a YAML expert—the patterns are straightforward."
- "At the top, you have metadata: name, description, whether it's enabled."
- "Then you define inputs. These are parameters users provide when they run the workflow manually."
- "Finally, you define steps. Steps are the actions: print a message, call an API, query Elasticsearch. Each step has a type and configuration."

**The Console Step:**
- "The simplest step type is 'console'—it just prints a message. Perfect for hello world."
- "You can reference inputs using Liquid templating: `{{ inputs.name }}`"
- "This is the same templating language used in Jekyll and Shopify—it's designed for inserting dynamic data into text."

**Running the Workflow:**
- "Once you create a workflow, you can run it manually from the Kibana UI. Click 'Run,' provide your inputs, and watch it execute."
- "The UI shows you each step's output in real-time. This is crucial for debugging."

### Wrap-Up (3:30-4:00)
"That's it for hello world! You just created your first workflow. In the next challenge, we'll chain multiple steps together and call external APIs. See you there!"

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:30** - Navigate to Challenge 2 in Instruqt
- Show challenge instructions
- Read the goal: "Build a workflow that accepts a name as input and prints a greeting"

**0:30-1:00** - Switch to Kibana → Workflows
- Click "Create Workflow" button
- Show blank YAML editor

**1:00-2:30** - Build the workflow (type or paste)
```yaml
version: "1"
name: hello_world
description: "My first workflow"
enabled: true

inputs:
  - name: user_name
    type: string
    description: "Your name"

steps:
  - name: greet_user
    type: console
    with:
      message: "Hello, {{ inputs.user_name }}! Welcome to Elastic Workflows."
```
- Explain each section as you type/paste
- "Version is always 1. Name is unique identifier. Inputs define what users provide."
- "Steps array contains our actions. This console step prints a message using the input."

**2:30-3:00** - Save and run the workflow
- Click "Save"
- Click "Run"
- Show input dialog, enter a name (e.g., "Jeff")
- Click "Execute"

**3:00-3:30** - Show execution results
- Highlight the "Executions" tab
- Show successful execution with green checkmark
- Expand the `greet_user` step
- Show the output: "Hello, Jeff! Welcome to Elastic Workflows."
- "See how it interpolated the input? That's Liquid templating in action."

**3:30-4:00** - Wrap up
- "You've created your first workflow. Next up: chaining steps and calling external APIs."

---

# Challenge 3: Chaining Steps
**Target Duration:** 6-8 minutes

## Section A: Verbal Script

### Intro (0:00-0:45)
"In the last challenge, we built a simple hello world workflow. Now we're leveling up: chaining multiple steps together and calling external APIs.

This is where workflows get powerful. You can take the output of one step—maybe an HTTP API call—and use that data in the next step. Let's build an IP geolocation workflow that demonstrates this pattern."

### Key Points (0:45-5:30)

**HTTP Steps:**
- "The `http` step type lets you call any REST API. You specify the URL, method, headers, and optionally a request body."
- "When the step completes, the response is stored in `steps.step_name.output`."
- "You can then reference that output in subsequent steps using Liquid templating."

**Output Chaining:**
- "Let's say step 1 calls an API and gets back JSON. You access fields like this: `{{ steps.step1.output.data.field_name }}`"
- "Kibana parses the JSON response automatically, so you don't have to do any manual parsing."
- "This pattern—query data, extract fields, pass to next step—is fundamental to workflow orchestration."

**Real-World Example:**
- "We're building an IP geolocation workflow. Step 1 calls an API to get your public IP. Step 2 uses that IP to call a geolocation API. Step 3 prints your location."
- "Three steps, two external APIs, fully automated."

**Data Transformation:**
- "You can do simple transformations with Liquid filters: `{{ value | upcase }}`, `{{ number | plus: 10 }}`"
- "For complex transformations, you might call an AI agent (we'll see this in Challenge 5) or use a more sophisticated step type."

### Wrap-Up (5:30-6:00)
"That's step chaining! You now know how to call external APIs and pass data between steps. In the next challenge, we'll make this more robust with error handling and retry logic."

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:30** - Show Challenge 3 instructions
- "Build a workflow that chains two API calls: get public IP, then geolocate it."

**0:30-1:00** - Navigate to Workflows UI
- Click "Create Workflow"

**1:00-3:30** - Build the workflow
```yaml
version: "1"
name: ip_geolocator
description: "Get public IP and geolocate it"
enabled: true

inputs: []

steps:
  - name: get_public_ip
    type: http
    with:
      url: "https://api.ipify.org?format=json"
      method: GET

  - name: geolocate_ip
    type: http
    with:
      url: "http://ip-api.com/json/{{ steps.get_public_ip.output.data.ip }}"
      method: GET

  - name: display_location
    type: console
    with:
      message: |
        Your IP: {{ steps.get_public_ip.output.data.ip }}
        Location: {{ steps.geolocate_ip.output.data.city }}, {{ steps.geolocate_ip.output.data.regionName }}
        Country: {{ steps.geolocate_ip.output.data.country }}
```
- Explain as you go:
  - "First step gets public IP from ipify API"
  - "Second step uses that IP in the URL—see the Liquid template?"
  - "Third step prints the location from the second API's response"

**3:30-4:30** - Save and run
- Click "Save"
- Click "Run" (no inputs needed)
- Show execution in progress

**4:30-5:30** - Review execution results
- Expand `get_public_ip` step
  - Show output: `{"ip": "203.0.113.42"}`
- Expand `geolocate_ip` step
  - Show output with city, region, country fields
- Expand `display_location` step
  - Show final formatted message
- "Notice how each step builds on the previous one. That's the power of chaining."

**5:30-6:00** - Wrap up
- "Next challenge: What happens when an API fails? We'll add error handling."

---

# Challenge 4: Making it Robust
**Target Duration:** 6-8 minutes

## Section A: Verbal Script

### Intro (0:00-0:45)
"Alright, we've built workflows that chain HTTP calls. But what happens when an API is down? Or returns an error? Right now, the workflow just fails. Not great.

In this challenge, we're adding error handling and retry logic. This is essential for production workflows—you need to gracefully handle failures."

### Key Points (0:45-5:30)

**The `on-failure` Block:**
- "Every step can have an `on-failure` section. This tells the workflow what to do if the step fails."
- "You have two options: retry (try again after a delay) or fallback (execute alternative steps)."
- "Retries are perfect for transient failures—network blips, rate limits, temporary API downtime."

**Retry Logic:**
```yaml
on-failure:
  retry:
    max-attempts: 3
    delay: 2s
```
- "This will retry up to 3 times, waiting 2 seconds between attempts."
- "The delay can be static (2s) or you can implement exponential backoff with some creative Liquid templating."

**Fallback Steps:**
- "If you don't want to retry, you can run fallback steps instead. Maybe you log the error, send a notification, or use cached data."
```yaml
on-failure:
  fallback:
    - name: log_error
      type: console
      with:
        message: "API call failed: {{ steps.api_call.error }}"
```

**Conditional Logic:**
- "You can also use `if` steps to branch based on conditions. Check if a value is above a threshold, if an API returned a certain status code, etc."
- "The condition is written as a Liquid expression that evaluates to true or false."

### Wrap-Up (5:30-6:00)
"Now your workflows can handle failures gracefully. Retry transient errors, fall back when needed, and branch based on conditions. This is production-ready error handling. In the next challenge, we're introducing AI agents!"

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:30** - Show Challenge 4 instructions
- "Add retry logic and conditional branching to the IP geolocator workflow."

**0:30-1:00** - Open existing `ip_geolocator` workflow
- Click on the workflow from Challenge 3
- "We're going to enhance this with error handling."

**1:00-3:30** - Add retry logic to HTTP steps
```yaml
  - name: get_public_ip
    type: http
    with:
      url: "https://api.ipify.org?format=json"
      method: GET
    on-failure:
      retry:
        max-attempts: 3
        delay: 2s

  - name: geolocate_ip
    type: http
    with:
      url: "http://ip-api.com/json/{{ steps.get_public_ip.output.data.ip }}"
      method: GET
    on-failure:
      retry:
        max-attempts: 3
        delay: 2s
      fallback:
        - name: log_geo_error
          type: console
          with:
            message: "Geolocation API failed after 3 retries. Error: {{ steps.geolocate_ip.error }}"
```
- "Each HTTP step now retries 3 times. The second step also has a fallback—if all retries fail, we log the error instead of crashing."

**3:30-4:30** - Add conditional logic
```yaml
  - name: check_country
    type: if
    condition: "{{ steps.geolocate_ip.output.data.country == 'United States' }}"
    steps:
      - name: domestic_message
        type: console
        with:
          message: "Domestic location detected: {{ steps.geolocate_ip.output.data.city }}"
    else:
      - name: international_message
        type: console
        with:
          message: "International location: {{ steps.geolocate_ip.output.data.country }}"
```
- "This `if` step checks the country. Different messages for US vs. international."

**4:30-5:00** - Save and test
- Click "Save"
- Click "Run"

**5:00-5:30** - Show execution with conditional branch
- Expand steps to show which branch executed
- "See? The workflow took the domestic path because my IP is in the US."

**5:30-6:00** - Wrap up
- "You now have production-grade error handling. Next: AI agents!"

---

# Challenge 5: The AI "Assembly Line"
**Target Duration:** 8-10 minutes

## Section A: Verbal Script

### Intro (0:00-1:00)
"Alright, things are about to get interesting. We're introducing AI agents.

Elastic's Agent Builder lets you create AI agents with specific personas and instructions. You can call these agents from workflows using the `kibana.post_agent_builder_converse` step.

But here's where it gets powerful: you can *chain* multiple AI agents together in what I call an 'assembly line' pattern. Agent 1 generates content. Agent 2 critiques it. Agent 3 remediates it. Let's build this."

### Key Points (1:00-7:00)

**Agent Builder Basics:**
- "During lab setup, we pre-created 4 AI agents for you. Let's look at them in Kibana."
- "Each agent has a persona, instructions, and optionally tools. For this challenge, we're using 3 agents: a content creator, a sentiment analyzer, and a PR spin specialist."

**The Assembly Line Pattern:**
- "Here's the flow: Agent 1 writes a negative press release. Agent 2 analyzes the sentiment and returns JSON. Agent 3 reads that analysis and rewrites the content with positive spin."
- "This demonstrates chaining—each agent's output feeds the next agent's input."
- "This pattern is useful for complex reasoning tasks: Generate → Critique → Refine → Approve."

**Calling Agents from Workflows:**
```yaml
- name: call_agent
  type: kibana.post_agent_builder_converse
  with:
    agent_id: agent_content_creator
    input: "Write a press release about a data breach."
```
- "Super simple. Specify the agent ID and provide an input message."
- "The agent's response is in `steps.call_agent.output.response.message`."

**Chaining Agents:**
- "To chain, just reference the previous agent's output in the next agent's input."
- "Example: `input: 'Analyze this content: {{ steps.generate.output.response.message }}'`"

### Wrap-Up (7:00-8:00)
"That's multi-agent orchestration! You can chain as many agents as you want. Generate, critique, remediate, summarize—whatever your use case needs. In the next challenge, we'll flip this: instead of calling agents from workflows, we'll give agents workflows as tools."

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:45** - Show Challenge 5 instructions
- "Build a 3-agent assembly line: generator → critic → remediator."

**0:45-1:30** - Show pre-created agents in Kibana
- Navigate to Agent Builder (if available in UI) or explain verbally
- "We have agent_content_creator, agent_sentiment_analyzer, and agent_pr_spin_specialist."
- Briefly describe each persona

**1:30-4:30** - Build the workflow
```yaml
version: "1"
name: ai_content_chain
description: "Multi-agent content generation and remediation"
enabled: true

inputs:
  - name: topic
    type: string
    description: "Press release topic"

steps:
  - name: generate_content
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_content_creator
      input: "Write a concise, negative press release about: {{ inputs.topic }}"

  - name: analyze_sentiment
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_sentiment_analyzer
      input: |
        Analyze this content and return JSON:
        {{ steps.generate_content.output.response.message }}

  - name: remediate_content
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_pr_spin_specialist
      input: |
        The sentiment analysis shows: {{ steps.analyze_sentiment.output.response.message }}
        Original content: {{ steps.generate_content.output.response.message }}
        Rewrite this with positive spin.

  - name: display_results
    type: console
    with:
      message: |
        === ORIGINAL ===
        {{ steps.generate_content.output.response.message }}
        
        === SENTIMENT ===
        {{ steps.analyze_sentiment.output.response.message }}
        
        === REMEDIATED ===
        {{ steps.remediate_content.output.response.message }}
```
- Walk through each step:
  - "First agent generates negative content"
  - "Second agent analyzes sentiment, returns JSON"
  - "Third agent uses both previous outputs to create positive spin"
  - "Final console step displays everything"

**4:30-5:00** - Save and run
- Click "Save"
- Click "Run"
- Provide topic: "our payment service had an outage"
- Click "Execute"

**5:00-7:00** - Show execution results
- "This will take 30-60 seconds—AI agents need time to think."
- Expand each step:
  - `generate_content`: "Our payment service failed catastrophically..."
  - `analyze_sentiment`: `{"sentiment": "NEGATIVE", "score": -0.8, ...}`
  - `remediate_content`: "We proactively identified an opportunity to enhance our payment service resilience..."
- "See the transformation? Negative → JSON analysis → Positive spin."

**7:00-8:00** - Wrap up
- "This is multi-agent orchestration. You can build arbitrarily complex reasoning chains. Next challenge: giving agents workflows as tools!"

---

# Challenge 6: The "Full Circle" - AI Agent Tools
**Target Duration:** 8-10 minutes

## Section A: Verbal Script

### Intro (0:00-1:00)
"In the last challenge, we called AI agents from workflows. Now we're doing the opposite: we're giving an AI agent a workflow as a tool.

Think about this for a second. You have an SRE triage bot—an AI agent that helps engineers investigate incidents. What if that bot could run Elasticsearch queries on demand? Not just static queries, but dynamic queries based on the conversation.

That's exactly what we're building. An AI agent with a workflow tool. Let's do it."

### Key Points (1:00-7:00)

**The Concept:**
- "Normally, AI agents are limited to text generation. They can't query databases or call APIs on their own."
- "But Agent Builder supports 'tools'—external capabilities you can give to agents. Workflows are tools."
- "When you give an agent a workflow, it can call that workflow whenever it needs the information. The agent decides when to use the tool based on the conversation."

**Building the Workflow Tool:**
- "We're building a simple observability query workflow. It accepts a service name and queries Elasticsearch for recent errors."
- "This workflow will be registered as a tool with our SRE triage bot."

**Configuring the Agent:**
- "In Agent Builder, you specify: Here's a workflow called `triage_service_incident`. You can call it when users ask about service health."
- "The agent will automatically call the workflow, wait for results, and incorporate those results into its response."

**The Conversation:**
- "Once configured, you chat with the agent: 'How is payment-service doing?' The agent calls your workflow, gets real Elasticsearch data, and responds with actual metrics."
- "This is a game-changer for observability. Your AI assistant isn't hallucinating—it's querying real data."

### Wrap-Up (7:00-8:00)
"That's the full circle. Workflows call agents. Agents call workflows. You can build incredibly sophisticated systems with this pattern. Next up: we're connecting workflows to real alerts!"

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:45** - Show Challenge 6 instructions
- "Build a workflow that queries Elasticsearch, then give it to an AI agent as a tool."

**0:45-3:00** - Build the observability query workflow
```yaml
version: "1"
name: triage_service_incident
description: "Query recent errors for a service"
enabled: true

inputs:
  - name: service_name
    type: string
    description: "Service to investigate"

steps:
  - name: query_errors
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      body:
        size: 10
        sort: [{"@timestamp": "desc"}]
        query:
          bool:
            must:
              - term:
                  service.name: "{{ inputs.service_name }}"
              - range:
                  http.status_code:
                    gte: 500
              - range:
                  "@timestamp":
                    gte: "now-15m"

  - name: return_summary
    type: console
    with:
      message: |
        Found {{ steps.query_errors.output.hits.total.value }} errors for {{ inputs.service_name }} in the last 15 minutes.
        Sample error: {{ steps.query_errors.output.hits.hits[0]._source.log.message }}
```
- "This workflow queries for 5xx errors in the last 15 minutes and returns a summary."

**3:00-3:30** - Save and test the workflow manually
- Click "Save"
- Click "Run"
- Input: "payment-service"
- Show results: "Found 12 errors..."

**3:30-5:00** - Configure the SRE triage bot agent
- Navigate to Agent Builder (or explain via API call)
- "We need to tell the sre_triage_bot agent about this workflow."
- Show agent configuration (or describe):
  - Agent ID: `sre_triage_bot`
  - Tools: Add workflow `triage_service_incident`
  - Instructions: "You can query service health using the triage_service_incident workflow. Call it when users ask about service errors."

**5:00-6:30** - Test the agent conversation
- Open Agent Builder chat interface
- Type: "How is payment-service doing?"
- Show agent response:
  - "[Agent is calling workflow triage_service_incident...]"
  - Agent response: "I queried the last 15 minutes of data. Payment-service has 12 errors, primarily timeouts. The most recent error was 'Upstream gateway connection timeout after 5000ms'."
- "See that? The agent called our workflow automatically, got real data, and summarized it."

**6:30-7:00** - Try another query
- Type: "What about trade-service?"
- Show agent calling workflow again with different input
- Agent responds with trade-service metrics

**7:00-8:00** - Wrap up
- "This is the power of workflows as tools. Your AI agents can now query live data instead of hallucinating. Next challenge: alert-triggered workflows!"

---

# Challenge 7: Self-Healing AI
**Target Duration:** 8-10 minutes

## Section A: Verbal Script

### Intro (0:00-1:00)
"We're at the penultimate challenge, and this is where everything comes together. We're building a self-healing workflow that's triggered by a real alert.

Here's the scenario: Your ML anomaly detection spots a latency spike on payment-service. An alert fires. That alert automatically triggers a workflow. The workflow queries Elasticsearch for context, calls an AI agent to analyze root cause, and hits a remediation API—all without human intervention.

This is production-ready AIOps. Let's build it."

### Key Points (1:00-7:00)

**Alert Triggers:**
```yaml
triggers:
  - type: alert
```
- "When you set a trigger type to `alert`, the workflow can be configured as an alert action in Kibana."
- "Whenever the alert fires, the workflow runs automatically."

**Accessing Alert Data:**
- "The alert passes data to the workflow in the `event` object."
- "You can access alert metadata: `{{ event.alerts[0].rule.name }}`, `{{ event.alerts[0].id }}`"
- "Some alerts include context fields—depends on the alert type."

**The Self-Healing Flow:**
1. Alert fires: "payment-service latency > 800ms"
2. Workflow triggered automatically
3. Step 1: Query Elasticsearch for recent logs/metrics
4. Step 2: Send that data to an AI agent: "What's the likely root cause?"
5. Step 3: Call remediation API (e.g., restart service, scale pods)
6. Step 4: Index audit log to Elasticsearch

**Remediation APIs:**
- "In this lab, we're calling a mock API that simulates restarting a service."
- "In production, you'd call real APIs: Kubernetes to restart pods, AWS to scale instances, PagerDuty to update incidents."

### Wrap-Up (7:00-8:00)
"That's self-healing! When an alert fires, the workflow handles the first 5 minutes of investigation and remediation. Your team can sleep through minor incidents because the automation handles it. Next challenge is the capstone: we're building a business impact detector!"

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:45** - Show Challenge 7 instructions
- "Build a workflow triggered by the payment-service latency alert, query Elasticsearch, use AI for analysis, and call the remediation API."

**0:45-4:00** - Build the self-healing workflow
```yaml
version: "1"
name: self_healing_aiops
description: "Auto-remediate service latency issues"
enabled: true

inputs: []

triggers:
  - type: alert

steps:
  - name: query_recent_errors
    type: elasticsearch.search
    with:
      index: "o11y-heartbeat"
      body:
        size: 20
        sort: [{"@timestamp": "desc"}]
        query:
          bool:
            must:
              - term:
                  service.name: "payment-service"
              - range:
                  "@timestamp":
                    gte: "now-10m"

  - name: ai_root_cause_analysis
    type: kibana.post_agent_builder_converse
    with:
      agent_id: sre_triage_bot
      input: |
        Alert fired: {{ event.alerts[0].rule.name }}
        Recent errors: {{ steps.query_recent_errors.output.hits.hits | json }}
        What's the likely root cause and recommended action?

  - name: remediate_service
    type: http
    with:
      url: "http://host-1:3000/remediate_service"
      method: POST
      headers:
        Content-Type: application/json
      body:
        service_name: "payment-service"
        action: "restart"
    on-failure:
      retry:
        max-attempts: 2
        delay: 1s

  - name: log_to_elasticsearch
    type: elasticsearch.index
    with:
      index: "workflow_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}"
      document:
        timestamp: "{{ execution.startedAt }}"
        workflow: "self_healing_aiops"
        alert_id: "{{ event.alerts[0].id }}"
        alert_name: "{{ event.alerts[0].rule.name }}"
        ai_analysis: "{{ steps.ai_root_cause_analysis.output.response.message }}"
        remediation_result: "{{ steps.remediate_service.output.data.message }}"
```
- Walk through each step as you build

**4:00-5:00** - Save the workflow
- Click "Save"
- "Don't run it manually—we need to configure the alert action first."

**5:00-6:00** - Configure the alert action
- Navigate to Observability → Alerts → Rules
- Find "payment-service-latency-spike" alert
- Click "Edit"
- Scroll to "Actions" section
- Add action → Workflows
- Select `self_healing_aiops` workflow
- Save

**6:00-7:00** - Trigger an incident
- Switch to Terminal tab
- Run: `bash /opt/workshop-assets/setup_scripts/04-force-incident.sh`
- "This injects 10 high-latency documents to trigger the alert."

**7:00-7:30** - Wait for alert to fire
- Navigate to Observability → Alerts
- "Within 1-2 minutes, the alert should fire."
- Show alert status changing to "Active"

**7:30-8:30** - View workflow execution
- Navigate to Management → Workflows → self_healing_aiops
- Click "Executions" tab
- Show the automatic execution (green checkmark)
- Expand steps:
  - `query_recent_errors`: Shows 20 error documents
  - `ai_root_cause_analysis`: AI says "Likely upstream latency, recommend restart"
  - `remediate_service`: Mock API returns "Service restarted: 2 → 4 instances"
  - `log_to_elasticsearch`: Audit log written

**8:30-9:00** - Check mock API logs
- Switch to Terminal
- Run: `pm2 logs mock-api --lines 10`
- Show the POST request to /remediate_service
- "There's the API call. In production, this would actually restart your service."

**9:00-10:00** - Wrap up
- "That's self-healing! The alert fired, the workflow ran, the service was remediated—all automatically. In the next challenge, we're building an even more sophisticated system: a business impact detector."

---

# Challenge 8: Capstone - Business Impact Detection
**Target Duration:** 12-15 minutes

## Section A: Verbal Script

### Intro (0:00-1:30)
"Welcome to the capstone challenge. This is where we pull out all the stops and build something truly production-ready.

Here's the problem: Traditional observability treats all alerts equally. Latency is high? Fire an alert. Error rate spikes? Fire an alert. But not all incidents are created equal.

What if your error rate spikes by 10%, but it's only affecting a low-traffic endpoint? That's a problem, but it's not urgent. Now imagine your payment service error rate spikes by 10%, AND your successful payment transactions drop by 40%. That's not just a technical problem—that's a *business* problem. You're losing revenue in real-time.

This is business impact detection. We're building a workflow that:
1. Uses ES|QL to efficiently query multiple metrics in a single query
2. Calculates business impact using deterministic logic (no AI guessing)
3. Uses AI to explain the impact to stakeholders in plain English
4. Automatically scales your infrastructure if revenue is at risk

Let's build it."

### Key Points (1:30-10:00)

**ES|QL Multi-Metric Queries:**
- "Traditional Elasticsearch queries require separate requests for each metric. Want error count, current payment volume, AND baseline payment volume? That's 3 queries."
- "ES|QL lets you get all of that in ONE query using EVAL and STATS."
- "This is faster, more efficient, and easier to maintain in workflows."

**The Query:**
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
- "This returns 4 metrics: errors, current payments, current revenue, baseline payments."
- "All in one query. Beautiful."

**Accessing ES|QL Results:**
- "ES|QL returns data as an array of arrays."
- "First row, first column: `{{ steps.get_all_metrics.output.values[0][0] }}` is error_count."
- "First row, second column: `{{ steps.get_all_metrics.output.values[0][1] }}` is current_payment_count."

**Deterministic Scaling Logic:**
- "We calculate the payment drop percentage using simple math in Liquid templates."
- "If drop >= 30%, we scale. Otherwise, we log and alert but don't scale."
- "This is deterministic—no AI involved in the decision. Reliability is critical here."

**AI for Explanation:**
- "After we make the decision, we call an AI agent to explain the business impact."
- "The agent gets all the metrics and writes a 2-3 sentence summary for stakeholders: 'Revenue is at risk due to payment failures. Recommend immediate investigation.'"
- "AI isn't making the decision—it's explaining it in human language."

**The Complete Flow:**
1. Alert fires: payment-service 5xx errors detected
2. Workflow queries all metrics with ES|QL
3. Workflow calculates payment drop percentage
4. If drop >= 30%:
   - Call AI agent for business summary
   - POST to scaling API
   - Log action to Elasticsearch
5. If drop < 30%:
   - Log the incident but don't scale

### Wrap-Up (10:00-12:00)
"This is a production-ready business impact detector. It's fast (ES|QL), reliable (deterministic logic), explainable (AI summaries), and auditable (indexed logs).

You can adapt this pattern to any business-critical metric: checkout conversion, order fulfillment rate, API billing, whatever matters to your business.

The key lesson: Use deterministic logic for decisions. Use AI for explanations. Never let AI make critical decisions in prod—but absolutely use it to make those decisions understandable to humans."

---

## Section C: Full Demo Flow with Timestamps

**0:00-1:00** - Show Challenge 8 instructions
- "Build a business impact detector from scratch using ES|QL, deterministic logic, and AI."
- "This is the capstone—everything you've learned comes together here."

**1:00-1:30** - Navigate to Workflows UI
- Click "Create Workflow"

**1:30-7:00** - Build the complete workflow
```yaml
version: "1"
name: business_impact_detector
description: "Detect and respond to business-critical payment service degradation"
enabled: true

inputs: []

triggers:
  - type: alert

steps:
  - name: get_all_metrics
    type: elasticsearch.esql.query
    with:
      query: >
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

  - name: ai_business_summary
    type: kibana.post_agent_builder_converse
    with:
      agent_id: agent_business_slo
      input: |
        Here are the current metrics for payment-service:
        - Error count (last 5m): {{ steps.get_all_metrics.output.values[0][0] }}
        - Current successful payments (last 5m): {{ steps.get_all_metrics.output.values[0][1] }}
        - Baseline successful payments (previous 60m total): {{ steps.get_all_metrics.output.values[0][3] }}
        
        For context: The baseline covers 60 minutes, so to compare to the 5-minute current window,
        the normalized baseline rate would be approximately {{ steps.get_all_metrics.output.values[0][3] | divided_by: 12 | round }} payments per 5 minutes.
        
        Calculate the percentage drop: if current is significantly below the normalized baseline (drop >= 30%),
        this indicates a business-critical issue affecting revenue.
        
        Your job is to explain the business impact in 2–3 sentences for an SRE and business audience.

  - name: notify_stakeholder
    type: console
    with:
      message: |
        [EMAIL] To: sre-team@example.com
        Subject: Payment service impact detected
        {{ steps.ai_business_summary.output.response.message }}

  - name: check_scaling_needed
    type: if
    condition: |
      {% assign current = steps.get_all_metrics.output.values[0][1] | plus: 0 %}
      {% assign baseline_total = steps.get_all_metrics.output.values[0][3] | plus: 0 %}
      {% assign normalized_baseline = baseline_total | divided_by: 12.0 %}
      {% assign drop_pct = normalized_baseline | minus: current | times: 100.0 | divided_by: normalized_baseline %}
      {% if drop_pct >= 30 %}true{% else %}false{% endif %}
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
            {{ steps.scale_service.output.data.message }}
    else:
      - name: log_no_scaling
        type: console
        with:
          message: "⚠️ No scaling action needed. Manual investigation may be required."

  - name: log_to_elasticsearch
    type: elasticsearch.index
    with:
      index: "business_actions-{{ execution.startedAt | date: '%Y-%m-%d' }}"
      id: "{{ execution.id }}"
      document:
        timestamp: "{{ execution.startedAt }}"
        workflow_name: "business_impact_detector"
        alert_id: "{{ event.alerts[0].id }}"
        service_name: "payment-service"
        error_count: "{{ steps.get_all_metrics.output.values[0][0] }}"
        current_payment_count: "{{ steps.get_all_metrics.output.values[0][1] }}"
        baseline_payment_count: "{{ steps.get_all_metrics.output.values[0][3] }}"
        ai_explanation: "{{ steps.ai_business_summary.output.response.message }}"
```
- Walk through each section:
  - **ES|QL query:** "One query for all metrics"
  - **AI summary:** "Explain business impact in plain English"
  - **Notification:** "Alert stakeholders"
  - **Conditional scaling:** "Deterministic decision based on 30% threshold"
  - **Audit log:** "Index everything for compliance"

**7:00-7:30** - Save the workflow
- Click "Save"

**7:30-8:30** - Configure alert action
- Navigate to Observability → Alerts
- Find "business-impact-payment-degradation" alert
- Edit → Actions → Add Workflows action
- Select `business_impact_detector`
- Save

**8:30-9:00** - Trigger business incident
- Switch to Terminal
- Run: `bash /opt/workshop-assets/setup_scripts/06-trigger-business-incident.sh`
- "This simulates a business incident: payment transactions will drop by 60%, amounts by 50%, for 5 minutes."

**9:00-10:00** - Wait for alert to fire
- Navigate to Observability → Alerts
- "Within 1-2 minutes, the business alert should fire."
- Show alert status: Active

**10:00-12:00** - View workflow execution
- Navigate to Workflows → business_impact_detector → Executions
- Show automatic execution
- Expand steps:
  - `get_all_metrics`: Show the 4 values (errors, current, amount, baseline)
  - `ai_business_summary`: AI says "Payment processing is experiencing significant degradation. Current successful payment rate is 60% below baseline, indicating potential revenue loss of approximately $X per hour. Recommend immediate investigation of payment gateway connectivity and consider scaling infrastructure."
  - `check_scaling_needed`: Condition evaluated to TRUE (drop > 30%)
  - `scale_service`: Mock API returns "Scaled from 2 to 4 instances"
  - `log_to_elasticsearch`: Document indexed

**12:00-13:00** - Query audit logs
- Switch to Kibana → Dev Tools
- Run:
```json
GET business_actions-*/_search
{
  "size": 1,
  "sort": [{"timestamp": "desc"}]
}
```
- Show the indexed document with all metrics and AI explanation
- "Full audit trail. You can track every automated decision."

**13:00-14:00** - Check mock API logs
- Terminal: `pm2 logs mock-api --lines 20`
- Show POST to /scale_service
- "In production, this would scale your Kubernetes deployment or EC2 Auto Scaling Group."

**14:00-15:00** - Wrap up
- "That's the capstone! You built a production-ready business impact detector."
- "Key takeaways:"
  - "ES|QL for efficiency"
  - "Deterministic logic for reliability"
  - "AI for explainability"
  - "Audit logs for compliance"
- "You can adapt this to any business-critical metric: checkout conversion, API billing, order fulfillment, whatever matters to your revenue."
- "Final challenge: summary and next steps!"

---

# Challenge 9: Workshop Summary
**Target Duration:** 3-5 minutes

## Section A: Verbal Script

### Intro (0:00-0:30)
"Congratulations! You've completed the Elastic Workflows and AI Agent workshop. Let's recap what you've learned and talk about next steps."

### Key Points (0:30-3:30)

**What You Built:**
- "You started with a simple hello world workflow. By the end, you built two complete production-ready systems:"
  - "A self-healing observability workflow triggered by ML anomaly alerts"
  - "A business impact detector that monitors revenue metrics and auto-scales infrastructure"
- "These aren't toy examples. These are real patterns you can deploy in your environment today."

**Patterns You Learned:**
1. **Workflow Orchestration:** Chaining steps, passing data, transforming outputs
2. **Error Handling:** Retry logic, fallback steps, conditional branching
3. **AI Orchestration:** Multi-agent assembly lines, agents with workflow tools
4. **Alert Integration:** Triggering workflows from observability alerts
5. **ES|QL Queries:** Efficient multi-metric data retrieval
6. **Hybrid Logic:** Deterministic decisions + AI explanations

**Production Considerations:**
- "When you deploy workflows in production, remember:"
  - "Security: Use restrictive API keys, store secrets properly"
  - "Monitoring: Track workflow execution metrics and failure rates"
  - "Audit Logging: Always index workflow actions for compliance"
  - "Rate Limiting: Be careful with external API calls"
  - "Testing: Test workflows in staging before production"

**Next Steps:**
- "Here's what you should do next:"
  1. "Identify 3-5 high-toil runbooks in your environment—manual processes your team repeats constantly."
  2. "Translate those runbooks into workflows. Start simple (notifications, queries) and progressively add automation (API calls, scaling)."
  3. "Build a workflow library for your organization—reusable patterns for common tasks."
  4. "Explore advanced topics: ML-based anomaly detection, multi-region coordination, approval workflows with Slack."
  5. "Share your workflows with the Elastic community!"

### Wrap-Up (3:30-4:00)
"Thank you for taking this workshop! You now have the skills to close the gap between findings and outcomes. Go build amazing automation. And if you create something cool, share it with the community—we'd love to see it. Happy automating!"

---

## Section C: Full Demo Flow with Timestamps

**0:00-0:30** - Show Challenge 9 in Instruqt
- "Final challenge: summary and next steps."
- Read through the summary content briefly

**0:30-1:30** - Review completed workflows in Kibana
- Navigate to Management → Workflows
- Show the list of workflows created:
  - hello_world
  - ip_geolocator
  - ai_content_chain
  - triage_service_incident
  - self_healing_aiops
  - business_impact_detector
- "Look at what you've built in 4 hours. Impressive!"

**1:30-2:30** - Review execution history
- Click on `business_impact_detector`
- Show "Executions" tab with successful runs
- "Every workflow tracks its execution history. Full observability of your automation."

**2:30-3:00** - Review audit logs one more time
- Dev Tools:
```json
GET business_actions-*/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```
- "All automated actions logged to Elasticsearch. Auditable, queryable, dashboardable."

**3:00-3:30** - Show documentation links
- "Resources to continue learning:"
  - Elastic Workflows documentation
  - Agent Builder API reference
  - ES|QL reference
  - GitHub repo with workshop content

**3:30-4:00** - Final message
- "Thank you for completing this workshop!"
- "Key takeaway: From findings to outcomes. Elastic now has the 'hands' to take action."
- "Go automate your runbooks, eliminate toil, and build self-healing systems."
- "Share your work with the community. We'd love to see what you build."
- "Happy automating!"

---

## End of Video Series

**Production Notes:**
- Maintain consistent pacing throughout series (not too slow, not too fast)
- Show real execution time for AI agents (30-60 seconds)—don't cut it entirely, but can time-lapse with "Waiting for AI..." overlay
- Use cursor highlighting or zoom for small UI elements
- Keep terminal text large enough to read at 1080p
- Add chapter markers in YouTube for each major section
- Include links in description to:
  - Workshop URL
  - GitHub repo
  - Official documentation
  - Community forum
- Consider adding end cards with "Next video" links

