---
slug: overview
id: korob9kr7qii
type: challenge
title: Elastic AI Agents - Tools, Agents, and MCP
teaser: Learn about Elastic's AI Agentic Tools
notes:
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025].png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D.png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (1).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(1).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (2).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(2).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (3).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(3).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (4).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(4).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (5).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(5).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (6).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(6).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (7).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(7).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (8).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(8).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (9).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(9).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (10).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(10).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (11).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(11).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (12).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(12).png)'
- type: text
  contents: '![Elastic AI Agents Customer Messaging & Roadmap [August 2025] (13).png](../assets/Elastic%20AI%20Agents%20Customer%20Messaging%20%26%20Roadmap%20%5BAugust%202025%5D%20(13).png)'
tabs:
- id: 85bdikzplfla
  title: What Is MCP
  type: website
  url: https://www.elastic.co/what-is/mcp
  new_window: true
difficulty: basic
timelimit: 0
enhanced_loading: false
---

Welcome to the Elastic Agent Builder Workshop
===

In this hands-on workshop you'll use **Elastic Agent Builder** to build AI agents that can reason over your Elasticsearch data using natural language. Agent Builder combines large language models with Elastic-native search capabilities, giving you a framework to create custom agents and tools -- and expose them to external clients through MCP (Model Context Protocol).

By the end of this workshop, you'll have built a working financial data assistant from the ground up: a custom agent with specialized tools, accessible through both the Kibana chat UI and an external MCP client.

---

What is Elastic Agent Builder?
===

Elastic Agent Builder is a feature in Kibana that lets you:

- **Chat with your Elasticsearch data** using a built-in conversational UI
- **Build custom agents** with tailored instructions, personas, and guardrails
- **Create custom tools** (powered by ES|QL) that give agents precise, efficient access to your data
- **Expose everything via MCP and APIs** so external clients like Claude Desktop, Cursor, or your own apps can use the same agents and tools

Key Concepts
===

| Concept | What It Does |
|---|---|
| **Agent Chat** | The conversational interface in Kibana for talking to agents in real time |
| **Agents** | LLM-powered personas with custom instructions and an assigned set of tools. You control what they can do and how they respond |
| **Tools** | Modular functions that agents call to search, retrieve, and act on Elasticsearch data. Built-in tools work out of the box; custom ES\|QL tools let you tailor queries to your data |
| **MCP** | Model Context Protocol -- a standard for exposing tools to external AI clients. Elastic Agent Builder acts as an MCP server that any compatible client can connect to |

What You'll Build Today
===

Here's what's ahead:

1. **Overview & Presentation** -- You are here. Review the slides and get oriented
2. **Chat Setup** -- Connect Elastic Chat to an LLM and confirm the AI assistant can respond
3. **Create a Custom Tool** -- Write an ES|QL-powered tool that finds news and reports for a financial symbol
4. **Create a Custom Agent** -- Build a Financial Manager agent with specialized instructions and your new tool
5. **ES|QL Refresher** _(optional)_ -- A hands-on walkthrough of ES|QL basics using the workshop's financial data
6. **Explore the APIs** -- Use the Tools, Agents, and Converse APIs directly from the Kibana Console
7. **MCP Client** -- Connect an external MCP client to Elastic's MCP server and chat with your agents from outside Kibana
8. **Feedback** -- Let us know how it went

Getting Started
===

1. Click `View Notes` in the upper right to view the presentation slides
2. [Optional] Read about MCP in the [button label="What Is MCP"](tab-0) tab

---

![social_kegsofduff_human_and_robot_building_chat_app_with_elasticsear_b5a3c6da-b66f-4339-900b-97bcd2ef0299_1.gif](../assets/social_kegsofduff_human_and_robot_building_chat_app_with_elasticsear_b5a3c6da-b66f-4339-900b-97bcd2ef0299_1.gif)
