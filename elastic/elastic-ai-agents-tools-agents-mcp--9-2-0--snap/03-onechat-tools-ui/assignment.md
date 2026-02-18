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
![CleanShot 2025-08-20 at 12.54.34@2x.png](../assets/CleanShot%202025-08-20%20at%2012.54.34%402x.png)
3. under `Tool ID` put:
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
6. Click on `Infer parameters from query` under the ES|QL Parameters section:

![CleanShot 2025-08-20 at 12.55.10@2x.png](../assets/CleanShot%202025-08-20%20at%2012.55.10%402x.png)

7. You should see a `symbol` entry. In the `description` box for that row put:
```
The asset symbol to lookup
```
8. Leave the `type` as
```nocopy
text
```
![CleanShot 2025-08-20 at 12.55.32@2x.png](../assets/CleanShot%202025-08-20%20at%2012.55.32%402x.png)
- *click image to enlarge*

9. Click `Save`

You'll see a toast message letting you know the tool has been created
![CleanShot 2025-08-20 at 12.55.57@2x.png](../assets/CleanShot%202025-08-20%20at%2012.55.57%402x.png)

You'll also see our new tool in the tools list:
![CleanShot 2025-08-20 at 12.57.30@2x.png](../assets/CleanShot%202025-08-20%20at%2012.57.30%402x.png)
