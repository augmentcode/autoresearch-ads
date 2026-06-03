# Augment Cosmos — Product Messaging (Source of Truth)
**Last updated**: 2026-06-03

A single source of truth for how we talk about Augment Cosmos. Use this doc as context when drafting any external content (web, email, social, sales collateral, event copy, ads). If a claim isn't supported here, it shouldn't be in the copy.

---

## Summary

**Product:** Augment Cosmos.

**Category:** Unified Cloud Agents Platform (acceptable shorthand: Unified Agents Platform).

**Company mission:** We make software teams AI native.

**Higher-level theme we own:** Agentic SDLC — the outcome an engineering org reaches when agents work across the software development lifecycle as one coordinated system. For now we treat it as a category theme to own (the way Atlassian owns "Agile"), not the product descriptor — though it could eventually become the product category itself.

**One-line positioning:** Augment Cosmos is the unified cloud agents platform with shared context and memory that compounds across the team and the software development lifecycle.

**The narrative:** Coding agents have made individual developers more productive, but those gains haven't reached the organization. Engineers are drowning in agent-generated PRs, quality is dropping, and nothing is compounding. What's missing is a system — one where humans, agents, code, tools, policy, and memory are coordinated at the org level. Cosmos is that system, productized.

**Four key values:**

1. Unified across the software development lifecycle — one platform, no integration work per use case
2. Self-improving agents — patterns and corrections compound across the team
3. Enterprise scale — reliable across large codebases and high concurrent volume
4. Enterprise control — observable, auditable, governed by default

**Primary buyer:** CTO / VP Engineering at enterprise companies (ideally cloud-native).

**Key competitive frames:** Build vs buy, multi-model vs single-lab lock-in, true unified platform vs stitched cloud services.

---

## 1. What we believe

Coding agents promised massive productivity gains. At the individual level, that promise has been real — engineers are shipping more code than ever, often wiring up their own agent workflows to ship even more.

But the organization doesn't feel 10x more productive. Individual productivity is not organizational productivity. Agents have made individuals faster in silos, with no shared patterns and no shared memory. The result is more PRs, more tickets, more 2am alerts, but nothing compounding.

What's missing is a system — one where humans, agents, code, tools, policy, and memory are coordinated at the org level, where every new agent inherits the context the team has already built, and where knowledge compounds instead of resetting with every session. The teams modernizing fastest — Stripe, Ramp, Uber — are building this system themselves. Augment Cosmos is that system, productized.

---

## 2. The category

**Category name:** Unified Cloud Agents Platform (acceptable shorthand: Unified Agents Platform)

**Category definition:** A unified platform for running agents in the cloud, with shared context and memory that compounds across the team and the software development lifecycle.

**The higher-level theme we own: Agentic SDLC.** For now this is the destination, not the product descriptor — the state an engineering organization reaches when agents operate across the software development lifecycle as one coordinated system rather than a swarm of disconnected workers. We own Agentic SDLC the way Atlassian owns "Agile": through thought leadership and content, positioned as the outcome that the Unified Cloud Agents Platform delivers. It's how we make software teams AI native. Today we keep it at the category/narrative level — it is not the product's name, and the bare acronym "SDLC" stays out of broad customer-facing copy — but it could eventually become the product category itself as the market matures.

---

## 3. Product positioning

**Single sentence (CTO / VP Engineering):**
Augment Cosmos is the unified cloud agents platform with shared context and memory that compounds across the team and the software development lifecycle.

**Single paragraph (CTO / VP Engineering):**
Augment Cosmos is the unified cloud agents platform for engineering organizations that have rolled out individual coding agents and are now feeling the breakdown. Engineers are buried in agent-generated PRs, quality is dropping, and the productivity gains haven't reached the organization. Cosmos coordinates that energy into one system. Agents share context and memory across the team, with patterns and corrections compounding session over session. Built on a shared context engine, tenant-wide memory, and an event-driven runtime, Cosmos is what teams like Stripe, Ramp, and Uber are building for themselves — productized. Humans steer; agents do the doing; the system gets better over time.

**Single sentence (Staff engineer / platform lead):**
Augment Cosmos is a unified cloud agents platform with the composable building blocks to run agents in production: governed, observable, and reproducible.

**Single paragraph (Staff engineer / platform lead):**
Augment Cosmos gives platform engineers the building blocks to operationalize agents across the software development lifecycle. Environments define where agents run and what they can touch. Experts define how agents behave, what tools they use, and what events they subscribe to. Sessions turn one-off prompts into auditable, replayable workflows. Each can stay private to one engineer or get promoted into a shared capability the whole org draws on. Cosmos runs in your own environment or in our cloud sandboxes; supports BYOK across major model providers; and is observable and auditable by default.

---

## 4. The four key values

### 4.1 Unified across the software development lifecycle

**Promise — Unified:** One platform where agents work across every tool, surface, and stage of software development, with no integration work to stitch it together.

