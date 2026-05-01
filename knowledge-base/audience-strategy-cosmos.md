# Cosmos — Audience Targeting & Strategy (Full Recommendation)
**Last updated**: 2026-05-01 | **Status**: Final v1
**Sources**: Account performance data (8 cycles) + Ahrefs keyword research + Proxy MCP competitor intel + Google Ads Transparency Center

---

## Executive Summary

The current account has 44 audience lists with no strategy, no suppression, and no segmentation. We're spending $344K to reach "anyone who searches our keywords" — and the data shows this is failing: non-brand CPA is $143, mobile CR is 0.5%, and 3 ad groups have never converted despite 250+ combined clicks ($2,600 wasted).

This proposal replaces the graveyard with a **6-segment audience architecture** informed by:
- **Our own data**: 8 cycles of experiment learnings, QS analysis, device/hourly performance
- **Ahrefs**: 20 keywords mapped by volume, CPC, difficulty, and intent
- **Proxy MCP**: Live competitor ad intelligence (Cursor 40 ads, Replit 40, Claude 40, Devin 2)
- **URL library**: 31 competitor/adjacent URLs with traffic data for Custom Segment seeding

**Core thesis**: System-buyers, not seat-buyers. Cosmos sells to whoever is responsible for the agentic SDLC at the org level — not individual developers shopping for a coding tool.

---

## What Our Own Data Tells Us About Audience

### Signal 1: "3 failed ads = audience problem, not copy" (Rule #8)
ralph (3 ads, 115 clicks, 0 conv), gastown_ai (3 ads, 31 clicks, 0 conv), coding_agent (3 ads, 0 conv). **When copy fails 3x in a row, the audience is wrong.** This is the strongest evidence that targeting matters more than creative at this stage.

### Signal 2: Desktop converts 8x mobile (4.0% vs 0.5%)
Our buyer searches on desktop. Mobile is $319/mo in near-pure waste. **Action**: -80% mobile bid adjustment on all non-brand campaigns.

### Signal 3: Natural capability framing wins, generic AI language loses
- ✅ "Run Agents in Git Worktrees" → 8.7% CR
- ✅ "No More Pasting Into Prompts" → 8.33% CR
- ❌ "One App for AI Development" → 445 clicks, 0 conv
- ❌ "Free with Claude Code Sub" → 972 clicks, 0 conv

**Implication for audiences**: We need to reach people who understand what "agent orchestration" and "worktrees" mean — technical buyers, not casual browsers. Generic AI audiences will waste budget.

### Signal 4: Price-first messaging never converts (Rule #1)
972/0, 437/0, 56/0 across price-first headlines. **Implication**: Suppress free-tier seekers and student audiences aggressively. The "free" negative keyword alone could save hundreds/mo.

### Signal 5: Brand keywords have 30% CR at $2.40 CPA
"augment code intent" converts at 30.3% in NAM, 29.4% in EMEA. Brand is the single best traffic source but is budget-starved (10% IS). **Implication**: Branded audience segment + maximum budget.

### Signal 6: Evening hours (7-9 PM) have 8.7% CR
Low volume but highest conversion rate. These are senior engineers/leaders browsing after work. **Implication**: Ad schedule bid boost during peak windows.

---

## The 6 Custom Segments (Build in Google Ads)

These are the primary targeting mechanism. Each combines search keywords + competitor URLs to create a precise audience signal.

### Segment 1: Cosmos – Agentic Dev Buyers (Core)
**Who**: Engineers actively searching for agentic coding tools. Highest commercial intent.
**Why**: "agentic software development" has KD=2 and "ai sdlc" has KD=1 — near-zero competition. Cosmos can own these category terms before incumbents pivot.

| Keywords | URLs |
|----------|------|
| agentic software development, agentic ai coding, ai coding agent, autonomous coding agent, ai software engineer, autonomous software development, llm agents for coding, background agents, ai agent for developers, ai sdlc, agentic sdlc, ai dev tools, ai engineering agent, autonomous dev agent | cognition.ai, cognitionlabs.com, factory.ai, devin.ai, sweep.dev, aider.chat, continue.dev, all-hands.dev, cursor.com/cli, cursor.com/bugbot, claude.com/claude-code |

**Deploy to**: Search (high CPC, exact intent) + YouTube + Demand Gen
**Data backing**: "coding agent" (600 vol, KD=39), "ai software engineer" (1.7K vol, $7 CPC, KD=48) — commercial intent keywords our account hasn't tested yet.

