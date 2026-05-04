# Learnings

Generated from experiments.jsonl. Last updated: 2026-05-04 (Cycle 9).

## Confirmed Winners ✅

1. **"Run Agents in Git Worktrees"** (worktrees, C3, 18d) — 2 conv / 23 clicks = **8.7% CR**, CTR 4.1% → 7.0%. Old ad: 0 conv / 33 clicks. Natural capability framing beats keyword stuffing. **Best experiment result.**
2. **Negative keywords** — 5 deployed, ~$355/mo in waste eliminated:
   - "what is" PHRASE → informational intent (~$52/mo)
   - "process automation" PHRASE → non-dev traffic (~$12/mo)
   - "claude code plans" EXACT → pricing seekers (~$122/mo)
   - "claude managed agents" PHRASE → Claude feature seekers (~$74/mo)
   - "claude coworker" PHRASE → Claude feature seekers (~$95/mo, pending approval)

## Confirmed Losers ❌

### Ad swaps that failed
1. **"Skip the Prompt Wrangling"** (claude_code, C2) — 112 clicks, 0 conv. Original had 1.56% CR. Rolled back C5. **Cost: ~$640.**
2. **"Agentic Coding Platform" RSA** (coding_agent, C4) — 3 clicks / 86 impr = 3.5% CTR vs old DKI's 9.7%.
3. **"Agentic Coding Tools" RSA** (coding_agent, C7) — 0 clicks / 13 impr. Third consecutive failure.
4. **sdd C3 ad** (C3, 18d) — 0 conv / 68 clicks despite 14.7% CTR. High CTR ≠ conversions. Rollback proposed.

### Ad groups that never convert (audience problems, not copy)
5. **ralph** — 0 conv EVER: 115+ clicks, $1,094/mo across 3 ads over 30 days. Pause recommended.
6. **gastown_ai** — 0 conv EVER: 31+ clicks, $517/mo across 3 ads. Pause recommended.
7. **coding_agent** — 0 conv EVER: 3 ads failed consecutively. DKI ad can't be restored. Pause recommended.

## Still Running 🟡 (150-click maturity gate applies)

| Experiment | Ad Group | Age | Clicks | Conv | Status |
|---|---|---|---|---|---|
| C5 | claude_code rollback | 18d | 89 | 0 | 89/150 clicks. 0 conv concerning but below scoring threshold. |
| C8 | sdd rollback | 7d | 27 | 0 | 27/150 clicks. Too early. |
| C3 | orchestration | 25d | 27 | 0 | 27/150 clicks. Very slow volume (~1/day). |
| C3 | worktrees | 25d | 32 | 2 | 32/150 clicks. 2 conv = 6.25% CR but sample too small. |

## What Converts — Headline Patterns

- "Run Agents in Git Worktrees" → **8.7% CR** ⭐ (worktrees)
- "No More Pasting Into Prompts" → 8.33% CR (claude_code)
- "Orchestrate Agents in Parallel" → 6.67% CR (orchestration)
- "Claude Code With Worktrees" → 4.88% CR (claude_code)
- "Agentic Orchestration" → 4.35% CR (orchestration)
- "Augment Intent" → 4.35% CR (sdd)
- **Pattern**: Capability-specific + action verbs + natural language. Pain-point elimination. Methodology naming for high-intent.

## What Does NOT Convert — Headline Patterns

- "Free with Claude Code Sub" → 972 clicks, 0 conv
- "Download Free for Mac" → 437 clicks, 0 conv
- "One App for AI Development" → 445 clicks, 0 conv
- "Code, Preview, Git In One" → 368 clicks, 0 conv
- "Beyond Ralph" → 170 clicks, 0 conv
- "Better Than Claude Code Alone" → 162 clicks, 0 conv
- "From Spec To PR In Parallel" → 156 clicks, 0 conv
- "Skip the Prompt Wrangling" → 112 clicks, 0 conv (C2 loser)
- "Parallel Git Worktree AI" → 34 clicks, 0 conv
- **Pattern**: Free/price, generic AI, abstract claims, keyword stuffing all fail.

