# Google Ads Account Audit — Full Knowledge Base
**Account**: 9232939339 | **Manager**: 7885345352
**Last updated**: 2026-05-01 | **Data sources**: All-time retro + MCP live queries (last 30d)

---

## 1. Account Overview

| Metric | Value |
|--------|-------|
| Total campaigns created | ~75 |
| Currently ENABLED | 19 |
| Currently PAUSED | ~45+ |
| Active ad groups | ~60 |
| All-time spend | ~$344K |
| All-time conversions | ~10,534 |
| Blended all-time CPA | ~$32.66 (heavily brand-skewed) |
| Non-brand conversions | ~1,518 |
| Non-brand spend | ~$217K |
| **True non-brand CPA** | **~$143** |

**Naming convention**: `{platform}_{geo}_{team}_{channel}_{strategy}_{qualifier}`
Example: `gg_nam_dg_search_competitor_intent_claude_mac`

**Geographic coverage**: NAM (primary), EMEA (secondary), APAC (all paused), Global (display/demandgen remarketing)
**Campaign types**: Search (12), Display (2), Demand Gen (3), Video/YouTube (2)

---

## 2. Conversion Tracking (CRITICAL FINDING)

**7 of 9 conversion actions are set as PRIMARY for bidding.**

| Conversion Action | Type | Category | Primary? | Issue |
|---|---|---|---|---|
| Install | Website | Page View | ⭐ YES | Top-of-funnel — inflates conversion counts |
| User Signed Up | Website | Page View | ⭐ YES | Account creation |
| Credit Card Added | Website | Page View | ⭐ YES | Payment intent |
| Customer Created | Website | Page View | ⭐ YES | Actual paid conversion |
| Clicked Download Intent | Website | Download | ⭐ YES | CTA click — very top of funnel |
| Submitted Contact Us Form | Website | Download | ⭐ YES | Inbound lead |
| YouTube channel subscriptions | Auto | — | ⭐ YES | Vanity metric counting as conversion! |
| YouTube follow-on views | Auto | — | ⭐ YES | Vanity metric counting as conversion! |
| Lead form - Submit | Lead form | Download | ❌ NO | Only non-primary action |

### Impact
- **Smart Bidding is optimizing for ALL of these simultaneously.** A "Download Intent" click counts the same as a "Customer Created" event.
- **YouTube subscriptions and follow-on views are PRIMARY** — this means YouTube campaigns technically "convert" but at zero business value.
- The 10,534 "conversions" are **multi-counted across the funnel**. Actual unique customers are far fewer.
- **Recommendation**: Set only "Customer Created" (or at most "User Signed Up") as primary. Everything else secondary/observation.

---

## 3. Campaign Performance Tiers (Last 30 Days — Live MCP Data)

### Tier 1: Keep & Optimize
| Campaign | Bidding | Clicks | Conv | Cost | CPA | IS | Budget Lost IS |
|---|---|---|---|---|---|---|---|
| NAM Brand | Manual CPC | 670 | 30 | $2,481 | $82.70 | 10.0% | **90.0%** |
| EMEA Brand | Manual CPC | 605 | 24 | $1,346 | $56.08 | 11.9% | **85.6%** |
| Claude Mac Competitor | Manual CPC | 442 | 38 | $8,046 | $211.74 | 16.7% | **69.2%** |
| Global Display Remarket | Manual CPC | 906 | 25 | $456 | $18.24 | — | — |
| Global DemandGen Remarket | Max Conv | 333 | 18 | $2,111 | $117.28 | — | — |

### Tier 2: Underperforming, Needs Restructure
| Campaign | Bidding | Clicks | Conv | Cost | CPA | IS | Rank Lost IS |
|---|---|---|---|---|---|---|---|
| Claude Competitor (non-mac) | Manual CPC | 414 | 6 | $3,049 | $508 | 10.7% | **38.0%** |
| Generic Intent | Manual CPC | 415 | 4 | $4,196 | $1,049 | 11.7% | 9.3% |
| Competitor Intent (ralph etc) | Manual CPC | 155 | 1 | $1,703 | $1,703 | 10.0% | 12.5% |

### Tier 3: Burn — Pause or Kill
| Campaign | Bidding | Clicks | Conv | Cost | CPA |
|---|---|---|---|---|---|
| YouTube NAM | CPV | 67 | 0 | $4,267 | ∞ |
| YouTube EMEA | CPV | 159 | 0 | $6,395 | ∞ |

---

## 4. Impression Share Analysis (CRITICAL FINDING)

**Brand campaigns are capturing only 10-12% of available impressions.**

| Campaign | IS | Budget Lost | Rank Lost | Meaning |
|---|---|---|---|---|
| NAM Brand | 10.0% | **90.0%** | 2.2% | Budget-starved — losing 90% of brand searches |
| EMEA Brand | 11.9% | **85.6%** | 2.5% | Same — massive budget gap |
| Claude Mac | 16.7% | **69.2%** | 14.1% | Budget + some rank issues |
| Generic Intent | 11.7% | **79.0%** | 9.3% | Budget-starved but low conversion anyway |
| Competitor Intent | 10.0% | **80.8%** | 12.5% | Budget-starved |
| Claude (non-mac) | 10.7% | 51.2% | **38.0%** | Rank problem — low QS driving this |

