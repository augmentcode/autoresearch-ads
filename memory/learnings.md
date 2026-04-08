# Learnings

Generated from experiments.jsonl. Last updated: 2026-04-07.

## Patterns (from baseline analysis)

### What converts in claude_code ad group
- "Claude Code With Worktrees" → 4.9% CR
- "Claude Code Without Conflicts" → 1.6% CR
- "Run Claude Code agents in parallel. Each in its own worktree, no conflicts." → 10.3% CR (4 conv)
- **Pattern**: capability-first messaging (parallel agents, worktrees, no conflicts) converts. Price-first messaging does not.

### What does NOT convert
- "Free with Claude Code Sub" → 987 clicks, 0 conversions
- "One App for AI Development" → 452 clicks, 0 conversions
- "Already have a Claude Code, Codex, or OpenCode subscription? Use Intent completely free." → 949 clicks, 0 conversions
- "Beyond Ralph" → 173 clicks, 0 conversions
- "From Spec To PR In Parallel" → 175 clicks, 0 conversions
- **Pattern**: free-tier offers, generic positioning, and abstract benefit claims do not convert.

### Hypotheses under test (cycle 2 — deployment failed, then re-attempted)
First 5 proposals from cycle 2 failed to deploy due to Google Ads API IMMUTABLE_FIELD constraint. Re-deployed cycle 2 on 2026-04-08 using create-new-RSA + pause-old approach.

| Proposal | Ad Group | Status | Direction |
|---|---|---|---|
| "Skip the Prompt Wrangling" | claude_code | **launched** | Pain-point elimination (mirrors 8.3% CR "No More Pasting Into Prompts") |
| "Prompt to Merged PR in Intent" | claude_code | **launched** | Workflow-outcome (mirrors 3.1% CR "Spec to PR With Claude Code") |
| "Visual Diffs for Ralph Loop" | ralph | **launched** | Concrete addition over Ralph's gap (visual workspace) |
| "Ralph Loop in One Workspace" | ralph | **launched** | Proven structure from "Claude Code in One Workspace" (2.0% CR, 7 conv) |
| "Spec to PR No Tab Switching" | sdd | **launched** | Concrete friction elimination over abstract "In Parallel" |
| "Define What Agents Handle How" | sdd | **launched** | Core spec-driven differentiator from product.md |

### Top performing assets (30-day data, 2026-04-08)
| Asset | Ad Group | CR | Conv | Impressions |
|---|---|---|---|---|
| "Spec to PR With Claude Code" | claude_code_mac | 16.7% | 3 | 321 |
| "Run Claude Code agents in parallel..." | claude_code_mac | 10.3% | 4 | 866 |
| "Claude Code in One Workspace" | claude_code_mac | 10.3% | 4 | 840 |
| "The developer workspace designed for orchestrating agents." | ade | 9.8% | 1.96 | 403 |
| "No More Pasting Into Prompts" | claude_code | 8.3% | 1 | 417 |
| "Spec to PR With Claude Code" | claude_code | 3.1% | 4 | 4,183 |
| "Claude Code With Worktrees" | claude_code | 2.8% | 2 | 2,106 |
| "Claude Code in One Workspace" | claude_code | 2.0% | 7 | 10,813 |

## Rules (requires ≥3 data points)

1. **Price-first messaging does not convert.** "Free with Claude Code Sub" (1,025 clicks, 0 conv), "Don't pay twice..." (995 clicks, 0 conv), "Already have a Claude Code..." (963 clicks, 0 conv). 3+ data points, all zero. Never lead with free/price.
2. **"[Brand] in One Workspace" headline structure converts.** "Claude Code in One Workspace" (7 conv across ad groups), replicated to ralph. Pattern = competitor-name + "in One Workspace".
3. **claude_code_mac is the highest-converting ad group.** 10-17% CR on multiple assets. Users searching install/download terms have strongest purchase intent.

## Deployment Notes

- Google Ads RSA headlines/descriptions are **immutable via AdService UPDATE**. Resolved: use `create_responsive_search_ad` + `pause_ad` (create-new, pause-old approach). Cycle 2 successfully deployed on 2026-04-08.