### Segment 2: Cosmos – Competitor Evaluators
**Who**: People mid-evaluation comparing AI coding tools. Catch them with system-level reframing.
**Why**: This is where volume lives — "cursor ai" (96K), "claude code" (200K), "github copilot" (112K). But our account proves you can't just bid on competitor names blindly (ralph = 0 conv ever). The difference: pair competitor keywords with comparison-intent signals.

| Keywords | URLs |
|----------|------|
| cursor vs claude code, cursor vs copilot, devin vs cursor, claude code vs cursor, best ai coding agent, ai coding tools comparison, devin alternatives, cursor alternatives, github copilot alternatives, best ai pair programmer, ai coding tool review | cursor.com/pricing, cursor.com, github.com/features/copilot, cognition.ai, devin.ai, replit.com/ai, claude.com/claude-code, factory.ai, codeium.com, windsurf.com, qodo.ai |

**Deploy to**: Search (branded competitor) + Demand Gen
**Data backing**: Our Claude Mac campaign converts at 8.6% CR with 38 conv/mo — proof that competitor conquest *can* work when intent matches. The key is cursor.com/pricing visitors (7,867 US traffic) = high commercial intent signal.
**Learning from our failures**: ralph (0 conv, 115 clicks) and gastown_ai (0 conv, 31 clicks) prove that not all competitor keywords convert. Use comparison-intent ("vs", "alternatives", "best") not just brand names.

### Segment 3: Cosmos – Platform & DevEx Leaders
**Who**: Buyers, not users. They search for org-wide tooling, internal platforms, developer productivity. Higher LTV.
**Why**: This is the Cosmos buyer persona — the person who decides to adopt an agent OS for the team. Entirely missing from current targeting.

| Keywords | URLs |
|----------|------|
| developer productivity tool, internal developer platform, idp platform, developer experience platform, ai for engineering teams, engineering velocity tool, ai code review tool, automated code review platform, developer platform engineering, platform engineering tools, ci/cd ai, automated software delivery | atlassian.com/software, about.gitlab.com, github.com/enterprise, harness.io, cortex.io, backstage.io, lineardev.com, port.io, jetbrains.com/teamcity |

**Deploy to**: Search + Demand Gen + YouTube
**Data backing**: "ai code review" (1.2K vol, $4 CPC, KD=57) maps to this segment. These are platform buyers with budget authority — the LTV per conversion should be 5-10x an individual dev signup.
**Account heuristic**: Our "augment_intent" keyword (30% CR) proves that high-intent, lower-volume keywords dramatically outperform high-volume generic ones. Platform keywords follow the same pattern.

### Segment 4: Cosmos – Agent Builders & ML Engineers
**Who**: Engineers building agents themselves — most likely to immediately understand the OS-for-agents pitch.
**Why**: These people already use LangChain, CrewAI, LlamaIndex. They know the pain of fragmented agent infra. Cosmos solves their problem directly.

| Keywords | URLs |
|----------|------|
| build ai agent, agent framework, langchain alternative, llm orchestration, ai agent platform, multi agent system, agent runtime, agent memory, agentic workflow, ai workflow automation, llm agent platform, ai agent infrastructure | langchain.com, docs.crewai.com, llamaindex.ai, autogen.dev, together.ai, e2b.dev, modal.com, daytona.io, runpod.io |

**Deploy to**: Search + Display retargeting + YouTube tech channels
**Data backing**: "ai agent platform" (1.3K vol, $7 CPC, KD=29) — high CPC signals commercial intent with low difficulty. "llm agents" (1K vol, $2 CPC, KD=45) and "multi agent systems" (800 vol, $3.50, KD=49) are directly in the Cosmos sweet spot.
**Account heuristic**: Our "orchestration" ad group shows CTR improved but volume is low (18 clicks, 0 conv). Agent Builders segment would dramatically expand reach for this intent.

### Segment 5: Cosmos – Eng Leadership (VP/CTO)
**Who**: Top-of-funnel awareness for technical buyers making the agentic-SDLC bet.
**Why**: These are the budget holders. They read a16z, Thoughtworks, Martin Fowler. They're thinking about "ai transformation" at the org level. Cosmos is the answer to their strategic question.