### Interpretation
- Brand IS at 10% means **9 out of 10 people searching "augment code" DON'T see our ad**.
- Brand campaigns have QS 10 and $0.94 CPC — this is the cheapest, highest-converting traffic.
- Budget is $60/day NAM + $35/day EMEA = $95/day for brand. Should be 5-10x this.
- $940/day goes to Competitor Max Conv which under-spends. Budget is misallocated.

---

## 5. Quality Score Analysis (Last 30 Days)

### QS 10 (Perfect) — All brand keywords
| Keyword | Campaign | Clicks | Conv | CR |
|---|---|---|---|---|
| augment code (exact) | NAM Brand | 339 | 10 | 3.0% |
| augment code (exact) | EMEA Brand | 331 | 8 | 2.3% |
| augment code intent (exact) | NAM Brand | 33 | 10 | **30.3%** |
| augment code intent (exact) | EMEA Brand | 17 | 5 | **29.4%** |
| augment code mcp | NAM Brand | 21 | 2 | 11.1% |
| augmentcode (phrase) | Both | 63 | 4 | 6.3% |
| augment ai (exact) | Both | 100 | 0 | 0.0% |

### QS 5 — Generic keywords (mixed)
| Keyword | Campaign | Clicks | Conv | CR | LP Score |
|---|---|---|---|---|---|
| spec driven development | Generic Intent | 184 | 1 | 0.5% | BELOW_AVERAGE |
| spec driven development ai | Generic Intent | 42 | 0 | 0.0% | BELOW_AVERAGE |
| ai agent orchestration | Generic Intent | 23 | 0 | 0.0% | BELOW_AVERAGE |
| agent orchestration | Generic Intent | 15 | 1 | 6.7% | BELOW_AVERAGE |

### QS 1-3 — Competitor keywords (problematic)
| Keyword | QS | Clicks | Conv | CR | LP Score |
|---|---|---|---|---|---|
| download claude mac | 3 | 182 | 30 | **16.5%** | BELOW_AVERAGE |
| claude for mac | 3 | 124 | 4 | 3.2% | BELOW_AVERAGE |
| claude code workspace | 3 | 106 | 1 | 0.9% | BELOW_AVERAGE |
| claude code install on mac | 2 | 97 | 3 | 3.1% | BELOW_AVERAGE |
| ralph loop | 3 | 53 | 0 | 0.0% | BELOW_AVERAGE |
| ralph loop claude code | 2 | 41 | 0 | 0.0% | BELOW_AVERAGE |
| google antigravity | 1 | 11 | 0 | 0.0% | BELOW_AVERAGE |

### Pattern: Landing page is BELOW_AVERAGE on every non-brand keyword
- Every keyword with QS < 10 has `post_click_quality_score = BELOW_AVERAGE`
- This means the landing page doesn't match searcher intent for non-brand queries
- Fix: Create dedicated landing pages per keyword intent cluster

---

## 6. Device Performance (Last 30 Days)

| Device | Clicks | Conv | Cost | CR |
|--------|--------|------|------|-----|
| **Desktop** | 2,513 | 102 | $20,491 | **4.0%** |
| Mobile | 183 | 1 | $319 | **0.5%** |
| Tablet | 5 | 0 | $10 | 0.0% |

### Key Insight
- **Desktop CR is 8x mobile CR.** This is a developer tool — developers search on desktop.
- Mobile gets 6.8% of clicks but only 1% of conversions — nearly pure waste.
- **Action**: Consider mobile bid adjustments (-50% to -90%) on non-brand campaigns.

---

## 7. Hour-of-Day Performance (Last 30 Days, All Search)

| Time Block | Clicks | Conv | CR | Signal |
|-----------|--------|------|-----|--------|
| 00:00-04:00 | 391 | 11 | 2.8% | Low volume, moderate CR |
| 05:00-06:00 | 307 | 10 | 3.3% | EMEA morning ramp |
| **07:00-08:00** | **407** | **19** | **4.7%** | ⭐ Peak conversion window |
| 09:00-11:00 | 668 | 26 | 3.9% | High volume, good CR |
| 12:00-14:00 | 482 | 14 | 2.9% | Lunch dip |
| 15:00-18:00 | 311 | 14 | 4.5% | Afternoon recovery |
| **19:00-21:00** | **92** | **8** | **8.7%** | ⭐ Evening — low volume, highest CR |
| 22:00-23:00 | 43 | 0 | 0.0% | Dead zone |

---

## 8. Ad Group Performance Detail (Last 30 Days)

