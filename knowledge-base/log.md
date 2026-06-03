# Knowledge Base Log
Append-only. Each entry records what changed and why.

---

## [2026-05-01] init | Knowledge Base Created
- Created KB structure following LLM Wiki pattern
- Schema: `KNOWLEDGE.md` — defines 3-layer architecture (sources → wiki → schema), operations (ingest, query, lint), conventions
- Created `index.md`, `log.md`

## [2026-05-01] ingest | Full Account Audit
- Source: User-provided retro (all-time account data) + 6 live MCP queries (last 30d)
- Created: `01-account-audit.md` — 13 sections covering account overview, conversion tracking, campaign tiers, impression share, QS analysis, device performance, hourly performance, ad group detail, negative keyword gaps, audience inventory, budget allocation, agent results, top 10 issues
- Key findings: 7/9 conversion actions are PRIMARY (critical), brand IS at 10% (budget-starved), LP quality BELOW_AVERAGE on all non-brand keywords, desktop CR 8x mobile, budget inverted (YouTube $0 return gets 4x brand budget)
- MCP queries run: conversion_actions, keyword_quality_scores, campaign_impression_share, device_performance, ad_schedule_hourly, all_ad_groups_30d
- Failed query: geographic_view (parsing error — retry needed)

## [2026-05-01] ingest | Google Ads Architecture
- Source: Figma board — Google Ads System Architecture diagram
- Created: `02-google-ads-architecture.md` — 9-layer system flow, ASCII diagram, layer-by-layer breakdown, optimization lever mapping, key formulas
- Key insight: Agent operates in Layer 9 (Feedback Loop) touching only Creative + Negatives. Highest-impact levers (conversion setup, budget, bidding, campaign structure) are upstream and untouched.

## [2026-05-01] ingest | Product Positioning — Cosmos
- Source: User-provided product positioning document
- Created: `03-product-positioning.md` — Cosmos (formerly Poseidon/Intent) as OS for agentic software development
- Key change: Category shift from "developer workspace" to "operating system for agent systems". This invalidates most existing campaign targeting (Cursor, Claude Code, spec-driven development keywords). New keyword universe needed around platform/infrastructure buyer intent.
- Added: Ad-relevant claims section (safe + off-limits), new competitor context matrix

## [2026-05-01] ingest | Agent Architecture Proposal v2
- Created: `agent-architecture-proposal.md` — 4-layer composable system design
- Layers: Intelligence (weekly) → Strategy (bi-weekly, human-gated) → Execution (daily, autonomous) → Measurement (continuous)
- 15 components across 4 layers, up from 2 components in v1
- MCP tool map: 7 available, 9 needed for full v2
- 4-phase implementation roadmap (12 weeks): Enhanced Execution → Measurement → Intelligence → Strategy
- Review gate architecture: Strategy layer always requires human approval before deployment
- Knowledge Base (LLM Wiki) sits at center — all layers read, Intelligence + Execution write

## [2026-05-01] ingest | Executive Audit
- Created: `executive-audit.md` — shareable boss-ready audit document
- Synthesized from account audit + MCP queries into 5 key problems, budget reallocation table, 10 prioritized next steps

## [2026-05-01] ingest | Audience Strategy (Cosmos) — Full Recommendation
- Sources: Account performance data (8 cycles) + Ahrefs keyword research (20 KWs) + Proxy MCP competitor intel (4 competitors, 122 live ads) + Google Ads Transparency Center + URL library (31 URLs) + 6 custom segment definitions + negative keyword list + in-market/affinity audiences
- Created: `audience-strategy-cosmos.md` — comprehensive audience targeting strategy
- 6 Custom Segments defined: Agentic Dev Buyers, Competitor Evaluators, Platform & DevEx Leaders, Agent Builders, Eng Leadership, Branded
- 10 In-Market/Affinity positive layers + 3 negative layers
- Suppression framework (4 exclusion lists)
- 25+ negative keywords (proven from our data + new from research)
- Competitive positioning by segment (Cursor, Claude, Replit, Devin)
- 7-week rollout plan
- Budget allocation by segment ($69K/mo total)
- Measurement framework with kill/scale thresholds
- All recommendations grounded in our 8-cycle experiment heuristics (Rules #1, #7, #8)

## [2026-06-03] refresh | Product Positioning — Cosmos
- Source: Updated messaging house provided by Molisha
- Updated: `03-product-positioning.md` — full rewrite to current source-of-truth
- Key change: Higher-level frame swapped from "The Operating System for Agentic Software Development" to "Agentic SDLC" — owned the way Atlassian owns "Agile", thought-leadership-only, never as product descriptor. Product category remains "Unified Cloud Agents Platform".
- New explicit guardrails added to §8: do not name Stripe/Ramp/Uber as customers; do not use "AI transformation," "AI software engineer/droid/coding agent" framing; "SDLC" stays out of broad customer-facing copy (Agentic SDLC excepted as category theme).
- Expanded §4 with full Customer pain + Product proof bullets for each of the four key values.
- Added §5 Audience switching rules (CTO ↔ Staff Eng vocabulary swaps).

## [2026-05-01] init | Schema Established
- Created: `KNOWLEDGE.md` — full schema with directory structure, three-layer architecture, operations (ingest/query/lint), conventions, agent startup sequence
- Defined: page format, naming conventions, data citation rules, cross-referencing requirements
- Defined: agent startup sequence (5-step read order for every new run)
