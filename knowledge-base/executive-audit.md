# Google Ads Account Audit — Executive Summary
**Account**: 9232939339 | **Prepared by**: Molisha Shah | **Date**: May 1, 2026
**Data**: All-time performance + live account queries (last 30 days)

---

## TL;DR

We've spent **$344K** on Google Ads generating **~10,500 conversions** at a blended **$33 CPA**. But that number hides three structural problems:

1. **86% of conversions are brand searches** — strip brand out and the true non-brand CPA is **$143**
2. **7 of 9 conversion actions are set as "primary"** — Smart Bidding can't distinguish a download click from a paid customer
3. **Budget is inverted** — brand campaigns (best CPA) get 5% of budget while YouTube (zero conversions) gets 11%

These are fixable. The recommendations below would reallocate ~$14K/mo from waste to high-performing channels and fix the data foundation that Smart Bidding relies on.

---

## What's Working

| Signal | Data | Implication |
|--------|------|-------------|
| **Brand campaigns** | QS 10, $0.94 CPC, 90%+ budget-lost IS | Best traffic in the account — massively underfunded |
| **Claude Mac competitor** | 8.6% CR, 38 conv/mo | Conquest traffic that actually converts |
| **Display remarketing** | $18 CPA, 25 conv/mo | Cheapest non-brand channel |
| **Desktop traffic** | 4.0% CR (8× mobile) | Developer audience searches on desktop |
| **Evening hours (7-9 PM)** | 8.7% CR | Low volume but highest conversion rate window |
| **"augment code intent" keyword** | 30% CR | Highest-intent branded search — room to scale with awareness |
| **Agent-driven copy testing** | CR: 0.49% → 1.19% over 8 cycles | Ad copy optimization is working, but hitting a ceiling |

---

## The 5 Biggest Problems

### 1. 🔴 Conversion Tracking Is Broken
**7 of 9 conversion actions are PRIMARY.** Smart Bidding treats a YouTube channel subscription the same as a paying customer. The "10,500 conversions" number is multi-counted funnel events — actual unique customers are far fewer.

**Fix**: Set only "Customer Created" as primary. Everything else → secondary/observation. **Effort**: 15 minutes. **Impact**: Immediate — Smart Bidding starts optimizing for real revenue.

### 2. 🔴 Brand Campaigns Are Starved
Brand impression share is **10%** — meaning **9 out of 10 people searching "augment code" don't see our ad.** Brand has QS 10, $0.94 CPC, and the best CPA in the account. It's losing impressions purely due to budget ($60/day NAM, $35/day EMEA).

**Fix**: Increase brand daily budget to $300-500/day combined. Fund it by pausing YouTube. **Impact**: Capture 5-10× more brand searches at the cheapest CPC in the account.

### 3. 🔴 $14K/Month Going to Zero-Return Channels
| Channel | Monthly Spend | Conversions | Verdict |
|---------|--------------|-------------|---------|
| YouTube NAM | $4,267 | 0 | Pause |
| YouTube EMEA | $6,395 | 0 | Pause |
| Mobile traffic (all campaigns) | ~$960 | ~1 | Reduce 90% |
| ralph/gastown_ai ad groups | ~$1,500 | 0 | Already paused |
| **Total recoverable** | **~$13,122/mo** | | |

### 4. 🟡 Landing Page Fails Non-Brand Traffic
Every non-brand keyword has **BELOW_AVERAGE** landing page quality score. This structurally caps Quality Score at 5-7 (vs brand at 10), which means:
- Higher CPCs (competitor keywords cost 19× more than brand)
- Lower ad positions
- Less impression share

**Fix**: Create intent-matched landing pages for each keyword cluster. **Effort**: High — requires product/marketing collaboration.

### 5. 🟡 5 Highest-Spending Campaigns Have Zero Negative Keywords
These campaigns are bleeding money on irrelevant searches like "claude code," "claude ai," "google antigravity." The autoresearch agent has deployed 5 negatives saving ~$355/mo, but systematic negative keyword coverage is needed across all campaigns.

---

## Budget Reallocation — Recommended

| Channel | Current Monthly | Recommended | Change |
|---------|----------------|-------------|--------|
| Brand (NAM + EMEA) | $2,850 (5%) | **$12,000 (17%)** | +$9,150 |
| Competitor (Claude Mac) | $13,500 (20%) | $13,500 (20%) | — |
| Competitor (Non-Mac) | $9,000 (13%) | $6,000 (9%) | -$3,000 |
| Display Remarketing | $1,370 (2%) | $3,000 (4%) | +$1,630 |
| DemandGen Remarketing | $6,330 (9%) | $4,000 (6%) | -$2,330 |
| Generic Intent | $4,500 (7%) | $2,000 (3%) | -$2,500 |
| YouTube | **$7,500 (11%)** | **$0 (0%)** | **-$7,500** |
| Competitor Max Conv | $28,200 (41%) | $28,200 (41%) | — |
| **Total** | **~$73,250** | **~$68,700** | **-$4,550** |

Net effect: **$4,550/mo savings** while massively increasing brand coverage and cutting waste channels.

---

## Audience Inventory — Current State

| Category | Lists | Size | Status |
|----------|-------|------|--------|
| YouTube Engagers | 12 | up to 3.8M | Unused |
| Website Remarketing | 7 | up to 220K | Used in Display/DemandGen only |
| GA4/Analytics | 7 | up to 270K | Unused |
| CRM/Customer Match | 4 | ~100 | Stale (March 2025) |
| Lookalike | 3 | **All 0 size** | Broken |
| Smart/Optimized | 2 | up to 320K | Auto-generated |

**44 audience lists exist with no strategy.** No suppression (existing customers see ads), no tiering, no funnel segmentation, duplicate lists.

---

## Product Pivot Context

We are transitioning from **Intent** (a developer workspace) to **Cosmos** (an operating system for agentic software development). This means:

- Most existing keyword targeting (Cursor, Claude Code, spec-driven development) **becomes less relevant**
- New keyword universe needed around **agent platforms, agentic SDLC, autonomous workflows**
- Target buyer shifts from **individual developers** to **platform teams and engineering organizations**
- Audience strategy needs complete rebuild for the new category
- Existing brand campaigns remain relevant — "augment code" searchers are warm leads regardless

---

## Recommended Next Steps (Priority Order)

| # | Action | Impact | Effort | Timeline |
|---|--------|--------|--------|----------|
| 1 | Fix conversion actions — set only "Customer Created" as primary | CRITICAL | 15 min | Today |
| 2 | Pause YouTube campaigns | HIGH | 5 min | Today |
| 3 | Increase brand budget to $300-500/day | HIGH | 5 min | Today |
| 4 | Add negative keywords to top 5 spending campaigns | HIGH | 2 hours | This week |
| 5 | Set mobile bid adjustment -80% on non-brand campaigns | MEDIUM | 30 min | This week |
| 6 | Refresh CRM audience list | MEDIUM | 1 hour | This week |
| 7 | Design new keyword strategy for Cosmos positioning | HIGH | 1 week | Next sprint |
| 8 | Build intent-matched landing pages | HIGH | 2-3 weeks | Next sprint |
| 9 | Restructure campaigns for Cosmos product launch | HIGH | 1 week | After LP ready |
| 10 | Build new audience strategy for platform buyer | MEDIUM | 1 week | After keyword research |

---

*Data sources: Google Ads account 9232939339 (all-time + live MCP queries May 1, 2026). Prepared using autoresearch-ads knowledge base.*
