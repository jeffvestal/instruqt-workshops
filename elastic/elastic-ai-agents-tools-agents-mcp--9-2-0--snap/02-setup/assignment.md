---
slug: setup
id: 9z5qeybsp62i
type: challenge
title: Chat Setup
teaser: Connect Elastic Chat to an LLM Chat Completion Model
tabs:
- id: ochr2uda1du0
  title: Kibana - Chat
  type: service
  hostname: kubernetes-vm
  path: /app/agent_builder/conversations
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
On this challenge you will:
- Configure the Chat Completion LLM connection
- Confirm you can Chat with Robots 🤖

> [!NOTE]
> Click `close` on the dialog box in the upper left
> ![close-dialog-es.png](../assets/close-dialog-es.png)

Configure LLM Connector
==
Elastic Chat needs a connection to a large language model (LLM) so the AI assistant can respond to your questions. We'll configure an OpenAI connector that will also be reused later when connecting an MCP client.

1. Click on the [button label="Kibana - Chat"](tab-0) tab (`Agents` -> `Agent Chat` )
![CleanShot 2025-09-21 at 14.55.59@2x.png](../assets/CleanShot%202025-09-21%20at%2014.55.59%402x.png)
2. Click on **AI Assistant** in the top right of the tab
3. Click on **Set up GenAI connector**
![CleanShot 2025-08-20 at 12.40.29@2x.png](../assets/CleanShot%202025-08-20%20at%2012.40.29%402x.png)
4. Click the **OpenAI** button
![CleanShot 2025-09-21 at 14.58.02@2x.png](../assets/CleanShot%202025-09-21%20at%2014.58.02%402x.png)
5. Fill out the form using the variables below. The API key is unique to you and valid only for this workshop!
- Connector Name =>
```
OpenAI
```
- **URL** => This is the LLM endpoint that Elastic Chat will send requests to.
```
[[ Instruqt-Var key="LLM_CHAT_URL" hostname="kubernetes-vm" ]]
```
- **Default model** =>
```
gpt-4.1
```
- Leave `OpenAI Organization`, `OpenAI Project`, and `Context window length` blank
- **API Key** =>
```
[[ Instruqt-Var key="LLM_KEY" hostname="kubernetes-vm" ]]
```

6. Click Save
    - You will see a pop letting you know the connector was created
    ![CleanShot 2025-08-20 at 12.42.52@2x.png](../assets/CleanShot%202025-08-20%20at%2012.42.52%402x.png)
7. Click on the `X` or click off of the flyout to close the AI Assistant panel
![CleanShot 2025-08-20 at 12.43.16@2x.png](../assets/CleanShot%202025-08-20%20at%2012.43.16%402x.png)

Test Chat UI
==
You should still be in `Agents` -> `Agent Chat`

Lets see what our new Chat agent can do
```
What can you help with?
```
You should get a response similar to the screenshot below.
![CleanShot 2025-09-21 at 15.01.32@2x.png](../assets/CleanShot%202025-09-21%20at%2015.01.32%402x.png)
_click the image to enlarge_

We can check what data is loade in our cluster
```
What indices are available?
```

You can ask other questions but we'll move on to create specialised agents for out data.
