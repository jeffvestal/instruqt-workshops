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
  path: /app/chat/conversations
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

1. Click on the [button label="Kibana - Chat"](tab-0) tab (`Chat` -> `Conversations` )
![CleanShot 2025-08-20 at 12.41.25@2x.png](../assets/CleanShot%202025-08-20%20at%2012.41.25%402x.png)
2. Click on **AI Assistant** in the top right of the tab
3. Click on **Set up GenAI connector**
![CleanShot 2025-08-20 at 12.40.29@2x.png](../assets/CleanShot%202025-08-20%20at%2012.40.29%402x.png)
4. Click the **OpenAI** button
![Upload failed: Something went wrong]()
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
    ![CleanShot 2025-08-20 at 12.42.52@2x.png](../assets/CleanShot%202025-08-20%20at%2012.42.52%402x.png)
8. Click on the `X` or click off of the flyout to close the AI Assistant panel
![CleanShot 2025-08-20 at 12.43.16@2x.png](../assets/CleanShot%202025-08-20%20at%2012.43.16%402x.png)

Test Chat UI
==
You should still be in `Chat` -> `Conversations`

Ask a question like
```
Are you online?
```
or

```
What can you help with?
```
You should get a response similar to the screenshot below.
![CleanShot 2025-08-20 at 12.53.40@2x.png](../assets/CleanShot%202025-08-20%20at%2012.53.40%402x.png)
_click the image to enlarge_
