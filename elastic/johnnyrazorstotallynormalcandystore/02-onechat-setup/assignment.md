---
slug: onechat-setup
id: 9z5qeybsp62i
type: challenge
title: OneChat Setup
teaser: Connect OneChat to an LLM Chat Completion Model
tabs:
- id: ochr2uda1du0
  title: Kibana - Spaces
  type: service
  hostname: kubernetes-vm
  path: /app/management/kibana/spaces
  port: 30001
  custom_request_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self''; worker-src blob: ''self''; style-src ''unsafe-inline''
      ''self'''
  custom_response_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self''; worker-src blob: ''self''; style-src ''unsafe-inline''
      ''self'''
- id: njkw4ydyevpr
  title: Kibana - Console
  type: service
  hostname: kubernetes-vm
  path: /app/dev_tools#/console/shell
  port: 30001
  custom_request_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self''; worker-src blob: ''self''; style-src ''unsafe-inline''
      ''self'''
  custom_response_headers:
  - key: Content-Security-Policy
    value: 'script-src ''self''; worker-src blob: ''self''; style-src ''unsafe-inline''
      ''self'''
difficulty: ""
timelimit: 0
enhanced_loading: null
---
On this challenge you:
- Set the feature flags to enable OneChat and  APIs.
- Confiture the Chat Completion LLM connection

Configure OneChat and Chat UI
===
> [!NOTE]
> This step is only necessary until OneChat is released for public preview

## Create Search Space
1. Open the [button label="Kibana - Spaces"](tab-0) tab
    - This is the Spaces management section of Kibana
3. Click "Edit" in the far right pop-up menu
![CleanShot 2025-08-06 at 15.53.22@2x.png](../assets/CleanShot%202025-08-06%20at%2015.53.22%402x.png)
3. Click "Edit Space" on the the Default space line

2. Under "Select solution view" select `Elasticsearch`
![CleanShot 2025-07-30 at 09.57.41@2x.png](../assets/CleanShot%202025-07-30%20at%2009.57.41%402x.png)
4. Click "Apply Change"
5. Click "Update Space" in the pop-up confirmation message.

## Enable OneChat and APIs
1. Switch to the [button label="Kibana - Console"](tab-1) tab
2. Copy and paste the below code into the left console window
```json
POST kbn://internal/kibana/settings
{
   "changes": {
      "onechat:mcp:enabled": true,
      "onechat:api:enabled": true,
      "onechat:ui:enabled": true
   }
}
```
3. Run the above command
    ![CleanShot 2025-08-11 at 14.06.44@2x.png](../assets/CleanShot%202025-08-11%20at%2014.06.44%402x.png)
4. Reload the tab

Configure LLM Connector
==
> For now you have to create the LLM Connector through Playground
> OneChat will eventually let you configure this directly

## Configure LLM Connector
1. Open `Chat` -> `Conversations` the left navigation panel
![CleanShot 2025-08-19 at 13.51.35@2x.png](../assets/CleanShot%202025-08-19%20at%2013.51.35%402x.png)
2. Click on **AI Assistant** in the top right of the tab
3. Click on **Set up GenAI connector**
![CleanShot 2025-08-19 at 13.45.54@2x.png](../assets/CleanShot%202025-08-19%20at%2013.45.54%402x.png)
4. Click the **OpenAI** button
![CleanShot 2024-09-10 at 15.03.30@2x.png](../assets/CleanShot%202024-09-10%20at%2015.03.30%402x.png)
5. Fill out the form using the variable below, The API key is unique to you and vaild only for this workshop!
- Connector Name =>
```
OpenAI
```
- **URL** =>
```
[[ Instruqt-Var key="LLM_CHAT_URL" hostname="kubernetes-vm" ]]
```
- **Default model** =>
```
gpt-4o
```
- Leave `OpenAI Organization` blank =>
```nocopy

```
- Leave  `OpenAI Project`  blank =>
```nocopy

```
   - **API Key** =>
```
[[ Instruqt-Var key="LLM_KEY" hostname="kubernetes-vm" ]]
```

7. Click Save
    - You will see a pop letting you know the connector was created
![CleanShot 2024-09-06 at 11.37.31@2x.png](../assets/CleanShot%202024-09-06%20at%2011.37.31%402x.png)
8. Click on the `X` or click off of the flyout to close the AI Assistant panel
![CleanShot 2025-08-19 at 13.54.10@2x.png](../assets/CleanShot%202025-08-19%20at%2013.54.10%402x.png)

Test Chat UI
==
Go to Chat -> Conversations

Ask a question like
```
Are you online?
```
or

```
What can you help with?
```
You should get a response similar to the screenshot below.
![CleanShot 2025-07-30 at 10.20.55@2x.png](../assets/CleanShot%202025-07-30%20at%2010.20.55%402x.png)
_click the image to enlarge_
