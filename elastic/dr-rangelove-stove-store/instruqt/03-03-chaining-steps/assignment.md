---
slug: 03-chaining-steps
id: yhqhz6pd1vza
type: challenge
title: 'Chaining Steps: From Input to Output'
teaser: Build a workflow that chains HTTP calls with data transformation
tabs:
- id: ol12t7c9c5vj
  title: Kibana
  type: service
  hostname: kubernetes-vm
  path: /app/management/kibana/workflows
  port: 30001
- id: r8exwdlodzkd
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: basic
timelimit: 900
enhanced_loading: null
---

# 📖 Challenge 3: Chaining Steps - From Input to Output

Workflows are powerful because they are a *chain*. The output of one step becomes the input for the next.

Let's build a workflow that takes an IP address, enriches it with a free geolocation API, and then prints the location.

## 1. Create a New Workflow

1. In the **Kibana > Workflows** UI, create a new workflow.
2. Name it `ip_geolocator`.

## 2. Define Inputs and Constants

This time, we'll use `consts` to store our API's base URL. This is a best practice so you don't hardcode URLs or secrets.

Paste this as your base:

```yaml
version: "1"
name: ip_geolocator
description: "Geolocate an IP address using a public API"
enabled: true

consts:
  ip_api_base_url: http://ip-api.com/json

inputs:
  - name: ip_address
    type: string
    required: true
    description: "The IP to geolocate (e.g., 8.8.8.8)"

triggers:
  - type: manual
    enabled: true
```

## 3. Add the `http` Step

This is the workhorse. We will add an `http` step to call the API.

Add this `steps` block below your `triggers`:

```yaml
steps:
  - name: get_geolocation
    type: http
    with:
      url: "{{ consts.ip_api_base_url }}/{{ inputs.ip_address }}"
      method: GET
```

**Analysis:**

* `type: http`: Tells the workflow to make a web request.
* `url:`: We build the URL *dynamically*, combining our `consts` and our `inputs`.

## 4. Add the "Chained" Step

Now, add a *second* step that *uses the output* of the first.

Add this *below* your `get_geolocation` step (inside the `steps` array):

```yaml
  - name: print_location
    type: console
    with:
      message: "IP {{ inputs.ip_address }} is in {{ steps.get_geolocation.response.city }}, {{ steps.get_geolocation.response.country }}."
```

**This is the most important concept:**

* `steps.get_geolocation.response.city`: We are accessing the `response` of the step named `get_geolocation` and digging into its JSON structure.

## 5. Run and Verify

1. **Save** the workflow.
2. **Run** it.
3. For the `ip_address` input, use `8.8.8.8`.
4. Let it run, then click the `print_location` step.
5. Check the **Output** tab. You should see: `"IP 8.8.8.8 is in Mountain View, United States."`

You just chained two steps!

**Click "Next" to make this workflow smarter.**