## Ad Group Tiers (as of 2026-04-27)

### Tier 1: Converting, don't touch
- **ade** — 10.89% CR (DKI ad, can't reproduce)
- **claude_code_mac** — 7.9% CR (3 conv / 38 clicks)
- **conductor** — 12.5% CR (1 conv / 8 clicks)
- **worktrees** — 8.7% CR (winner from C3 swap)

### Tier 2: Monitor (waiting for 150-click maturity)
- **claude_code** — Rollback deployed C5, 89 clicks 0 conv (need 61 more clicks to score)
- **sdd** — Rollback deployed C8, 27 clicks 0 conv (need 123 more clicks to score)
- **orchestration** — C3 swap, 27 clicks 0 conv, ~1 click/day (will take months to reach 150)

### Tier 3: Paused (never converted)
- **ralph** — Paused C8. 0% CR, 115 clicks, $1,094/mo.
- **gastown_ai** — Paused C8. 0% CR, 31 clicks, $517/mo.
- **coding_agent** — Paused C8. 0% CR, 3 consecutive failures.

## Rules (requires ≥3 data points)

1. **Price-first messaging does not convert.** (972/0, 437/0, 56/0). Never lead with free/price.
2. **"[Brand] in One Workspace" converts.** "Claude Code in One Workspace" (7 conv). Pattern = competitor + "in One Workspace".
3. **Generic AI language does not convert.** (445/0, plus 2 more). Specificity beats category.
4. **Spec/workflow messaging works on high-intent.** (455/1, 210/1, 23/1).
5. **Natural capability framing beats keyword stuffing.** "Run Agents in Git Worktrees" (23/2, 8.7% CR) vs "Parallel Git Worktree AI" (34/0). NEW C3→C8.
6. **Don't swap converting ads without A/B test.** claude_code swap cost ~$640. Use ad_variation for CR > 0%. NEW C5.
7. **High CTR ≠ conversions.** sdd C3 ad: 14.7% CTR, 0 conv / 68 clicks. CTR measures relevance of headline, not landing page fit. NEW C8.
8. **3 failed ads = not a copy problem.** ralph (3 ads/0 conv), coding_agent (3 ads/0 conv). Stop iterating copy, investigate audience/LP. NEW C8.

## Deployment Notes

- RSAs are **immutable** via AdService UPDATE. Always create-new + pause-old.
- DKI headlines exceed 30-char schema limit. Can't reproduce — preserve existing DKI RSAs.
- ade: preserve RSA 799320437900 — DKI driving 10.89% CR.
- coding_agent: DKI ad can't be restored. Group should be paused.

## Account CR Trend

| Cycle | Date | CR | Note |
|---|---|---|---|
| 1 | Apr 7 | 0.57% | Baseline |
| 4 | Apr 13 | 0.57% | Flat — experiments too young |
| 5 | Apr 16 | 0.74% | worktrees 1st conv + negative keywords |
| 6 | Apr 20 | 0.93% | worktrees 2nd conv |
| 7 | Apr 23 | 1.10% | Window shift |
| 8 | Apr 27 | 1.19% | Stabilizing |
| 9 | May 4 | 0.83% | OBSERVE cycle. Drop likely from window shift (losing early high-CR days). |

## Meta-Learnings

1. **Negative keywords are the highest-ROI lever.** ~$355/mo saved, zero risk.
2. **Be conservative with high-performers.** claude_code swap was a $640 mistake.
3. **3 failed ads = audience/LP problem.** Stop iterating copy.
4. **CTR ≠ CR.** sdd proves great CTR can mask zero conversions.
5. **~$1,836/mo addressable waste** in ralph + gastown_ai + coding_agent (all 0 conv ever).
6. **Account CR: 0.57% → 1.19% → 0.83%.** The drop from C8→C9 illustrates why the 150-click gate matters — CR is volatile with small samples. Window shift moved high-CR days out of the 30-day range.
