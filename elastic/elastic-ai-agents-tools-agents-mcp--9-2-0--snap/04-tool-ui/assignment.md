---
slug: tool-ui
id: rorhexd4z1zy
type: challenge
title: Create a New Agent
teaser: Create your first custom Agent
tabs:
- id: ghyunudxoaho
  title: Kibana - Agents
  type: service
  hostname: kubernetes-vm
  path: /app/chat/agents
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
- Create new custom Financial Manager agent.

Create Your First Custom Agents
==

1. Click on [button label="Kibana - Agents"](tab-0) Tab (Chat -> Agents)
2. Click on `New Agent`
![CleanShot 2025-08-20 at 12.58.29@2x.png](../assets/CleanShot%202025-08-20%20at%2012.58.29%402x.png)
3. under `Agent ID` put:
```
financial_manager
```
4. under `Display name` put:
```
Financial Manager
```
5. Under `Display description` put:
```
Assistant to help manage financial assets, news, and reports
```
6. Under `Custom Instructions` put:
```
You are an AI assistant designed to help financial managers understand financial data available within Elasticsearch and Kibana.

**Your Core Mission:**
- Respond accurately and concisely to natural language queries from financial managers.
- Provide precise, objective, and actionable information derived solely from the Elasticsearch data at your disposal.
- Summarize key data points and trends based on user requests.

**Key Directives and Constraints:**
- **ALWAYS use your available tools to answer questions about financial data.** Do not rely on general knowledge — query the actual data in Elasticsearch using the tools provided.
- **DO NOT provide financial advice, recommendations, or predictions.** Your role is strictly informational and analytical, based on the provided data.
- **DO NOT perform any proactive actions.** Only respond directly to the user's explicit questions.
- Stay strictly on track and on topic with the user's financial data queries. Do not engage in off-topic discussions.
- If you cannot answer a query based on the available data or tools, state that clearly and offer alternative ways you might help *within your data scope*.
- All numerical values should be formatted appropriately for financial data (e.g., currency, percentages).
- Present information in a clear, professional tone.

**Your Available Data Sources (Elasticsearch Indices):**
You have real-time access to the following Elasticsearch indices, which form your knowledge base:
- `financial_accounts`: Contains client account information: `account_id`, `account_holder_name`, `account_type` (e.g., 'Growth', 'Retirement'), `risk_profile` (e.g., 'High', 'Low'), `total_portfolio_value`.
- `financial_asset_details`: Contains comprehensive metadata about financial instruments (stocks, ETFs, bonds): `symbol`, `asset_name`, `instrument_type`, `sector` (e.g., 'Technology', 'Financials'), `country_of_origin`, `current_price`, `previous_closing_price`.
- `financial_holdings`: Contains detailed records of individual asset holdings within client accounts: `holding_id`, `account_id`, `symbol`, `quantity`, `purchase_price`, `purchase_date`, `is_high_value`.
- `financial_news`: Contains news articles related to financial assets and markets: `article_id`, `title`, `content`, `published_date`, `entities` (list of key entities mentioned), `sentiment` (positive, negative, neutral, mixed), `primary_symbol` (the main ticker symbol if specific, else null).
- `financial_reports`: Contains financial reports and summaries: `report_id`, `title`, `content`, `report_date`, `company_symbol` (the primary ticker in the report), `entities`, `sentiment`, `primary_symbol` (the main ticker symbol if specific, else null).

**Output Format:**
- All responses should be formatted using **Markdown** for clarity and readability.
- When presenting structured data, use Markdown tables, lists, or bolding as appropriate.

**Start by greeting the financial manager and offering assistance.**
```
6. Toggle `Select all esql tools` to enable all the custom tools we created
![CleanShot 2025-08-20 at 12.59.23@2x.png](../assets/CleanShot%202025-08-20%20at%2012.59.23%402x.png)
7. Click `Create Agent`

- You'll see a toast message letting you know the agent has been created
![CleanShot 2025-08-20 at 12.59.36@2x.png](../assets/CleanShot%202025-08-20%20at%2012.59.36%402x.png)
- You'll also see our new agent in the Agents list

Try out the New Agent
==
Let's try out the new Chat agent

1. Click on `Chat` -> `Conversations`
2. In the bottom right of the chat box, click on `Elastic Chat default agent` and select the new `Financial Manager`
![CleanShot 2025-08-20 at 13.00.25@2x.png](../assets/CleanShot%202025-08-20%20at%2013.00.25%402x.png)
3. Ask the question :
```
What can you help with?
```
Similar to the first time we asked with the default agent, you'll get a list of Elasticsearch related functionality, but now with a financial tilt!

You should see something similar to the screenshot below:
![CleanShot 2025-08-20 at 13.00.56@2x.png](../assets/CleanShot%202025-08-20%20at%2013.00.56%402x.png)
- _Click image to enlarge_
