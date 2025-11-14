---
slug: 04-robust-workflows
id: yhiyheqao8wq
type: challenge
title: 'Making it Robust: Logic & Error Handling'
teaser: Add retry logic and conditional branching to workflows
tabs:
- id: 0ivomx1tph00
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: y0uwy6vpglv0
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
You should still be in the  [button label="Kibana - Workflows"](tab-0) tab

1. Click on the  `ip_geolocator` workflow you just built.

## 2. Add Error Handling

What if the API call fails? Let's add an `on-failure` block to the `http` step.

Modify your `get_geolocation` step to look like this:

```yaml
  - name: get_geolocation
    type: http
    with:
      url: "{{ consts.ip_api_base_url }}/{{ inputs.ip_address }}"
      method: GET
    on-failure:
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
    message: >-
      {% assign status = steps.get_geolocation.output.data.status %}
      {% assign cc = steps.get_geolocation.output.data.countryCode %}
      {% assign city = steps.get_geolocation.output.data.city %}
      {% assign country = steps.get_geolocation.output.data.country %}
      {% assign europe = "AL,AD,AT,BA,BE,BG,BY,CH,HR,CY,CZ,DE,DK,EE,ES,FI,FO,FR,GG,GI,GR,HU,IE,IM,IS,IT,JE,LI,LT,LU,LV,MC,MD,ME,MK,MT,NL,NO,PL,PT,RO,RS,SE,SI,SK,SM,UA,UK,VA" %}
      {% assign asia = "AE,AM,AZ,BH,BD,BN,BT,KH,CN,GE,HK,ID,IL,IN,IQ,IR,JO,JP,KG,KR,KW,KZ,LA,LB,LK,MM,MN,MO,MY,NP,OM,PH,PK,QA,SA,SG,SY,TH,TJ,TL,TM,TW,UZ,VN,YE" %}

      {% if status == "success" %}
        {% if cc == "US" %}
          🇺🇸 United States-based IP from {{ city }}.
        {% elsif europe contains cc %}
          🇪🇺 Europe-based IP from {{ city }}, {{ country }}.
        {% elsif asia contains cc %}
          🌏 Asia-based IP from {{ city }}, {{ country }}.
        {% else %}
          🌍 IP from {{ country }}.
        {% endif %}
      {% else %}
        This IP could not be geolocated (private or unknown range).
      {% endif %}
```

This logic block checks the `countryCode` from the API response and changes the message.

## 4. Test All Scenarios

1. Save your workflow.

2. Test 1 (**United States** path):
   - Run with ip_address: `8.8.8.8`
   - Check output under **print_location**
     - “🇺🇸 United States-based IP from …”

3. Test 2 (**Europe** path):
   - Run with ip_address: `81.2.69.142` (United Kingdom)
   - Check output **print_location**
     - “🇪🇺 Europe-based IP from …, United Kingdom”

4. Test 3 (**Asia** path):
   - Run with ip_address: `114.114.114.114` (China)
   - Check output **print_location**
     - “🌏 Asia-based IP from …, China”

5. Test 4 (**Private/unknown** path):
   - Run with ip_address: 1`0.0.0.1` (private IP)
   - **Observe**: Under `get_geolocation` > `1-attempt` > `get_location`
     - `HTTP 200` with `data.status`: `fail` and no city/country
    ![CleanShot 2025-11-13 at 13.39.13@2x.png](../assets/CleanShot%202025-11-13%20at%2013.39.13%402x.png)
   - You’ll see under  **print_location**
     - “This IP could not be geolocated (private or unknown range).”
You've built a workflow that can make decisions and handle errors!

**Click "Next" to bring in the Agents.**
