---
slug: 04-robust-workflows
id: 99z4kizklpcy
type: challenge
title: 'Making it Robust: Logic & Error Handling'
teaser: Add retry logic and conditional branching to workflows
tabs:
- id: zfzdafxse1cd
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: xtx0jr9h5wu2
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: intermediate
timelimit: 900
enhanced_loading: null
---

# 📖 Challenge 4: Making it Robust - Logic & Error Handling

Real-world automation must handle errors and make decisions. Let's add `on-failure` retries and `{% if %}` logic to our IP workflow.

## 1. Open Your `ip_geolocator` Workflow

1. Go back to the `ip_geolocator` workflow you just built.
2. We will modify it.

## 2. Add Error Handling

What if the API call fails? Let's add an `on-failure` block to the `http` step.

Modify your `get_geolocation` step to look like this:

```yaml
  - name: get_geolocation
    type: http
    with:
      url: "{{ consts.ip_api_base_url }}/{{ inputs.ip_address }}"
      method: GET
    on-failure: # <-- ADD THIS BLOCK
      retry:
        max-attempts: 2
        delay: 1s
```

This tells the workflow to "try this step 2 times, waiting 1 second between failures" before giving up.

## 3. Add Conditional Logic

What if we want to do different things based on the *result*? Let's change our `console` message to use Jinja `if` logic.

Replace your *entire* `print_location` step with this:

```yaml
  - name: print_location
    type: console
    with:
      message: >- # <-- Use >- to avoid extra newlines
        {% if steps.get_geolocation.output.data.status == "success" %}
          {% if steps.get_geolocation.output.data.countryCode == "US" %}
          🇺🇸 This is a United States-based IP from {{ steps.get_geolocation.output.data.city }}.
          {% else %}
          🌍 This is an international IP from {{ steps.get_geolocation.output.data.country }}.
          {% endif %}
        {% else %}
        This IP could not be geolocated (private or unknown range).
        {% endif %}
```

This logic block checks the `countryCode` from the API response and changes the message.

## 4. Test All Scenarios

1. **Save** your workflow.
2. **Test 1 (The "US" path):**
   * **Run** with `ip_address`: `8.8.8.8`
   * **Check output:** `🇺🇸 This is a United States-based IP...`

3. **Test 2 (The "International" path):**
   * **Run** with `ip_address`: `81.2.69.142` (European - United Kingdom)
   * **Check output:** `🌍 This is an international IP...`
   * Or try `114.114.114.114` (Asian - China) for another international example

4. **Test 3 (The "Private IP" path):**
   * **Run** with `ip_address`: `10.0.0.1` (This is a private IP)
   * **Observe:** The `get_geolocation` step will succeed (HTTP 200), but the API returns `status: "fail"` in the response data with no city/country fields
   * You'll see: `This IP could not be geolocated (private or unknown range).`

You've built a workflow that can make decisions and handle errors!

**Click "Next" to bring in the AI.**