| Keywords | URLs |
|----------|------|
| future of software development, ai transformation engineering, agentic ai for enterprise, ai engineering strategy, cto ai strategy, autonomous engineering, agent ops, ai workforce engineering, ai engineering roi, engineering productivity ai, scaling engineering with ai | mckinsey.com/capabilities/quantumblack, a16z.com/ai, gartner.com/en/information-technology, thoughtworks.com, stackoverflow.blog, martinfowler.com, increment.com, ben-evans.com |

**Deploy to**: YouTube (CTO podcasts) + Demand Gen
**Data backing**: "agentic ai" (94K vol, $7 CPC, KD=72) is the category keyword — high volume, high CPC, high difficulty. We won't win Search on this term, but YouTube/Demand Gen with this audience segment is viable and cheaper.
**Account heuristic**: Evening hours (7-9 PM) have 8.7% CR — this aligns with senior leaders browsing after work. Layer ad schedule boost on this segment.

### Segment 6: Cosmos – Branded & Existing Awareness
**Who**: People who already know Cosmos / Augment / Poseidon.
**Why**: Brand is our best-performing traffic (30% CR on "augment code intent", $0.94 CPC, QS 10). Starving it is the biggest budget mistake in the account.

| Keywords | URLs |
|----------|------|
| cosmos ai, cosmos agent platform, augment code, augment cosmos, poseidon dev tool, poseidon agent, augmentcode cosmos | augmentcode.com, augmentcode.com/cosmos, augmentcode.com/poseidon |

**Deploy to**: Search (branded, low CPC) + Display retargeting
**Data backing**: Brand IS is 10% — we're losing 90% of brand searches. At QS 10 and $0.94 CPC, every dollar here is 19x more efficient than competitor keywords at QS 3 ($18.28 CPC).

---

## Google In-Market & Affinity Layers

**Rule: NEVER use as primary targeting. Always layer on top of Custom Segments. Start as observation for 14 days, then bid-adjust winners.**

### Positive Layers (Observation → Bid Boost)

| Type | Audience | Layer On | Rationale |
|------|----------|----------|-----------|
| In-Market | Business Software | All campaigns | Broad B2B software buyer qualifier |
| In-Market | Cloud Computing | Search + Demand Gen | Platform teams overlap |
| In-Market | Software Dev & Eng Jobs | YouTube + Demand Gen | Hiring = infra investment signal |
| In-Market | Computers & Peripherals > Software | Display + YouTube | Broader software buyer pool |
| Affinity | Tech News | YouTube + Demand Gen | Eng leaders + early adopters |
| Affinity | Software & App Enthusiasts | YouTube + Display | Tool-curious developers |
| Affinity | Business Professionals | Demand Gen | Layer with In-Market for VP/CTO |
| Affinity | Avid Investors | Demand Gen | Funded startup proxy |
| Detailed Demo | Industry > Technology | All campaigns | Self-reported tech — positive bid |
| Detailed Demo | Company Size > Large (1,000+) | Search + Demand Gen | Enterprise platform buyers |

### Negative Layers (Exclude Immediately)

| Type | Audience | Why |
|------|----------|-----|
| In-Market | Education > CS & Software Engineering | Students — kill spend |
| Detailed Demo | Parental Status: Has Children | Soft B2C noise signal |
| Affinity | Avid News Readers > Lifestyles | Off-topic consumption |

---

## Suppression Framework (Apply Day 1)

Currently zero suppression exists. This means we're paying to show ads to existing customers.

| Audience | Source | Apply To | Priority |
|----------|--------|----------|----------|
| **Existing customers** | CRM upload (refresh monthly) | Exclude from ALL acquisition campaigns | P0 |
| **Active trial users** | GA4 event: "User Signed Up" last 30d | Exclude from ALL except branded retargeting | P0 |
| **Pricing page converters** | GA4 event: "Credit Card Added" | Exclude from ALL | P0 |
| **Job applicants** | Careers page visitors or CRM tag | Exclude from ALL | P1 |

**Estimated savings**: If even 2% of current clicks are existing customers, that's ~$400/mo in wasted acquisition spend.

---

## Negative Keywords — Full Exclusion List

