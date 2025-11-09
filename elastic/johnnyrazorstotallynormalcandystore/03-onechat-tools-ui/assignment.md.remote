---
slug: onechat-tools-ui
id: ajuxnhvnx2qo
type: challenge
title: Create a New Tool
teaser: Create your first custom Tool
tabs:
- id: dibh4pgt5wvd
  title: Kibana - Tools
  type: service
  hostname: kubernetes-vm
  path: /app/chat/tools
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
# On this challenge you will:
- Create new custom tools for our MCP Server
---
# Create Your First Custom Tool

1. Click on [button label="Kibana - Tools"](tab-0) tab (Chat -> Tools)
2. Click on `New Tool`
![CleanShot 2025-08-19 at 14.00.32@2x.png](../assets/CleanShot%202025-08-19%20at%2014.00.32%402x.png)
3. under `Name` put:
```
esql_symbol_news_and_reports
```
4. Under `Description` put:
```
Find news and reports for a symbol
```
5. Under `ES|QL` put:
```
FROM financial_news, financial_reports
  | where MATCH(primary_symbol, ?symbol)
  | limit 5
```
6. Click on `Infer parameters from query`:

![CleanShot 2025-07-29 at 17.58.53@2x.png](../assets/CleanShot%202025-07-29%20at%2017.58.53%402x.png)

7. You should see a `symbol` entry. In the `description` box for that row put:
```
The asset symbol to lookup
```
8. Leave the `type` as
```nocopy
Text
```
![CleanShot 2025-08-19 at 14.04.01@2x.png](../assets/CleanShot%202025-08-19%20at%2014.04.01%402x.png)
- *click image to enlarge*

9. Click `Save`

You'll see a toast message letting you know the tool has been created
![CleanShot 2025-07-29 at 18.03.40@2x.png](../assets/CleanShot%202025-07-29%20at%2018.03.40%402x.png)

You'll also see our new tool in the tools list:
![CleanShot 2025-08-19 at 14.05.56@2x.png](../assets/CleanShot%202025-08-19%20at%2014.05.56%402x.png)
