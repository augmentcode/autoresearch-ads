# Knowledge Base — Schema & Operations Guide
**Purpose**: This file tells the autoresearch-ads agent how the knowledge base is structured, how to navigate it, and how to maintain it across runs.

---

## Architecture

```
knowledge-base/
├── KNOWLEDGE.md          ← YOU ARE HERE. Schema + operations guide.
├── index.md              ← Content catalog. Read this FIRST on every run.
├── log.md                ← Chronological record of all KB updates.
│
├── sources/              ← Raw, immutable source data
│   ├── snapshots/        ← MCP query snapshots (daily archives)
│   ├── retro/            ← Account audits, retros, raw MCP dumps
│   └── external/         ← Competitor data, keyword research, market intel
│
├── entities/             ← Pages for specific things (campaigns, ad groups, keywords)
│   ├── campaigns.md      ← All campaign entities + status + performance
│   ├── ad-groups.md      ← All ad group entities + tier classification
│   ├── keywords.md       ← Keyword inventory + QS + match types
│   ├── audiences.md      ← Audience list inventory + usage status
│   └── conversion-actions.md  ← Conversion tracking setup
│
├── concepts/             ← How things work (reference material)
│   ├── google-ads-architecture.md  ← System flow, auction mechanics, formulas
│   ├── quality-score.md  ← QS components, impact on CPC, improvement levers
│   ├── bidding-strategies.md  ← Manual CPC vs Smart Bidding, when to use each
│   ├── rsa-mechanics.md  ← RSA creation, immutability, pinning, A/B testing
│   └── match-types.md    ← Exact vs Phrase vs Broad, negative match logic
│
├── strategy/             ← Synthesized analysis and plans
│   ├── product-positioning.md  ← What we sell, safe claims, competitor context
│   ├── account-audit.md  ← Full account audit with findings
│   ├── budget-allocation.md  ← Current vs recommended budget splits
│   ├── campaign-plan.md  ← New campaign architecture for Cosmos pivot
│   └── audience-strategy.md  ← Audience building plan for AI transformation
│
├── learnings/            ← Compounding experimental knowledge
│   ├── rules.md          ← Proven rules derived from ≥3 data points
│   ├── winners.md        ← What works (with data)
│   ├── losers.md         ← What fails (with data)
│   ├── hypotheses.md     ← Active hypotheses being tested
│   └── patterns.md       ← Headline/description patterns + CR data
│
└── competitive/          ← Competitive intelligence
    ├── keyword-landscape.md  ← What competitors bid on, gaps
    └── market-context.md     ← Industry trends, category dynamics
```

---

## Three Layers

### 1. Raw Sources (`sources/`)
Immutable. The agent reads from these but NEVER modifies them.
- MCP snapshots archived daily → `sources/snapshots/snapshot-YYYY-MM-DD.json`
- Raw MCP query dumps → `sources/retro/`
- External research → `sources/external/`

### 2. The Wiki (everything else)
Agent-maintained. The agent creates, updates, and cross-references these pages.
Every page should have:
- A `## Last Updated` line with date and context
- Cross-references to related pages using relative links: `[see Quality Score](concepts/quality-score.md)`
- Data citations: when citing a number, note the source date: `(source: snapshot 2026-04-27)`

### 3. This Schema (`KNOWLEDGE.md`)
Co-evolved by human and agent. Defines structure, conventions, and operations.

---

## Operations

### INGEST — Processing new data
Triggered when: new MCP snapshot arrives, new source is added, or agent completes a cycle.

1. Read the new source
2. Read `index.md` to understand current KB state
3. Update relevant entity pages (campaigns, ad groups, keywords)
4. Update relevant strategy pages if findings change analysis
5. Update `learnings/` if new experiment results are available
6. Flag contradictions: if new data contradicts existing wiki pages, note it explicitly
7. Update `index.md` with any new/changed pages
8. Append entry to `log.md`

**One source may touch 5-15 wiki pages.** This is expected and desired.

### QUERY — Answering questions
Triggered when: human asks a question about the account, strategy, or performance.

1. Read `index.md` to find relevant pages
2. Read those pages
3. Synthesize answer with citations to specific wiki pages
4. If the answer produces valuable new analysis, file it as a new wiki page
5. Append query + answer summary to `log.md`

### LINT — Health check
Triggered periodically (every 5 cycles or on request).

Check for:
- Stale data: pages citing snapshots older than 14 days
- Contradictions: entity pages that conflict with latest snapshot
- Orphan pages: pages with no inbound links from index or other pages
- Missing pages: concepts or entities mentioned but lacking their own page
- Data gaps: areas where a new MCP query would fill a hole

---

## Conventions

### Page format
```markdown
# Page Title
**Last updated**: YYYY-MM-DD | **Source**: [snapshot/retro/analysis]

## Summary
One paragraph TL;DR.

## Content
Main content with data tables, analysis, etc.

## Cross-References
- [Related Page 1](path/to/page.md)
- [Related Page 2](path/to/page.md)

## Open Questions
- Things we don't know yet that matter
```

### Naming
- Filenames: `kebab-case.md`
- Entity names: match Google Ads naming (campaign names, ad group names as-is)
- Dates: always YYYY-MM-DD

### Data citation
When citing a metric, always include:
- The value
- The date range
- The source: `(snapshot 2026-04-27)` or `(MCP query 2026-05-01)` or `(retro all-time)`

### Cross-referencing
- Every page should link to at least 2 other pages
- Use relative paths: `[text](../concepts/quality-score.md)`
- When updating a page, check if other pages need updating too

---

## Agent Startup Sequence

On every new run/cycle, the agent should:
1. Read `KNOWLEDGE.md` (this file) — understand the KB structure
2. Read `index.md` — know what exists
3. Read `learnings/rules.md` — load proven rules
4. Read `strategy/product-positioning.md` — know what we're selling
5. Read the latest snapshot — know current performance
6. Proceed with the cycle

This replaces the current approach of re-reading `program.md`, `config.yaml`, `product.md`, `memory/learnings.md` from scratch each time. The KB is pre-synthesized context.
