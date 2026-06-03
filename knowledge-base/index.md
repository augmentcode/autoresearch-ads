# Knowledge Base Index
**Last updated**: 2026-05-01 | **Total pages**: 3 (+ schema, index, log)

---

## Schema & Navigation
| Page | Path | Purpose |
|------|------|---------|
| Schema & Operations | [KNOWLEDGE.md](KNOWLEDGE.md) | How the KB is structured, operations guide, conventions |
| Index | [index.md](index.md) | This file — content catalog |
| Log | [log.md](log.md) | Chronological record of all KB updates |

## Strategy Pages
| Page | Path | Summary | Last Updated |
|------|------|---------|-------------|
| Account Audit | [01-account-audit.md](01-account-audit.md) | Full Google Ads account audit — $344K spent, 10.5K conv, 13 sections covering conversion tracking, impression share, QS, device, hourly, budget, audiences, negatives | 2026-05-01 |
| **Executive Audit** | [executive-audit.md](executive-audit.md) | **Shareable** — boss-ready summary: TL;DR, what's working, 5 biggest problems, budget reallocation, product pivot context, next steps | 2026-05-01 |
| **Audience Strategy (Cosmos)** | [audience-strategy-cosmos.md](audience-strategy-cosmos.md) | Full audience targeting strategy — 6 custom segments, in-market/affinity layers, suppression, negatives, competitive positioning, rollout plan, budget allocation, measurement framework | 2026-05-01 |
| **Agent Architecture v2** | [agent-architecture-proposal.md](agent-architecture-proposal.md) | 4-layer composable system proposal: Intelligence → Strategy → Execution → Measurement. Includes MCP tool map, implementation roadmap, review gates, guardrails | 2026-05-01 |
| Google Ads Architecture | [02-google-ads-architecture.md](02-google-ads-architecture.md) | 9-layer system flow from Figma board — account → campaigns → ad groups → targeting → creative → auction → delivery → conversion → feedback loop. Maps optimization levers to agent capabilities. | 2026-05-01 |
| Product Positioning | [03-product-positioning.md](03-product-positioning.md) | Cosmos positioning — Unified Cloud Agents Platform; Agentic SDLC owned as higher-level theme. Category, claims, four key values with proof, ICPs, competitive framing, language do/don't. | 2026-06-03 |

## Entity Pages
*Not yet created. Will be built as KB matures.*

## Concept Pages
*Not yet created. Content currently embedded in architecture doc.*

## Learnings Pages
*Not yet created. Content currently in `memory/learnings.md` (legacy location).*

## Competitive Pages
*Not yet created. Will be populated when external research is ingested.*

---

## Migration Status
The following legacy files contain knowledge that should be migrated into the KB structure:

| Legacy File | Status | Target Location |
|------------|--------|----------------|
| `memory/learnings.md` | Active — 8 cycles of experiment learnings | → `learnings/rules.md`, `learnings/winners.md`, `learnings/losers.md`, `learnings/patterns.md` |
| `memory/experiments.jsonl` | Active — 25 experiment entries | → `sources/retro/experiments.jsonl` (copy as raw source) |
| `memory/snapshots/*.json` | Active — 4 snapshots | → `sources/snapshots/` (move or symlink) |
| `product.md` | Current — Cosmos messaging (2026-06-03 refresh) | Operational ads brief; cross-references `03-product-positioning.md` |
| `config.yaml` | Active — campaign config | Stays in root (operational, not knowledge) |
| `program.md` | Active — agent program | Stays in root (operational, not knowledge) |
