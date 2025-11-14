---
slug: 02-hello-world
id: sunyyx6xqswh
type: challenge
title: Building Your First Workflow
teaser: Create a simple workflow with inputs and console output
tabs:
- id: rtyf1nawuqkv
  title: Kibana - Workflows
  type: service
  hostname: kubernetes-vm
  path: /app/workflows
  port: 30001
- id: kjq04qixcpft
  title: Terminal
  type: terminal
  hostname: host-1
difficulty: basic
timelimit: 600
enhanced_loading: null
---

# 📖 Challenge 2: Building Your First Workflow

Let's start with the "Hello, World!" of automation. We will build a simple workflow that takes a user's name as input and prints a greeting to the console.

## 1. Find the Workflow UI

In the [button label="Kibana"](tab-0) tab:

You should be in the **Workflows** UI. If you switched out of it:
   1. Go to the main menu (the "hamburger" icon).
   2. Navigate to **Management > Workflows**.
   3. This opens the Workflows UI (a new Tech Preview feature).

## 2. Create a New Workflow

1. Click **"Create a new workflow"**.
    ![CleanShot 2025-11-13 at 11.12.10@2x.png](../assets/CleanShot%202025-11-13%20at%2011.12.10%402x.png)
2. This will open the YAML editor. Delete all the boilerplate text.

## 3. Define the Inputs

A workflow needs to know what data it expects. Paste this `inputs` block.
- It tells the workflow to expect one `string` called `username`.

```yaml
version: "1"
name: hello_world
enabled: true

inputs:
  - name: username
    type: string
    required: true
    description: "The name of the user to greet"
```

## 4. Define the Steps

Now, let's tell the workflow *what to do*. We'll add a `steps` block with one `console` step.

Paste this *below* your `inputs` block:

```yaml
triggers:
  - type: manual

steps:
  - name: print_greeting
    type: console
    with:
      message: "Hello, {{ inputs.username }}!"
```

> [!IMPORTANT]
> Spaces in YAML are important
> `triggers` and `steps` should be at the beginning of the line, no indents.

<details>
  <summary>Click to see Full YAML</summary>

```yaml
version: "1"
name: hello_world
enabled: true

inputs:
  - name: username
    type: string
    required: true
    description: "The name of the user to greet"

triggers:
  - type: manual

steps:
  - name: print_greeting
    type: console
    with:
      message: "Hello, {{ inputs.username }}!"
```

</details>

**Look closely at the `message`:**

* We use `{{ ... }}` (Liquid templating) to access data.
* `inputs.username` directly references the input we defined!

## 5. Save and Run the Workflow

1. Click **"Save"** in the top right.
2. Now, click the top ▶️ (run) button (next to save).
    ![CleanShot 2025-11-13 at 11.37.47@2x.png](../assets/CleanShot%202025-11-13%20at%2011.37.47%402x.png)
3. A panel will appear asking for the `username`.
4. In the `username` field, replace the placeholder text "Enter a string" with your actual name (e.g., "Alex") and click **"Run"**.
    ![CleanShot 2025-11-13 at 11.30.04@2x.png](../assets/CleanShot%202025-11-13%20at%2011.30.04%402x.png)

## 6. Check the Output

You will see the workflow run in real-time.

* Click on the `print_greeting` step.
* In the **Output** tab, you should see your message: `"Hello, Alex!"` (or whatever name you enter!)
![CleanShot 2025-11-12 at 09.17.22@2x.png](../assets/CleanShot%202025-11-12%20at%2009.17.22%402x.png)

You've built and run your first workflow!

**Click "Next" to continue.**