**Customer pain:** Building agentic workflows today means stitching point solutions together. CodeRabbit for review, Cursor for coding, separate tools for triage, testing, monitoring. Each tool has its own integrations, its own auth, its own data model, its own context. Knowledge is split across tools. Building a workflow that spans more than one stage is a custom integration project every time.

**Cosmos promise:** Cosmos is one platform that connects to the tools and events your team already works from, so agents can be deployed anywhere across the software development lifecycle without custom plumbing for each new use case. Set up an agent for code review, incident triage, deployment monitoring, or a full multi-stage workflow with the same building blocks.

**Product proof:**

- Agents trigger automatically off the events teams already work from: PRs, production alerts, Jira and Linear tickets, schedules, and webhooks.
- Agents work where the team already does — CLI, web, Slack, mobile — not in a separate console.
- New workflows can be set up in natural language; no custom integration work for each new use case.

### 4.2 Compounding capability

**Promise — Self-improving agents:** Every agent built, every pattern learned, and every correction made compounds across the team.

**Customer pain:** Every coding agent on the market today starts from zero on every task. There's no shared context, no shared memory, no institutional knowledge. The patterns one engineer figures out don't carry forward, and the agents don't improve as the team works with them.

**Cosmos promise:** Cosmos is built on a shared context engine and a shared virtual filesystem with tenant-wide and private memory. Patterns, conventions, and corrections accumulate. Experts built by one engineer can be promoted into shared capabilities the whole org draws on. Institutional memory becomes a primitive, not an aspiration.

**Product proof:**

- Agents share a memory layer across the team, so patterns, conventions, and corrections accumulate instead of resetting each session.
- Agents built by one engineer can be promoted into shared capabilities the whole org uses — and improves on.
- Cosmos ships with a knowledge base of agent patterns refined across customer engagements; new agents lean on it and contribute back to it.

### 4.3 Enterprise scale

**Promise — Reliability:** Agents that run reliably across large codebases and high volumes of concurrent work, without an internal team to keep the system standing up.

**Customer pain:** Reliability is the hardest part of running agents at enterprise scale, and it's the reason internal "build it ourselves" projects stall. Most agentic tools demo well on small codebases and isolated tasks, then fall over in production: agents lose context in repos with millions of lines of code, fail unpredictably under concurrent load, and produce inconsistent results across long-running sessions. Solving this is a full-time job for a dedicated platform team, and even the most sophisticated organizations are finding it harder than expected.

**Cosmos promise:** Cosmos is built to run reliably at the scale enterprises actually operate at, so the customer doesn't have to staff a team to keep it running. Agents understand large, complex codebases from the first run. Sessions are durable across long-running and parallel work. The platform is designed for hundreds of concurrent agents per organization, not handfuls.

**Product proof:**

- Augment's Context Engine gives agents a grounded understanding of large enterprise codebases, not just toy repos.
- Agents and sessions are designed to run in parallel at high volume, with consistent behavior under load.
- Long-running sessions and agent teams persist across days and weeks without losing context.
- Reliability is Augment's problem, not the customer's. We maintain the platform; their team maintains their software.

### 4.4 Enterprise control

**Promise — Governance:** Run agents at scale with the observability, auditability, and human-in-the-loop controls enterprises require.

**Customer pain:** Agentic tools are exciting, but most weren't built for the controls a CTO needs to run them at scale. Where does the agent run? What can it touch? Who reviews what it does? When does a human get pulled in? These questions don't have clean answers in most agentic products today, which keeps adoption stuck in pilot.

**Cosmos promise:** Cosmos is governed by default. Every action is observable, every run is auditable, and human-in-the-loop is a feature, not an add-on. Teams set the policies for where human judgment is required, and Cosmos enforces them.

**Product proof:**

- Runs in your own environment or in our cloud sandboxes — your choice.
- Multi-model by default — bring your own keys for Anthropic, OpenAI, Bedrock, Vertex, or open-source models.
- Teams configure where humans get pulled in for review, and the platform enforces those rules.
- Every agent action is observable and auditable.

---

## 5. Who this is for

### Primary ICP: CTO / VP of Engineering

The CTO at an enterprise company (ideally cloud-native, with existing digital fluency) modernizing engineering to keep pace with tech-forward leaders like Stripe, Ramp, and Uber. They're convinced agents are the next platform shift and want their org to lead, not follow. They've already seen the limits of IDE-bound coding tools and know they need a system, not another point tool. They're the decision maker, often the champion, and often coordinating with the CEO as economic buyer given the scale of the transformation.

**What they care about:**

- Turning individual developer gains into organizational productivity
- Getting their team's agents working as one system rather than a swarm of disconnected workers
- Proving the agentic model works at enterprise scale
- Governance, observability, and security that satisfy security and compliance teams
- A system that compounds in value rather than another tool to maintain

### Secondary ICP: Staff engineer / platform lead

The senior IC the CTO brings in to onboard and execute on the initial workflows. Often already tinkering, building a homegrown version of this themselves, or in the CTO's ear about building an AI SDLC. They evaluate the primitives and decide whether the platform holds up under real production conditions.

