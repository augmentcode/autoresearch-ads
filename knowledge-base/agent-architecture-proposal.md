# Autoresearch-Ads v2 — Agent Architecture Proposal
**Last updated**: 2026-05-01 | **Status**: Draft v1

---

## The Problem: Single-Loop Agent Hitting a Ceiling

The v1 agent is a **monolithic daily cycle** touching 2 of 11 optimization levers:

```
┌─────────────────────────────────────────────────────────────┐
│                   CURRENT AGENT (v1)                        │
│                                                             │
│  program.md → Daily Cycle (Steps 0-9)                       │
│                                                             │
│  Pull → Compress → Analyze → Generate → Review → Deploy     │
│                                                             │
│  Scope:   Ad copy (RSAs) + Negative keywords                │
│  Covers:  8 of 19 campaigns                                │
│  Memory:  experiments.jsonl + learnings.md (flat)           │
│  Cycle:   1x daily                                          │
│  Result:  0.49% → 1.19% CR (+109%), then FLAT               │
└─────────────────────────────────────────────────────────────┘
```

**Why it's flat:**
- Touches 2 of 11 levers (copy + negatives = medium impact)
- 5 CRITICAL/HIGH levers untouched: conversion setup, budget, bidding, campaigns, LP
- No external intel (competitor monitoring, keyword research)
- No knowledge compounding (flat learnings.md, no cross-references)
- Monolithic — can't run pieces independently

---

## Design Principles

1. **Composable**: Each component runs independently and adds value alone
2. **Layered**: Intelligence feeds Strategy feeds Execution feeds Measurement
3. **Knowledge-centric**: All components read/write the LLM Wiki knowledge base
4. **Progressive**: Start with Execution (v1 enhanced), add layers incrementally
5. **Human-in-the-loop**: Strategy layer always requires review gate; Execution can run autonomously within guardrails


