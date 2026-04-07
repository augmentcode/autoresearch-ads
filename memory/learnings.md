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

### Hypotheses under test (cycle 2 — deployment failed)
All 5 proposals from cycle 2 failed to deploy due to Google Ads API IMMUTABLE_FIELD constraint on RSA headlines/descriptions. No outcome data yet.

| Proposal | Ad Group | Direction |
|---|---|---|
| "Parallel Claude Code Agents" | claude_code | Capability-first, mirrors proven pattern |
| "Claude Code With Living Spec" | claude_code | Differentiator framing (Intent vs. bare Claude Code) |
| "Run parallel Claude Code agents from spec to PR. No terminal switching, no conflicts." | claude_code | Workflow description, based on 10.3% CR pattern |
| "Ralph Loop Plus Visual Diff" | ralph | Concrete addition over Ralph's gap (no visual layer) |
| "Spec to PR, Zero Tab Switching" | sdd | Concrete friction elimination over abstract spec-to-PR |

## Rules (requires ≥3 data points — none yet)

No rules derived yet. Need more scored experiments.

## Deployment Notes

- Google Ads RSA headlines/descriptions are **immutable via AdService UPDATE**. Must use AdGroupAdAsset service or create-new-ad + pause-old-ad approach. All cycle 2 deployments blocked by this. Investigating MCP fix.
