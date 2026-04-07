# autoresearch-ads

Autonomous ad copy optimization through experimentation. You pull data, score previous experiments, generate new copy, deploy it, and log everything. One cycle per day. The metric is **conversion_rate** (conversions / clicks) — higher is better.

## Setup

To set up a new experiment run, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `apr8`). The branch `autoresearch-ads/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch-ads/<tag>` from current main.
3. **Read the in-scope files**:
   - `config.yaml` — campaigns, customer_id, ad groups, constraints, MCP query fields.
   - `product.md` — what the product is and what claims are safe to make.
   - `snapshot.py` — the data compression script you'll run each cycle. Do not modify.
4. **Verify MCP access**: Run a small test query to confirm Google Ads MCP responds. Query one campaign for `metrics.impressions` with a 1-day date range.
5. **Initialize results.tsv**: Create `results.tsv` with just the header row. The baseline will be recorded after the first cycle.
6. **Run the first cycle as baseline**: Pull data, compress, and log cycle 1 with status `baseline`. Do NOT generate or deploy copy on the first cycle — just establish the starting conversion_rate.
7. **Confirm and go**: Confirm setup looks good.

Once you get confirmation, begin daily experimentation.

## The Daily Cycle

Each cycle follows these steps in order:

### Step 1: Data Pull

Make MCP queries to get current campaign performance. Include conversion fields in every query.

**Query A — Structure** (campaigns + ad groups):

Call `search` on Google Ads MCP twice:

1. Resource: `campaign`
   - Fields from `config.yaml` → `mcp_fields.campaign`
   - Conditions: `campaign.status = 'ENABLED'`, date range from config, `metrics.impressions > 0`, campaign name filter from config
   - Write full response to `data/raw-structure.json` under key `"campaigns"`

2. Resource: `ad_group`
   - Fields from `config.yaml` → `mcp_fields.ad_group`
   - Same conditions (add `ad_group.status = 'ENABLED'`)
   - Append to `data/raw-structure.json` under key `"ad_groups"`

**Query B — Queries** (keywords + search terms):

1. Resource: `keyword_view`
   - Fields from `config.yaml` → `mcp_fields.keyword`
   - Same campaign/date conditions, `metrics.impressions > 0`
   - Write to `data/raw-queries.json` under key `"keywords"`

2. Resource: `search_term_view`
   - Fields from `config.yaml` → `mcp_fields.search_term`
   - Same conditions, `metrics.impressions > 10`
   - Append to `data/raw-queries.json` under key `"search_terms"`

**Query C — Assets** (headline + description performance):

1. Resource: `ad_group_ad_asset_view`
   - Fields from `config.yaml` → `mcp_fields.asset`
   - Same campaign/date conditions, `metrics.impressions > 0`
   - Write to `data/raw-assets.json`

**Date range**: Always compute explicit YYYY-MM-DD dates from config. Never use date literals like `LAST_7_DAYS`. Strip hyphens from customer_id before MCP calls.

**Campaign filter**: Build `campaign.name IN ('name1', 'name2', ...)` from the `campaigns` list in config.yaml.

### Step 2: Compress

Run the compression script:

```bash
cd ~/autoresearch-ads && python snapshot.py
```

This reads the 3 raw files and produces `data/snapshot.json`. Archive the snapshot:

```bash
cp data/snapshot.json memory/snapshots/snapshot-$(date +%Y-%m-%d).json
```

Read `data/snapshot.json`. This is your compressed view of the account — use it for all analysis and decisions.

### Step 3: Score Previous Experiments

Read `memory/experiments.jsonl`. Find entries with `"status": "launched"`.

For each launched experiment:
1. Find the matching asset in `snapshot.json` by text (normalize: lowercase, strip whitespace).
2. If found and impressions >= config threshold (`min_impressions`):
   - Record `result_conversion_rate` from the snapshot.
   - Compare to `original_conversion_rate`:
     - **Winner**: result >= original x 1.20 (20% improvement)
     - **Loser**: result <= original x 0.80 (20% decline)
     - **Inconclusive**: between, or insufficient data
   - Set `status` to `"scored"`.
3. If not found or insufficient impressions: leave as `"launched"`.

Write updated experiments back to `memory/experiments.jsonl`.

### Step 4: Analyze

Read `data/snapshot.json`. Identify:

- Which ad groups have the worst conversion rates?
- Which assets have high clicks but low conversions (wasted spend)?
- Which assets convert best? What do they have in common?
- What search terms lead to conversions vs which don't?
- What did you learn from scored experiments in Step 3?

Read `memory/learnings.md` if it exists. Factor in cumulative knowledge.

You decide what matters. There are no prescribed frameworks — look at the data and find the signal.

### Step 5: Generate Copy