```
╔════════════════════════════════════════════════════════════════════════╗
║              AUTORESEARCH-ADS v2 — 4-LAYER SYSTEM                    ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌────────────────────────────────────────────────────────────────┐   ║
║  │  LAYER 1: INTELLIGENCE            Cadence: Weekly / On-Demand │   ║
║  │                                                                │   ║
║  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────┐  │   ║
║  │  │ Competitive │  │  Keyword    │  │  Market Signal        │  │   ║
║  │  │ Monitor     │  │  Explorer   │  │  Tracker              │  │   ║
║  │  │             │  │             │  │                       │  │   ║
║  │  │ Ahrefs MCP  │  │ Vol + CPC  │  │ Category trends       │  │   ║
║  │  │ Proxy MCP   │  │ + KD       │  │ New entrants          │  │   ║
║  │  │ Ad copy     │  │ Gap finder │  │ Seasonal shifts       │  │   ║
║  │  │ SERP track  │  │ Intent     │  │ Intent evolution      │  │   ║
║  │  │             │  │ classifier │  │                       │  │   ║
║  │  └──────┬──────┘  └──────┬─────┘  └───────────┬───────────┘  │   ║
║  └─────────┼────────────────┼────────────────────┼──────────────┘   ║
║            │                │                    │                   ║
║            ▼                ▼                    ▼                   ║
║  ┌─────────────────────────────────────────────────────────────────┐ ║
║  │                    KNOWLEDGE BASE (LLM Wiki)                   │ ║
║  │                                                                 │ ║
║  │  KNOWLEDGE.md · index.md · log.md                               │ ║
║  │  entities/ · concepts/ · learnings/ · competitive/ · strategy/  │ ║
║  │  sources/snapshots/ · sources/external/                         │ ║
║  │                                                                 │ ║
║  │  ▲ Every layer READS from here                                  │ ║
║  │  ▲ Intelligence + Execution WRITE here                          │ ║
║  └─────────────────────────────────────────────────────────────────┘ ║
║            │                │                    │                   ║
║            ▼                ▼                    ▼                   ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │  LAYER 2: STRATEGY              Cadence: Weekly / Bi-Weekly   │  ║
║  │                                                                │  ║
║  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  ║
║  │  │ Budget   │  │ Campaign │  │ Audience │  │ Bidding      │  │  ║
║  │  │ Allocator│  │ Architect│  │ Builder  │  │ Optimizer    │  │  ║
║  │  │          │  │          │  │          │  │              │  │  ║
║  │  │ IS-based │  │ Create/  │  │ Custom   │  │ Manual→tCPA  │  │  ║
║  │  │ rebalance│  │ pause    │  │ Segments │  │ tCPA tuning  │  │  ║
║  │  │ ROI-wt   │  │ campaigns│  │ Suppress │  │ tROAS eval   │  │  ║
║  │  │ Waste    │  │ Keyword  │  │ In-Mkt   │  │              │  │  ║
║  │  │ detection│  │ grouping │  │ layers   │  │              │  │  ║
║  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │  ║
║  │       │             │             │               │           │  ║
║  │  ┌────▼─────┐  ┌────▼─────┐  ┌────▼──────────────▼────────┐  │  ║
║  │  │Conversion│  │ Device / │  │       REVIEW GATE          │  │  ║
║  │  │ Config   │  │ Schedule │  │   (Human approval req'd)   │  │  ║
║  │  │          │  │ Adjuster │  │                             │  │  ║
║  │  │ Primary/ │  │ Mobile   │  │  All Strategy changes stop  │  │  ║
║  │  │ secondary│  │ -80%     │  │  here for human review      │  │  ║
║  │  │ Goal     │  │ Hour bids│  │  before deploying           │  │  ║
║  │  │ alignment│  │ Geo bids │  │                             │  │  ║
║  │  └──────────┘  └──────────┘  └─────────────────────────────┘  │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
║            │                │                    │                   ║
║            ▼                ▼                    ▼                   ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │  LAYER 3: EXECUTION               Cadence: Daily              │  ║
║  │  (Current agent, enhanced)                                     │  ║
║  │                                                                │  ║
║  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  ║
║  │  │  Copy    │  │ Negative │  │ Keyword  │  │ Search Term  │  │  ║
║  │  │ Optimizer│  │ Keyword  │  │ Manager  │  │ Miner        │  │  ║
║  │  │ (v1 core)│  │ Engine   │  │          │  │              │  │  ║
║  │  │          │  │          │  │ Expansion│  │ Convert →    │  │  ║
║  │  │ RSA A/B  │  │ Auto-    │  │ from     │  │   keywords   │  │  ║
║  │  │ Headline │  │ detect   │  │ search   │  │ Waste →      │  │  ║
║  │  │ testing  │  │ waste    │  │ terms    │  │   negatives  │  │  ║
║  │  │ Desc     │  │ Campaign │  │ Match    │  │ Gaps →       │  │  ║
║  │  │ testing  │  │ + ad grp │  │ type opt │  │   intel L1   │  │  ║
║  │  │ DKI pres │  │ scoping  │  │ QS-based │  │              │  │  ║
║  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
║            │                │                    │                   ║
║            ▼                ▼                    ▼                   ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │  LAYER 4: MEASUREMENT              Cadence: Continuous        │  ║
║  │                                                                │  ║
║  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  ║
║  │  │ Snapshot │  │Experiment│  │  Alert   │  │  KB Writer   │  │  ║
║  │  │ Engine   │  │ Tracker  │  │  System  │  │              │  │  ║
║  │  │          │  │          │  │          │  │ Ingest       │  │  ║
║  │  │ Daily    │  │ Score at │  │ CR drop  │  │ snapshots →  │  │  ║
║  │  │ snapshots│  │ 150 clk  │  │ > 20%    │  │ wiki pages   │  │  ║
║  │  │ Trend    │  │ Winner / │  │ CPA 2x   │  │ Update       │  │  ║
║  │  │ detection│  │ loser    │  │ Budget   │  │ entities +   │  │  ║
║  │  │ Anomaly  │  │ tracking │  │ exhaust  │  │ learnings    │  │  ║
║  │  │ flagging │  │ Learning │  │ QS decay │  │ Run lint     │  │  ║
║  │  │          │  │ extract  │  │ Comp.    │  │ every 5      │  │  ║
║  │  │          │  │          │  │ entry    │  │ cycles       │  │  ║
║  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
║                                                                      ║
║  ┌────────────────────────────────────────────────────────────────┐  ║
║  │                    MCP INTERFACE LAYER                         │  ║
║  │                                                                │  ║
║  │  Google Ads R/W: search · get_ad · create_rsa · pause_ad ·    │  ║
║  │    create_variation · add_negative · add_keyword ·             │  ║
║  │    adjust_bid · set_budget · create/pause_campaign             │  ║
║  │                                                                │  ║
║  │  Ahrefs: keyword_vol · competitor_kw · serp · domain_rating   │  ║
║  │                                                                │  ║
║  │  Proxy: competitor_ads · ad_transparency · live_serp           │  ║
║  └────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════╝
```
---

## Layer Details

### Layer 1: Intelligence (Weekly / On-Demand)

**What it does**: Gathers external signals the agent can't get from Google Ads alone.