### Best Non-Brand Ad Groups
| Campaign | Ad Group | Clicks | Conv | CR | CPA |
|----------|----------|--------|------|-----|-----|
| Claude Mac | claude_code_mac | 442 | 38 | 8.6% | $212 |
| NAM Brand | augment_intent | 33 | 10 | **30.3%** | $2.40 |
| EMEA Brand | augment_intent | 17 | 5 | **29.4%** | $2.60 |
| Global DemandGen | website_visitors | 131 | 10 | 7.8% | $89 |
| Global Display | website_visitors_30d | 213 | 9 | 4.3% | $27 |
| Generic Intent | worktrees | 59 | 2 | 3.4% | $284 |

### Worst Ad Groups (Zero or Near-Zero Conversions)
ralph (104 clicks/$993), sdd (226/$2,177), coding_agent (22/$215), developer_tools (14/$135), workflow (11/$133), gastown_ai (30/$507), antigravity (11/$107), YouTube NAM (67/$4,267), YouTube EMEA (159/$6,395) — all 0% CR.

### Hidden Gem: "augment_intent" ad group
- 30.3% CR in NAM, 29.4% CR in EMEA on keyword "augment code intent"
- Highest-intent branded product searches — only 50 clicks/mo but room to grow with brand awareness

---

## 9. Negative Keyword Gaps

**5 highest-spending active campaigns have ZERO negative keywords:**
- gg_nam_dg_search_competitor_intent_claude ($11,327 all-time)
- gg_nam_dg_search_competitor_intent ($5,547)
- gg_nam_dg_search_generic_intent ($13,063)
- gg_nam_dg_search_competitor_max_conv ($11,474)
- gg_nam_dg_search_generic_maxclicks ($1,049)

Agent deployed 5 negatives saving ~$355/mo. More needed.

---

## 10. Audience Inventory (44 Lists — Unused)

| Category | Count | Largest Size |
|----------|-------|-------------|
| YouTube Engagers | 12 | 3.8M |
| Website Remarketing | 7 | 220K |
| GA4/Analytics | 7 | 270K |
| CRM/Customer Match | 4 | 100 |
| Lookalike | 3 | **All 0 size** |
| Smart/Optimized | 2 | 320K |

Issues: No suppression, all lookalikes empty, duplicate lists, stale CRM (March 2025), no funnel segmentation, YouTube lists (150K-420K) untapped for Search bid adjustments.

---

## 11. Budget Allocation (Current Daily)

| Bucket | Daily | Monthly | % | Efficiency |
|--------|-------|---------|---|-----------|
| Competitor Max Conv | $940 | $28,200 | 41% | 🟢 $17 CPA (under-spends) |
| Claude Mac | $450 | $13,500 | 20% | 🟡 $209 CPA |
| YouTube | $250 | $7,500 | 11% | 🔴 ∞ CPA |
| **NAM Brand** | **$60** | **$1,800** | **3%** | 🟢 **$10 CPA — UNDERFUNDED** |
| **EMEA Brand** | **$35** | **$1,050** | **2%** | 🟢 **$57 CPA — UNDERFUNDED** |
| TOTAL | ~$2,405 | ~$72,150 | | |

**Budget Inversion**: Brand (best CPA) gets 5% of budget but loses 90% of impressions. YouTube ($0 return) gets 11%.

---

## 12. Autoresearch Agent Results (8 Cycles)

CR: 0.49% → 1.19% (+109%) over 8 cycles. Attribution: ~40% agent, ~60% variance.
Key wins: worktrees ad (8.7% CR), negative keywords ($355/mo saved).
Key losses: claude_code swap ($640 mistake), ralph/gastown_ai/coding_agent (all paused).

**Meta-Rules**: (1) Negatives = highest ROI, (2) Don't touch winners without A/B, (3) 3 failures = audience problem, (4) CTR ≠ CR, (5) Natural framing > keyword stuffing, (6) Price-first fails, (7) Generic AI language fails.

---

## 13. Top 10 Issues to Fix (Priority Order)

| # | Issue | Impact | Effort |
|---|-------|--------|--------|
| 1 | **7 conversion actions are PRIMARY** — Smart Bidding optimizes for vanity metrics | CRITICAL | Low |
| 2 | **Brand IS at 10%** — losing 90% of brand searches | HIGH | Low |
| 3 | **5 campaigns have ZERO negative keywords** | HIGH | Medium |
| 4 | **Budget inverted** — YouTube gets 4x more than Brand | HIGH | Low |
| 5 | **LP quality BELOW_AVERAGE on all non-brand keywords** | HIGH | High |
| 6 | **Mobile CR 0.5% vs Desktop 4.0%** — no bid adjustments | MEDIUM | Low |
| 7 | **YouTube = $16.8K for 0 conversions** | MEDIUM | Low (pause) |
| 8 | **Audiences unused** — no suppression, no segmentation | MEDIUM | Medium |
| 9 | **DemandGen remarketing CPA 5-8x Display** | MEDIUM | Low |
| 10 | **All lookalike audiences = 0 size** | LOW | Medium |

