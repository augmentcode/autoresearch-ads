# Google Ads System Architecture
**Source**: [Figma Board](https://www.figma.com/board/6Pqc7EsElV7qzFK8biChKs/Google-Ads-System-Architecture)
**Last updated**: 2026-05-01

---

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    GOOGLE ADS SYSTEM FLOW                                       │
│                                                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────────────────────┐  │
│  │   MANAGER    │────▶│  GOOGLE ADS  │────▶│  CAMPAIGNS   │────▶│       AD GROUPS            │  │
│  │   ACCOUNT    │     │   ACCOUNT    │     │              │     │  Controls: Keywords,       │  │
│  │  Umbrella/   │     │              │     │ • Search     │     │  Ads, Targeting             │  │
│  │  Billing     │     │              │     │ • Display    │     │  e.g. exact, phrase,       │  │
│  └──────────────┘     └──────────────┘     │ • Demand Gen │     │  cursor_ai, pycharm        │  │
│                                            │ • Video/YT   │     └──────┬───────┬─────────────┘  │
│                                            └──────────────┘            │       │                 │
│                        Controls: Budget, Geo, Channel, Bidding         │       │                 │
│                                                                        ▼       ▼                 │
│                                                              ┌─────────────┐ ┌───────────────┐  │
│                                                              │  TARGETING  │ │   CREATIVE    │  │
│                                                              │  INPUTS     │ │   LAYER       │  │
│                                                              │             │ │               │  │
│                                                              │ • Geo       │ │ • RSAs        │  │
│                                                              │ • Keywords  │ │   3-15 heads  │  │
│                                                              │ • Negatives │ │   2-4 descs   │  │
│                                                              │ • Audiences │ │ • Video Ads   │  │
│                                                              └──────┬──────┘ │ • Display Ads │  │
│                                                                     │        └───────────────┘  │
│                                                                     ▼                            │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐│
│  │                           GOOGLE AUCTION SYSTEM                                             ││
│  │                                                                                             ││
│  │  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           ││
│  │  │ User Types   │────▶│  Keyword     │────▶│ Quality Score│────▶│   AD RANK    │           ││
│  │  │ Search Query │     │  Matching    │     │   1-10       │     │  Bid × QS ×  │           ││
│  │  │              │     │  Does query  │     │ Relevance +  │     │  Expected    │           ││
│  │  │              │     │  match your  │     │ CTR +        │     │  Impact      │           ││
│  │  │              │     │  keywords?   │     │ Landing Page │     │              │           ││
│  │  └──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘           ││
│  │        ▲                      ▲                                        │                    ││
│  │        │               Keywords feed in                                │                    ││
│  │        │               Negatives BLOCK                                 │                    ││
│  │        │               Audiences narrow/expand                         │                    ││
│  │        │               Geo filters                                     │                    ││
│  │        │               Bidding adjusts                                 │                    ││
│  └────────┼───────────────────────────────────────────────────────────────┼────────────────────┘│
│           │                                                               │                     │
│           │                                                               ▼                     │
│  ┌────────┼──────────────────────────────────────────────────────────────────────────────────┐  │
│  │        │                    AD DELIVERY                                                   │  │
│  │        │  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │  │
│  │        │  │  Ad Shown    │────▶│  User Clicks  │────▶│ Landing Page │                     │  │
│  │        │  │  to User     │     │  (pay CPC)    │     │              │                     │  │
│  │        │  └──────────────┘     └──────┬────────┘     └──────┬───────┘                     │  │
│  │        │                              │                      │                             │  │
│  └────────┼──────────────────────────────┼──────────────────────┼─────────────────────────────┘  │
│           │                              │                      ▼                                │
│  ┌────────┼──────────────────────────────┼──────────────────────────────────────────────────┐    │
│  │        │            CONVERSION FUNNEL │                                                  │    │
│  │        │  ┌──────────┐  ┌──────────┐  │  ┌──────────┐  ┌──────────────┐                 │    │
│  │        │  │ Install  │─▶│  User    │──┼─▶│ Credit   │─▶│   Customer   │                 │    │
│  │        │  │          │  │ Signed Up│  │  │Card Added│  │   Created    │                 │    │
│  │        │  └──────────┘  └──────────┘  │  └──────────┘  └──────┬───────┘                 │    │
│  └────────┼──────────────────────────────┼───────────────────────┼─────────────────────────┘    │
│           │                              │                       │                              │
│           │  ┌───────────────────────────┼───────────────────────┘                              │
│           │  │       FEEDBACK LOOP       │                                                      │
│           │  │  ┌──────────────┐     ┌───┴──────────┐                                          │
│           │  │  │ Performance  │────▶│ Optimization │──── refine ──▶ Ad Groups                  │
│           │  │  │ Data: Clicks,│     │ Pause losers,│──── adjust ──▶ Bidding                    │
│           └──│──│ Conv, CPA, QS│     │ add negatives│──── update ──▶ Negatives                  │
│              │  └──────────────┘     │ adjust bids, │                                          │
│              │                       │ test copy    │                                          │
│              │                       └──────────────┘                                          │
│              └─────────────────────────────────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Breakdown

### Layer 1: Account Structure
```
Manager Account (Umbrella / Billing)
  └── Google Ads Account
        ├── Search Campaigns (Brand, Competitor, Generic)
        ├── Display Campaigns (Remarketing)
        ├── Demand Gen Campaigns (Remarketing)
        └── Video / YouTube (Prospecting)
```

**Campaign controls**: Budget (daily cap), Geographic targeting, Channel type, Bidding strategy.
Each campaign contains one or more **Ad Groups**.

### Layer 2: Ad Group — The Operational Unit
The ad group is where targeting meets creative. It controls:
- **Keywords** — what search queries trigger your ads
- **Ads** — what the user sees (RSAs, display, video)
- **Targeting** — audiences, demographics, devices

This is the level where the autoresearch agent operates today.


### Layer 3: Targeting Inputs (Feed into the Auction)

| Input | What It Does | How It Affects Auction |
|-------|-------------|----------------------|
| **Geographic Targeting** | NAM, EMEA, APAC | **Filters** — restricts who sees your ad by location |
| **Keywords** (Exact, Phrase, Broad) | Match user queries to your ads | **Feeds into** keyword matching — determines if you enter the auction |
| **Negative Keywords** | Block irrelevant searches | **Blocks** — prevents you from entering the auction for wasteful queries |
| **Audiences** (Remarketing, CRM, YouTube, Lookalike) | Layer on user signals | **Narrows or expands** — can adjust bids or restrict delivery to known users |

### Layer 4: Creative Layer

| Ad Format | Specs | Used In |
|-----------|-------|---------|
| **Responsive Search Ads (RSAs)** | 3-15 headlines (≤30 chars), 2-4 descriptions (≤90 chars) | Search campaigns |
| **Video Ads** | YouTube pre-roll, in-stream | Video/YouTube campaigns |
| **Display / Image Ads** | Banner formats | Display, Demand Gen campaigns |

**RSA mechanics**: Google assembles combinations from your headline/description pool. It learns which combinations perform best per query. You can pin headlines to specific positions. RSAs are **immutable** — you can't edit them after creation, only create new + pause old.

### Layer 5: Google Auction System

This is the core engine. Every time a user searches, this happens in milliseconds:

```
User types query
       │
       ▼
┌─────────────────┐
│ Keyword Matching │ ◀── Do your keywords match this query?
│                  │     Exact: query = keyword
│                  │     Phrase: keyword is substring of query
│                  │     Broad: semantic match (Google decides)
│                  │     Negative: if match → BLOCKED, exit auction
└────────┬────────┘
         ▼
┌─────────────────┐
│  Quality Score   │  1-10, three components:
│                  │  1. Expected CTR (historical)
│                  │  2. Ad Relevance (keyword ↔ ad copy)
│                  │  3. Landing Page Experience (LP ↔ query)
└────────┬────────┘
         ▼
┌─────────────────┐
│    AD RANK      │  = Max Bid × Quality Score × Expected Impact
│                 │
│  Higher rank = higher position = more visibility
│  You pay: (rank below you ÷ your QS) + $0.01
│  → High QS = LOWER actual CPC
└─────────────────┘
```

**Critical insight for autoresearch**: Quality Score is the **multiplier** on everything. A QS 10 keyword pays ~1/3 the CPC of a QS 3 keyword for the same position. Our brand keywords (QS 10) have $0.94 CPC. Our Claude competitor keywords (QS 3) have $18.28 CPC. That's a 19x cost difference driven entirely by QS.

### Layer 6: Ad Delivery

```
Ad Shown → User Clicks (you pay CPC) → Landing Page → Conversion Funnel
```

Three performance signals feed back:
1. **Impression** — ad was shown (cost = $0, but uses impression share)
2. **Click** — user clicked (you pay CPC)
3. **Conversion** — user completed a goal action on your site

### Layer 7: Conversion Funnel (Augment-Specific)

```
Install → User Signed Up → Credit Card Added → Customer Created
```

Each stage is tracked as a separate conversion action. Currently **7 of 9 actions are PRIMARY** — meaning Smart Bidding treats a click-to-download the same as a paid customer. This is the #1 issue found in the audit.

### Layer 8: Bidding Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Manual CPC** | You set max bid per click | Full control, low-data campaigns |
| **Target CPA** | Google auto-bids to hit your target cost-per-acquisition | Campaigns with 30+ conversions/month |
| **Maximize Conversions** | Google spends full budget to get max conversions | Campaigns with clear conversion signal |

**Current state**: Brand campaigns use Manual CPC (leaving optimization on the table with QS 10). Smart Bidding campaigns count all 7 primary conversion actions, inflating what "maximize conversions" optimizes for.

### Layer 9: Feedback Loop

```
Performance Data ──▶ Optimization ──▶ Back into the system
(Clicks, Conv,       (Pause losers,
 CPA, QS)            add negatives,
                      adjust bids,
                      test copy)
                          │
                          ├──▶ refine → Ad Groups (new copy, pause bad ads)
                          ├──▶ adjust → Bidding (change strategy, bid amounts)
                          └──▶ update → Negative Keywords (block waste)
```

**This is where autoresearch-ads operates today.** The agent runs in the feedback loop: pulls performance data, scores experiments, generates new copy, deploys, and logs. But it currently only touches:
- ✅ Ad copy (headlines/descriptions within RSAs)
- ✅ Negative keywords (blocking waste)
- ❌ Bidding strategy (untouched)
- ❌ Budget allocation (untouched)
- ❌ Audience targeting (untouched)
- ❌ Campaign structure (untouched)
- ❌ Landing page optimization (untouched)
- ❌ Keyword expansion (logged but pending MCP tool)
- ❌ Device/geo/schedule bid adjustments (untouched)
- ❌ Conversion action configuration (untouched)

---

## How the Architecture Maps to Optimization Levers

| Lever | Layer | Impact | Agent Can Touch Today? |
|-------|-------|--------|----------------------|
| Conversion action setup (primary/secondary) | Conversion Funnel | CRITICAL | ❌ No |
| Budget reallocation | Campaign | HIGH | ❌ No |
| Bidding strategy changes | Bidding | HIGH | ❌ No |
| Negative keywords | Targeting | HIGH | ✅ Yes (via MCP) |
| Keyword expansion | Targeting | MEDIUM | ⚠️ Logged, MCP tool now available |
| Ad copy testing | Creative | MEDIUM | ✅ Yes (core capability) |
| Audience targeting | Targeting | MEDIUM | ❌ No |
| Device bid adjustments | Campaign/Ad Group | MEDIUM | ❌ No |
| Ad schedule bid adjustments | Campaign | LOW-MED | ❌ No |
| Landing page changes | Ad Delivery | HIGH | ❌ No (outside Google Ads) |
| Campaign structure (pause/create) | Campaign | HIGH | ❌ No |

### The Gap
The agent is optimizing at the **Creative Layer** (ad copy) and **Targeting** (negatives), which are medium-impact levers. The highest-impact levers — conversion setup, budget, bidding, campaign structure — are untouched. This is why CR improved 109% but remains at 1.19%: copy optimization has a ceiling when the structural problems above it remain.

---

## Key Formulas

```
Ad Rank = Max Bid × Quality Score × Expected Impact of Extensions

Actual CPC = (Ad Rank of advertiser below you) ÷ (Your Quality Score) + $0.01

Quality Score = f(Expected CTR, Ad Relevance, Landing Page Experience)
    Each component: BELOW_AVERAGE | AVERAGE | ABOVE_AVERAGE

Conversion Rate = Conversions ÷ Clicks
Cost Per Conversion = Cost ÷ Conversions
Search Impression Share = Your Impressions ÷ Total Eligible Impressions
Budget Lost IS = Impressions lost due to budget ÷ Total Eligible
Rank Lost IS = Impressions lost due to Ad Rank ÷ Total Eligible
```