| Component | Input | Output | MCP Tools |
|-----------|-------|--------|-----------|
| **Competitive Monitor** | Competitor domains list | Ad copy database, messaging trends, spend estimates | Proxy MCP: `competitor_ads`, `ad_transparency` |
| **Keyword Explorer** | Seed keywords + gaps from L3 | Ranked keyword opportunities (vol, CPC, KD, intent) | Ahrefs MCP: `keyword_volume`, `competitor_keywords` |
| **Market Signal Tracker** | Category terms, SERP data | Trend reports, new entrant alerts, seasonal patterns | Ahrefs MCP: `serp`, `organic_traffic` |

**Key rule**: Intelligence never deploys anything. It writes findings to the Knowledge Base. Strategy reads them.

**Example cycle output**:
```
[2026-05-07] Intelligence Run
- Cognition (Devin) launched 12 new Google Ads (was 2). Alert: competitive entry.
- "agentic software development" volume up 40% MoM (100 → 140). Category growing.
- New keyword found: "ai dev ops platform" — 800 vol, $4.50 CPC, KD=22. Recommend Segment 3.
- Cursor shifted messaging from "AI editor" to "AI-native IDE" — positioning convergence.
→ Written to: knowledge-base/competitive/2026-05-07.md
→ Written to: knowledge-base/entities/keywords.md (3 new entries)
```

### Layer 2: Strategy (Weekly / Bi-Weekly — HUMAN REVIEW REQUIRED)

**What it does**: Makes structural decisions that affect account architecture. Every output goes through a review gate before deployment.

| Component | Reads From | Proposes | Impact |
|-----------|-----------|----------|--------|
| **Budget Allocator** | Snapshot data, IS%, CR by campaign | Budget shifts between campaigns | HIGH — wrong allocation wastes $1K+/day |
| **Campaign Architect** | Keyword groups, audience segments | New campaigns, pause underperformers | HIGH — structural changes |
| **Audience Builder** | Custom Segment perf, In-Market data | New segments, suppression updates | MEDIUM — audience changes |
| **Bidding Optimizer** | CPA trends, conversion volume | Strategy shifts (Manual → tCPA) | HIGH — bidding affects every auction |
| **Conversion Config** | Goal alignment, conv action data | Primary/secondary designation | CRITICAL — wrong setup poisons Smart Bidding |
| **Device/Schedule Adj** | Device CR, hour-of-day data | Bid modifiers | MEDIUM — incremental |

**Review Gate**: Strategy generates a proposal doc (markdown), not API calls. Human approves/rejects/modifies before anything touches the account.

```
┌─────────────────────────────────────────────┐
│  STRATEGY PROPOSAL — Week of 2026-05-12     │
│                                             │
│  1. Shift $2K/day from C5 → Brand (IS 10%) │
│     Confidence: HIGH (Brand CR 30% vs 1%)   │
│     Risk: LOW                               │
│                                             │
│  2. Create Segment 1 campaign (Agentic)     │
│     Keywords: 8 terms, avg KD=12            │
│     Est. budget: $400/day                   │
│     Confidence: MEDIUM (new category)       │
│     Risk: MEDIUM                            │
│                                             │
│  3. Switch C8 to tCPA at $75               │
│     Requires: 30+ conversions/30d (have 34) │
│     Confidence: HIGH                        │
│     Risk: MEDIUM (2-week learning period)   │
│                                             │
│  [ ] APPROVE ALL                            │
│  [ ] APPROVE 1, 3 — REJECT 2               │
│  [ ] REJECT ALL — ADD NOTES                │
└─────────────────────────────────────────────┘
```

### Layer 3: Execution (Daily — Autonomous Within Guardrails)

**What it does**: The current v1 agent, enhanced with keyword management and search term mining. Runs daily without human approval, but within defined guardrails.

| Component | v1 Status | v2 Enhancement |
|-----------|-----------|---------------|
| **Copy Optimizer** | ✅ Working | Add DKI preservation rules, segment-matched messaging |
| **Negative Keyword Engine** | ✅ Working | Auto-detect from search terms, campaign+ad group scoping |
| **Keyword Manager** | ❌ New | Expand from search term reports, match type optimization, QS-based prioritization |
| **Search Term Miner** | ❌ New | Convert high-CR search terms → keywords, waste → negatives, gaps → Intelligence requests |

**Guardrails (autonomous limits)**:
- Can add/pause ad copy ✅
- Can add negative keywords ✅
- Can add keywords (up to 10/day, broad match excluded) ✅
- Cannot change budgets ❌ (→ Strategy)
- Cannot change bidding strategy ❌ (→ Strategy)
- Cannot create/pause campaigns ❌ (→ Strategy)
- Cannot modify conversion actions ❌ (→ Strategy)

### Layer 4: Measurement (Continuous)

**What it does**: Monitors everything, scores experiments, triggers alerts, and writes learnings back to the Knowledge Base.