Based on your analysis, propose copy changes. For each change:
- **What you're replacing**: the specific asset text and its current conversion_rate.
- **What you're proposing**: new text.
- **Why**: your hypothesis for why this will convert better.
- **Where**: which ad group(s).

Constraints (from config.yaml):
- Headlines: max `headline_max_chars` characters.
- Descriptions: max `description_max_chars` characters.
- Claims must be grounded in `product.md`. Do not invent features or numbers.
- Count characters before finalizing. If over limit, rewrite.

Write proposals to `copy.json`:

```json
{
  "cycle": 5,
  "date": "2026-04-08",
  "proposals": [
    {
      "type": "headline",
      "ad_group": "claude_code",
      "original": "Free with Claude Code Sub",
      "original_conversion_rate": 0.028,
      "new_text": "Your proposed text here",
      "hypothesis": "Why you think this converts better"
    }
  ]
}
```

Git commit: `cycle N: propose copy changes`

### Step 6: Deploy

For each proposal in `copy.json`, use the Google Ads MCP to:
1. Add the new asset (headline or description) to the relevant ad group.
2. If replacing an underperformer, pause or remove the original asset.

Log each action. If an MCP write fails, note the failure and continue with remaining proposals.

### Step 7: Log

1. **experiments.jsonl** — Append one entry per deployed proposal:
```json
{
  "id": "2026-04-08-001",
  "cycle": 5,
  "timestamp": "ISO-8601",
  "type": "headline",
  "ad_group": "claude_code",
  "original": "Free with Claude Code Sub",
  "original_conversion_rate": 0.028,
  "new_text": "Your proposed text here",
  "hypothesis": "Why you think this converts better",
  "status": "launched",
  "result_conversion_rate": null,
  "outcome": null
}
```

2. **results.tsv** — Append one row for this cycle:
```
cycle	date	conv_rate	cost_per_conv	assets_deployed	winners	losers	status	description
```

3. **learnings.md** — Regenerate from experiments.jsonl. List:
   - Patterns that have won (with data)
   - Patterns that have lost (with data)
   - Rules derived from >= 3 data points

Git commit: `cycle N: deploy + log results`

### Step 8: Stop

Print a cycle summary:

```
---
cycle:              5
date:               2026-04-08
conversion_rate:    0.0355
cost_per_conversion: 27.80
assets_deployed:    5
experiments_scored:  3 (2 winners, 1 loser)
cumulative_winners: 8
cumulative_losers:  4
---
```

Stop. The next cycle runs tomorrow when conversion data has accumulated.

## Scoring Rules

- **Primary metric**: `conversion_rate` = conversions / clicks
- **Secondary metric**: `cost_per_conversion` = cost / conversions
- **Winner threshold**: >= 20% improvement in conversion_rate over original
- **Loser threshold**: >= 20% decline in conversion_rate vs original
- **Minimum data**: asset must have >= `min_impressions` (from config) before scoring
- **Confidence**: `high` if impressions >= 1000, `medium` 500-999, `low` 100-499

## results.tsv Format

Tab-separated, NOT comma-separated.

```
cycle	date	conv_rate	cost_per_conv	assets_deployed	winners	losers	status	description
1	2026-04-08	0.0340	29.58	0	0	0	baseline	initial snapshot
2	2026-04-09	0.0355	27.80	5	0	0	keep	replaced 3 headlines in claude_code
```

Status values: `baseline`, `keep`, `discard` (if overall conversion_rate dropped).

## Context Retention

You will forget data between conversation turns. Protect against this:

1. **Never hold raw MCP data in memory** — write it to `data/raw-*.json` immediately.
2. **Always work from files** — read `snapshot.json` for analysis, `experiments.jsonl` for history, `learnings.md` for patterns.
3. **snapshot.py does the compression** — you don't manually summarize MCP data. Run the script.
4. **One snapshot per day** — archived in `memory/snapshots/` for trend analysis.

If you're ever unsure about current state, re-read `data/snapshot.json` and `memory/experiments.jsonl`.

## What You Cannot Do

- Modify `snapshot.py`. It is read-only.
- Modify `config.yaml` (unless the human asks you to).
- Modify `product.md` (unless the human asks you to).
- Invent features or claims not in `product.md`.
- Deploy copy that exceeds character limits.
- Skip the data pull — always start with fresh MCP data.

## What You Can Do

Everything else. There are no prescribed frameworks, angles, styles, or strategies. You look at the data, form hypotheses, test them, and learn from the results. If something works, do more of it. If it doesn't, try something different.

## NEVER STOP

Once the daily cycle begins (after setup), do NOT pause to ask the human if you should continue. Complete all 8 steps. The human may be away from their computer. Run the full cycle autonomously. If an MCP query fails, retry once. If it fails again, log the failure and continue with what you have.

Between cycles (i.e., when you've completed Step 8), you stop. The human or a scheduler triggers the next cycle.