Grounded in our account data (price-first = 0 conv across 1,465 clicks, Rule #1) + external research:

### From Our Account (Proven Wastes — Already Deployed)
| Keyword | Match | Monthly Waste | Status |
|---------|-------|--------------|--------|
| what is | Phrase | ~$52/mo | Deployed C5 |
| process automation | Phrase | ~$12/mo | Deployed C5 |
| claude code plans | Exact | ~$122/mo | Deployed C5 |
| claude managed agents | Phrase | ~$74/mo | Deployed C7 |
| claude coworker | Phrase | ~$95/mo | Deployed C8 |

### New — Intent Mismatches
| Keyword | Match | Reasoning |
|---------|-------|-----------|
| free | Phrase | Price-first never converts (972/0, 437/0 in our data) |
| tutorial | Phrase | Educational intent — not buying |
| course, udemy, coursera | Exact | Education platforms |
| youtube | Exact | Tutorial seekers |
| homework, assignment, for kids | Exact | Students |
| beginner, hobby | Exact | Non-professional |

### New — Wrong Vertical ("agent" dilution)
| Keyword | Match | Reasoning |
|---------|-------|-----------|
| real estate agent, insurance agent, travel agent | Phrase | "Agent" dilution |
| ai girlfriend, ai influencer | Exact | Adversarial noise |
| resume builder | Exact | Wrong vertical |

### New — Wrong Product Category
| Keyword | Match | Reasoning |
|---------|-------|-----------|
| vibe coding | Phrase | Replit-owned, consumer space (88K vol) |
| no code, no-code, low code, low-code | Exact | Different market |
| ai chatbot, chatgpt for coding | Phrase/Exact | Chat ≠ agentic SDLC |
| github desktop | Exact | App install, not platform |

### Placement Exclusions
| Placement | Why |
|-----------|-----|
| youtube.com/results?search=tutorial | Tutorial seekers |
| Mobile app categories: Games | Wrong context for B2B |


---

## Competitive Positioning by Segment

Based on live Google Ads intel (April 30, 2026):

| Competitor | Their Play | Our Counter | Where to Fight |
|-----------|-----------|-------------|---------------|
| **Cursor** (40 ads, text-heavy) | Bidding hard on "cursor ai" (96K vol) defensively + "ai code editor" offensively | System-level reframing: "You don't need another editor — you need an OS for the fleet." URL-target cursor.com/pricing visitors | Segments 1, 2, 4 |
| **Anthropic/Claude** (40 ads, heavy video) | Massive brand budget pushing Claude Code as CLI agent | Agent fleet vs single agent: "Claude Code is one agent. Cosmos runs the fleet." | Segments 2, 4 |
| **Replit** (40 ads, mixed format) | Pivoted to "vibe coding" (88K vol) + "AI app builder" | Don't compete — different market (consumer/prosumer). Block "vibe coding" as negative keyword | Negative keyword only |
| **Devin/Cognition** (2 ads only) | Surprisingly light Google paid. PR/LinkedIn focused | **Major opportunity** — dominate Google paid in "autonomous SWE" space before Cognition invests | Segments 1, 5 |

**The gap**: Cognition (Devin) is Cosmos's closest *positioning* competitor (both sell autonomous software engineering) but has almost zero Google Ads presence. First-mover advantage on "autonomous coding agent" (40 vol, KD=low), "ai software engineer" (1.7K vol), and "agentic software development" (100 vol, KD=2).

---

## Rollout Plan

### Week 1: Foundation (Zero-Risk)
- [ ] Fix conversion actions — set only "Customer Created" as primary
- [ ] Build suppression lists (customers, active trials, applicants)
- [ ] Apply suppression to ALL campaigns
- [ ] Deploy full negative keyword list (25+ terms)
- [ ] Set mobile bid adjustment -80% on all non-brand campaigns
- [ ] Pause YouTube campaigns ($7.5K/mo → $0)
- [ ] Increase brand budget to $400/day combined

### Week 2: Segment Build (Setup Only)
- [ ] Build all 6 Custom Segments in Google Ads Audience Manager
- [ ] Add In-Market/Affinity audiences as **observation only** on top campaigns
- [ ] Add Detailed Demographics (Industry: Tech, Company Size: 1,000+) as observation
- [ ] Add audience exclusions (CS Education, Parental: Has Children)
- [ ] Refresh CRM list upload
- [ ] Set ad schedule bid boost +30% for 7-9 PM

### Week 3-4: Signal Collection
- [ ] Monitor audience observation data — which segments show CTR/CR lift?
- [ ] Build remarketing funnel segments (docs readers, pricing visitors, trial starters)
- [ ] Create first Cosmos-specific Search campaign targeting Segment 1 keywords
- [ ] A/B test system-level messaging vs tool-level messaging on Segment 2

### Week 5-6: Activation
- [ ] Audiences with statistically significant lift → switch to targeting mode with positive bid adjustments
- [ ] Launch Demand Gen campaign targeting Segments 3 + 5 (platform buyers + eng leadership)
- [ ] Build lookalikes from refreshed CRM seed
- [ ] Launch YouTube campaign targeting Segment 5 with CTO/VP eng content

### Week 7+: Optimization
- [ ] Score audience performance, pause underperformers
- [ ] Expand winning Custom Segments with new keywords from search term reports
- [ ] Layer winning In-Market/Affinity audiences onto high-performing Custom Segments
- [ ] Feed learnings back to Knowledge Base

---

## Budget Allocation by Segment

| Segment | Channel | Monthly Budget | % of Total | Expected CPA |
|---------|---------|---------------|-----------|-------------|
| Seg 6: Branded | Search | $12,000 | 17% | $5-15 (proven) |
| Seg 2: Competitor Evaluators | Search + Demand Gen | $18,000 | 26% | $100-200 (based on Claude Mac) |
| Seg 1: Agentic Dev Buyers | Search + YouTube | $12,000 | 17% | $50-150 (low KD, high intent) |
| Seg 4: Agent Builders | Search + Display | $8,000 | 12% | $75-200 (new, test) |
| Seg 3: Platform & DevEx | Search + Demand Gen | $8,000 | 12% | $100-300 (high LTV) |
| Seg 5: Eng Leadership | YouTube + Demand Gen | $5,000 | 7% | $200-500 (awareness) |
| Display Remarketing | Display | $3,000 | 4% | $18-30 (proven) |
| Buffer / Testing | — | $3,000 | 4% | — |
| **Total** | | **$69,000** | **100%** | |

---

## Measurement Framework

### Primary Metrics (Weekly Review)
| Metric | Baseline | Week 4 Target | Week 8 Target |
|--------|----------|--------------|--------------|
| Blended CR | 1.19% | 3% | 5% |
| Non-brand CPA | $143 | $100 | $75 |
| Brand IS | 10% | 50% | 80% |
| Waste spend (YouTube + mobile + 0-conv groups) | $14K/mo | $2K/mo | $500/mo |
| Audience-attributed conversions | 0% | 15% | 40% |

### Per-Segment Scoring (Bi-Weekly)
| Metric | Kill Threshold | Scale Threshold |
|--------|---------------|----------------|
| CR | <0.5% after 500 clicks | >3% after 200 clicks |
| CPA | >3× segment target | <1.5× segment target |
| CTR | <1% on Search | >4% on Search |
| In-Market lift | <10% CTR lift vs no audience | >25% CTR lift |

### Decision Rules
1. **Kill**: Any segment with <0.5% CR after 500+ clicks. Don't iterate on copy — it's an audience problem (Rule #8).
2. **Scale**: Any segment with >3% CR after 200+ clicks → increase budget 50%, expand match types.
3. **Investigate**: Any segment with high CTR but low CR → landing page mismatch (Rule #7: CTR ≠ CR).
4. **Never touch**: Brand (Segment 6) performs at 30% CR. Don't experiment, just fund it.

---

## Key Insight: Why This Will Work

The old strategy targeted **individual developers** searching for **coding tools** — a crowded space where Cursor has 40 active ads and 96K monthly searches on their brand alone.

The new strategy targets **6 distinct buyer segments** across **3 levels of intent**:
- **Bottom-funnel** (Segments 1, 2, 6): People actively searching for agent platforms or comparing tools
- **Mid-funnel** (Segments 3, 4): People building agent systems or evaluating platform infrastructure
- **Top-funnel** (Segment 5): Engineering leaders thinking about agentic transformation

Each segment gets matched messaging, matched landing pages (when built), and matched bid strategy. No more one-size-fits-all.

The data supports this shift:
- Our best-performing keyword ("augment code intent") has 30% CR at 50 clicks/mo — proof that intent quality > volume
- "agentic software development" has KD=2 and "ai sdlc" has KD=1 — we can own these category terms
- Cognition (Devin) has only 2 Google Ads vs our 25 — first-mover advantage in the "autonomous SWE" paid space
- Our proven heuristics (natural framing > keyword stuffing, 3 failures = audience problem, price-first fails) are baked into every segment recommendation

---

## Cross-References
- [Account Audit](01-account-audit.md) — current performance data driving these recommendations
- [Product Positioning](03-product-positioning.md) — Cosmos positioning, safe claims, competitor context
- [Google Ads Architecture](02-google-ads-architecture.md) — how audiences interact with the auction system
- [Executive Audit](executive-audit.md) — leadership summary