| Component | Trigger | Action |
|-----------|---------|--------|
| **Snapshot Engine** | Daily (post-execution) | Pull full account snapshot, store in `sources/snapshots/` |
| **Experiment Tracker** | At 150 clicks per variant | Score winner/loser, update `experiments.jsonl`, extract learning |
| **Alert System** | Threshold breach | Notify: CR drop >20%, CPA spike >2×, budget exhaustion, QS decay, new competitor |
| **KB Writer** | Every 5 cycles | Ingest snapshots into wiki pages, update entities, run knowledge lint |

---

## MCP Tools Required

### Currently Available
| Tool | Layer | Status |
|------|-------|--------|
| `google_ads_search` | L3, L4 | ✅ Active |
| `google_ads_get_ad` | L3 | ✅ Active |
| `google_ads_create_rsa` | L3 | ✅ Active |
| `google_ads_pause_ad` | L3 | ✅ Active |
| `google_ads_create_variation` | L3 | ✅ Active |
| `google_ads_add_negative` | L3 | ✅ Active |
| `google_ads_add_keyword` | L3 | ✅ Available (unused) |

### Needed for v2
| Tool | Layer | Priority | Notes |
|------|-------|----------|-------|
| `google_ads_adjust_bid` | L2 | P1 | Bid modifiers for device/schedule/audience |
| `google_ads_set_budget` | L2 | P1 | Campaign budget changes |
| `google_ads_create_campaign` | L2 | P2 | New campaign creation |
| `google_ads_pause_campaign` | L2 | P2 | Campaign pause/enable |
| `google_ads_set_conversion_action` | L2 | P0 | Primary/secondary designation |
| `google_ads_get_search_terms` | L3 | P1 | Search term report for mining |
| `ahrefs_keyword_volume` | L1 | P1 | Keyword research |
| `ahrefs_competitor_keywords` | L1 | P2 | Competitive keyword gaps |
| `proxy_competitor_ads` | L1 | P1 | Live competitor ad monitoring |

---

## Implementation Roadmap

### Phase 1: Enhanced Execution (Weeks 1-2) — LOW RISK
Upgrade the v1 agent without changing its scope:
- Add `add_keyword` to daily cycle (from search term winners)
- Add search term mining step (pull search terms → classify → act)
- Add KB Writer (auto-update knowledge base every 5 cycles)
- Add experiment scoring at 150 clicks
- **Effort**: Config changes + 2 new program.md steps
- **Risk**: Same guardrails as v1

### Phase 2: Measurement Layer (Weeks 3-4) — LOW RISK
Add monitoring without touching the account:
- Build snapshot engine (daily pull → structured storage)
- Build alert system (threshold-based notifications)
- Build trend detection (week-over-week comparisons)
- **Effort**: New measurement cycle (runs post-execution)
- **Risk**: Read-only — can't break anything

### Phase 3: Intelligence Layer (Weeks 5-8) — LOW RISK
Add external research without touching the account:
- Connect Ahrefs MCP for keyword research
- Connect Proxy MCP for competitor monitoring
- Build weekly intelligence cycle
- Write findings to Knowledge Base
- **Effort**: New weekly cycle + MCP integrations
- **Risk**: Read-only external APIs

### Phase 4: Strategy Layer (Weeks 9-12) — MEDIUM RISK (human-gated)
Add structural optimization with human review:
- Build budget allocation proposals
- Build campaign architecture proposals
- Build audience segment proposals
- All proposals go through review gate
- **Effort**: Proposal generation + review UI/workflow
- **Risk**: Medium — but human review gate catches errors

---

## What Changes vs What Stays

| Aspect | v1 (Current) | v2 (Proposed) |
|--------|-------------|--------------|
| Daily cycle | Steps 0-9, copy + negatives | Steps 0-12, copy + negatives + keywords + search terms |
| Levers touched | 2 of 11 | 9 of 11 (with human gate on 7) |
| External intel | None | Ahrefs + Proxy MCP weekly |
| Memory | Flat learnings.md | LLM Wiki (entities, concepts, cross-refs) |
| Campaigns covered | 8 of 19 | All active campaigns |
| Human involvement | Post-hoc review | Pre-deployment review gate on structural changes |
| Measurement | Manual snapshot checks | Automated alerts + trend detection |
| Knowledge compounding | Linear (append-only) | Networked (cross-referenced, versioned) |

---

## Cross-References
- [Account Audit](01-account-audit.md) — current performance baseline
- [Google Ads Architecture](02-google-ads-architecture.md) — lever map and formulas
- [Audience Strategy (Cosmos)](audience-strategy-cosmos.md) — audience segments this system will manage
- [Learnings](learnings.md) — heuristics baked into decision rules