**What they care about:**

- Composable primitives they can wire into existing systems
- Reproducible Environments and observable Sessions
- BYOK, deployment in their own environment, and integration with the tools they already run

### Audience switching rules

Vocabulary that swaps between audiences:

- "Governance" (CTO) → "policy enforcement" (Staff Eng)
- "Observability" (CTO, abstract) → "every action emits a structured event" (Staff Eng, concrete)
- "Scale" (CTO) → "concurrent sessions, durable across long-running runs" (Staff Eng)
- "The system gets better over time" (CTO) → "tenant memory persists corrections and patterns across sessions" (Staff Eng)

---

## 6. Pain points we're testing

**1. Agent chaos.** Engineers are overwhelmed by agent-generated PRs. Quality is dropping. More incidents. Most relevant to organizations that have aggressively rolled out individual coding agents and are feeling the breakdown. For organizations earlier in adoption, this is what they will feel — but they may not be ready to buy a unified platform yet.

**2. Cost of point solutions.** Enterprises are stacking individual products (CodeRabbit for review, Cursor for coding, others for testing and triage) and spending heavily on seats and tokens with no compounding return. Most relevant to CTOs under cost pressure or coming up on a budget review.

**3. Fragmentation.** Too many point solutions, none of them talking to each other. Knowledge split across tools. No shared memory or context. Most relevant to organizations whose AI tooling has grown organically and now resembles a stack rather than a system.

---

## 7. Competitive framing

**1. Build vs buy.** The most sophisticated engineering organizations (Stripe, Ramp, Uber) are building this themselves, and internal platform teams at most enterprises will instinctively want to do the same. Cosmos is what those teams would have built if they wanted it productized — without the multi-year investment, the maintenance burden, or pulling platform engineers off their core work.

**2. Big model lab offerings (Claude Managed Agents, OpenAI Codex).** Model providers extending downstream into agent products. The differentiator: with Cosmos, customers aren't locked into a single model. BYOK across Anthropic, OpenAI, Bedrock, Vertex, and open source means they're not betting their agentic strategy on one lab's roadmap, ecosystem, or pricing.

**3. Big cloud provider platforms (AWS, Google enterprise agent platforms).** Both have launched platforms positioned as unified offerings. The differentiator: in reality, customers end up stitching together a collection of micro cloud services to make them work. Cosmos is a true unified platform, not a bunch of separate services connected by the customer.

---

## 8. Language to use, language to avoid

**Use:**

- Unified Cloud Agents Platform (default category descriptor)
- Unified Agents Platform (acceptable shorthand)
- Cloud Agents Platform (acceptable shorthand)
- We make software teams AI native (company mission)
- Agentic SDLC (as the higher-level category theme / outcome we own — in thought-leadership, category, and narrative contexts; never as the product descriptor)
- Across the software development lifecycle (in long form)
- Individual productivity vs organizational productivity
- Shared context, shared memory, learnings carry forward
- One system, not a swarm of disconnected workers
- Agents and humans coordinate
- Humans steer; agents do the doing
- Environments, Experts, Sessions
- Context engine, tenant memory
- Event-driven, observable, auditable

**Avoid:**

- Any phrasing that implies Stripe, Ramp, or Uber are Cosmos customers. They are referenced in this document as examples of sophisticated engineering organizations building this kind of system internally — they are not customers and have no commercial relationship with Cosmos. Do not write "trusted by," "used by," "including," or any list-style construction that places them alongside customer names. Do not write "leading enterprises like Stripe and Uber are building on Cosmos." Acceptable: "The teams modernizing fastest — Stripe, Ramp, Uber — are building this system themselves." Cosmos is what those teams would have built, productized.
- "Agentic software development platform" or "Agentic SDLC platform" as the product/category descriptor. The product is the Unified Cloud Agents Platform (or Unified Agents Platform). "Agentic SDLC" is a theme we own, not the platform's name.
- "SDLC" as a bare acronym in broad customer-facing copy (homepage, ads, top-of-funnel). Customers don't say it. Spell out "software development lifecycle" or name the specific stages (review, testing, deployment, etc.). Exception: "Agentic SDLC" is allowed as the category term in thought-leadership and category contexts (see Use).
- "AI transformation" or "AI-native transformation." Consultant / change-program language; engineering leaders react badly to it. Note the distinction: "AI native" as a state or mission ("make software teams AI native") is fine; "AI transformation" as a program is not.
- "AI software engineer," "AI engineer," "droid," or any framing that names agents as replacements for humans on the team. This reads as threatening to engineering leaders adjacent to our buyer and consistently lands badly.
- "Coding agent" as a description of Cosmos. Coding is one of many things agents on Cosmos do.
- Replacement language generally. Cosmos is about coordination, not substitution.

---

## 9. Customer proof

*Cosmos is in design partner stage. Customer references and case studies will be added as design partner agreements allow. Until then, copy should not imply published case studies or named customer outcomes.*
