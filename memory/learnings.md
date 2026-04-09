# Learnings

Generated from experiments.jsonl. Last updated: 2026-04-09.

## Patterns (from baseline + cycle data)

### What converts — headline patterns
- "Claude Code With Worktrees" → 4.88% CR (claude_code)
- "No More Pasting Into Prompts" → 8.33% CR (claude_code)
- "Orchestrate Agents in Parallel" → 6.67% CR (orchestration)
- "Agentic Orchestration" → 4.35% CR (orchestration)
- "Multi-Agent Orchestration" → 2.70% CR (orchestration)
- "Augment Intent" (sdd) → 4.35% CR
- "Move Up the Stack to SDD" → 0.48% CR (sdd, 210 clicks)
- "Spec-Driven Development" → 0.22% CR (sdd, 455 clicks — high volume)
- **Pattern**: Capability-specific + action verbs convert. Pain-point elimination converts ("No More Pasting"). Methodology naming converts for high-intent searches (spec-driven).

### What does NOT convert — confirmed losers
- "Free with Claude Code Sub" → 972 clicks, 0 conversions
- "Download Free for Mac" → 437 clicks, 0 conversions
- "One App for AI Development" → 445 clicks, 0 conversions
- "Code, Preview, Git In One" → 368 clicks, 0 conversions
- "Beyond Ralph" → 170 clicks, 0 conversions
- "Better Than Claude Code Alone" → 162 clicks, 0 conversions
- "From Spec To PR In Parallel" → 156 clicks, 0 conversions
- "Parallel Git Worktree AI" → 34 clicks, 0 conversions
- **Pattern**: Free/price offers, generic AI language, abstract capability claims all fail. Keyword stuffing fails.

### Ad group performance (30-day, 2026-04-09)
| Ad Group | Impressions | Clicks | Conv | CR |
|---|---|---|---|---|
| ade | 309 | 18 | ~2 | 10.89% |
| conductor | 179 | 11 | 1 | 9.09% |
| orchestration | 1,511 | 126 | 2 | 1.59% |
| claude_code | 85,061 | 1,349 | 4 | 0.30% |
| sdd | 5,206 | 459 | 1 | 0.22% |
| ralph | 4,164 | 219 | 0 | 0% |
| gastown_ai | 1,040 | 117 | 0 | 0% |
| worktrees | 1,082 | 42 | 0 | 0% |

## Hypotheses under test (launched, awaiting data)

### Cycle 2 (deployed 2026-04-08)
| Proposal | Ad Group | Direction |
|---|---|---|
| "Skip the Prompt Wrangling" | claude_code | Pain-point elimination (mirrors 8.3% CR "No More Pasting") |
| "Prompt to Merged PR in Intent" | claude_code | Workflow-outcome headline |
| "Visual Diffs for Ralph Loop" | ralph | Concrete value-add over Ralph |
| "Ralph Loop in One Workspace" | ralph | Proven "[Brand] in One Workspace" structure |
| "Spec to PR No Tab Switching" | sdd | Friction elimination over abstract "In Parallel" |
| "Define What Agents Handle How" | sdd | Core spec-driven differentiator |

### Cycle 3 (deployed 2026-04-09)
| Proposal | Ad Group | Direction |
|---|---|---|
| "Spec-First Agent Orchestration" | orchestration | Spec-first methodology → high-intent buyer signal |
| "Run Agents in Git Worktrees" | worktrees | Speaks to git worktree searchers directly |
| "Intent Is Your Agentic IDE" | ade | SKIPPED — DKI constraint in existing RSA |

## Rules (requires ≥3 data points)

1. **Price-first messaging does not convert.** "Free with Claude Code Sub" (972 clicks, 0 conv), "Download Free for Mac" (437 clicks, 0 conv), "Download Free for Mac" ralph (56 clicks, 0 conv). Never lead with free/price.
2. **"[Brand] in One Workspace" headline structure converts.** "Claude Code in One Workspace" (7 conv across ad groups). Pattern = competitor-name + "in One Workspace".
3. **Generic AI language does not convert.** "One App for AI Development" (445 clicks, 0), "Reimagine Your AI Workflows" (0 expected), "Automated Agent Workflows" (0 expected). Specificity beats category.
4. **Spec-driven / workflow-outcome messaging works on high-intent traffic.** "Spec-Driven Development" (455 clicks, 1 conv), "Move Up the Stack to SDD" (210 clicks, 1 conv), "Augment Intent" (23 clicks, 1 conv). Buyers who think in specs/workflows convert.

## Deployment Notes

- Google Ads RSA headlines/descriptions are **immutable via AdService UPDATE**. Use `create_responsive_search_ad` + `pause_ad` (create-new, pause-old).
- DKI headlines (e.g. `{KeyWord:Agentic Dev Environment}`) exceed the MCP tool's local 30-char schema validation. Cannot be reproduced in new RSAs via this tool — existing RSAs with DKI must stay in place.
- ade ad group: preserve existing RSA (799320437900) — DKI headline is driving 10.89% CR. Do not swap until a workaround for DKI is found.
