# Cosmos (formerly Poseidon) — Product Positioning
**Last updated**: 2026-05-01

## Category
**Operating System for Agentic Software Development**

---

## Positioning Statement
**Cosmos is the operating system for agentic software development — a platform where agents don't just assist work, they run it.**

It provides the environment, runtime, memory, and control plane for agents to operate across the entire software development lifecycle — and to improve the system itself over time.

---

## The Shift
We've crossed the first threshold: engineers use agents daily, code generation is fast and cheap. But:
- The bottleneck has shifted to **context, verification, and coordination**
- Individual adoption has not translated into **organizational transformation**

The future is not one agent or one workflow. It is an **environment where agents, humans, tools, and memory coexist and coordinate.**

---

## The Problem — Today's Agent Tools Break at the System Level

### 1. Fragmented workflows
Every engineer builds their own setup. Nothing compounds.

### 2. No shared memory
Agents don't retain knowledge across runs, teams, or systems.

### 3. No execution substrate
Agents lack persistent environments, real integrations, long-running behavior.

### 4. Humans are still the glue
Humans orchestrate workflows, debug failures, connect systems.

---

## The Insight
> The real shift isn't better agents. It's **systems where agents can operate end-to-end.**

The winning abstraction is not "AI coding assistant" or "agent framework." It is: **An operating system for agents.**

---

## What Cosmos Does

### 1. Runs Agents Across the Entire SDLC
Triage → Spec → Implementation → Review → Testing → Deployment → Monitoring

### 2. Provides a Persistent Agent Runtime
Agents are long-lived, stateful, event-driven. They **own workflows to completion**.

### 3. Gives Agents Real Environments
Cloud VMs, tools, credentials, APIs, access to systems (GitHub, CI, Slack, etc.)

### 4. Creates Shared Memory + Filesystem
Agents share context across runs. Patterns accumulate. Corrections compound. Workflows improve over time without being rewritten.

### 5. Enables Agentic System Building
Describe workflows in natural language:
> "When feedback arrives, triage it, create a ticket, implement, and send a PR."

Cosmos creates the agents, wires the workflow, runs it continuously.

---

## Core Design Principle
> **Agents should be able to operate and improve the system they run in.**

Agents, workflows, tools, and integrations are exposed as **files**. Agents can read, modify, and create new ones. This enables: **Agents building systems for agents.**

---

## What This Unlocks

| Capability | Description |
|-----------|-------------|
| **Agentic SDLC** | Agents do the work across the lifecycle; humans step in at key decision points |
| **Agent Teams** | Specialized, long-lived agents with shared memory and coordination |
| **Autonomous Workflows** | Event-driven: "On every merged PR, if docs need updating, create a docs PR" |
| **Self-Improving Systems** | Workflows evolve over time; agents refine behavior; best practices spread |

---

## Mental Model
**Small teams of humans. Large fleets of agents. Cosmos in between.**
- Humans set intent and review key decisions
- Agents execute continuously
- Cosmos coordinates everything

---

## Differentiation

| Dimension | Others | Cosmos |
|-----------|--------|--------|
| **Scope** | Add agents to workflows | Replace workflows with agent-operated systems |
| **State** | Task-based, stateless | Long-lived, memory-backed agents |
| **Scale** | Single agents | Agent fleets that share context, delegate, learn together |
| **Control** | Human-configured | Agent-operated: agents build workflows, manage agents, improve the system |

---

## Why Now
- Agent capabilities rapidly improving
- Code generation is commoditized
- Bottleneck is now **system-level coordination**

Winners = teams that move from **using agents → running agent systems**

---

## Target Users
- AI-native engineering teams
- Platform / infrastructure teams
- Organizations adopting agentic SDLC

---

## Taglines
- The operating system for agentic software development
- Where agents run the work
- From agents to agent systems
- Turn workflows into autonomous systems

## One-Liner
**Cosmos is the operating system where agents run, coordinate, and improve software development — turning fragmented workflows into autonomous, evolving systems.**

---

## Ad-Relevant Claims (Safe to Use)

### ✅ Safe Claims
- Agents run across the full SDLC
- Persistent, stateful agent runtime
- Shared memory across agent runs
- Event-driven autonomous workflows
- Agents can build and improve other agent workflows
- Real cloud environments with tools, credentials, APIs
- Works with GitHub, CI, Slack, Linear
- Describe workflows in natural language
- Small teams of humans, large fleets of agents

### ❌ Off-Limits
- Do NOT claim specific user counts unless provided
- Do NOT claim speed benchmarks unless provided
- Do NOT use "AI-powered" — say what it actually does
- Do NOT position as an IDE or coding assistant
- Do NOT compare directly to Cursor, Copilot, etc. (different category now)
- Do NOT use "ADE" or "AIDE"

### Competitor Context (New Category)
| vs | Cosmos's difference |
|----|---------------------|
| Coding assistants (Cursor, Copilot) | Not a tool — an OS for agent systems |
| Terminal agents (Claude Code, Codex CLI) | Persistent, stateful, event-driven — not session-based |
| Agent frameworks (LangChain, CrewAI) | Full runtime + environments + memory, not just orchestration code |
| DevOps platforms (GitHub Actions, Jenkins) | Agent-native: agents are first-class, not scripts in YAML |
| Single-agent tools | Fleet coordination: agents share context, delegate, learn together |
