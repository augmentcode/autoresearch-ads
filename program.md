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

**All data is pulled per-campaign to prevent MCP response truncation.** A single bulk query across all campaigns silently drops data.

Initialize partial file directory:

```bash
mkdir -p data/partials
```

**FOR each campaign** in the `campaigns` list from config.yaml:

Print: `📡 [{i}/{total}] Fetching: {campaign_name}`

1. **Structure** — campaign + ad group metrics
   - Query `campaign` resource with `campaign.name = '{campaign_name}'`
     - Fields from `config.yaml` → `mcp_fields.campaign`
     - Conditions: `campaign.status = 'ENABLED'`, date range, `metrics.impressions > 0`
   - Query `ad_group` resource with `campaign.name = '{campaign_name}'`
     - Fields from `config.yaml` → `mcp_fields.ad_group`
     - Conditions: `ad_group.status = 'ENABLED'`, date range, `metrics.impressions > 0`
   - Write to `data/partials/{campaign_name}-structure.json`:
     ```json
     {"campaigns": [...], "ad_groups": [...]}
     ```

2. **Queries** — keywords + search terms
   - Query `keyword_view` with `campaign.name = '{campaign_name}'`
     - Fields from `config.yaml` → `mcp_fields.keyword`
     - Conditions: date range, `metrics.impressions > 0`
   - Query `search_term_view` with `campaign.name = '{campaign_name}'`
     - Fields from `config.yaml` → `mcp_fields.search_term`
     - Conditions: date range, `metrics.impressions > 10`
   - Write to `data/partials/{campaign_name}-queries.json`:
     ```json
     {"keywords": [...], "search_terms": [...]}
     ```

3. **Assets** — headline + description performance
   - Query `ad_group_ad_asset_view` with `campaign.name = '{campaign_name}'`
     - Fields from `config.yaml` → `mcp_fields.asset`
     - Conditions: date range, `metrics.impressions > 0`
   - Write to `data/partials/{campaign_name}-assets.json`:
     ```json
     {"assets": [...]}
     ```

Print: `  ✓ {campaign_name} done ({N} assets, {M} keywords, {P} search terms)`

**END FOR**

**Aggregate** — After ALL campaigns are fetched, merge the partial files:

```bash
cd ~/autoresearch-ads && python3 aggregate.py
```

This reads all `data/partials/*-structure.json`, `*-queries.json`, and `*-assets.json` files and produces:
- `data/raw-structure.json` — all campaigns + ad groups merged
- `data/raw-queries.json` — all keywords + search terms merged
- `data/raw-assets.json` — all assets merged

**Date range**: Always compute explicit YYYY-MM-DD dates from config. Never use date literals like `LAST_7_DAYS`. Strip hyphens from customer_id before MCP calls.

### Step 2: Compress

Run the compression script:

```bash
cd ~/autoresearch-ads && python3 snapshot.py
```

This reads the 3 raw files and produces `data/snapshot.json`. Archive the snapshot:

```bash
cp data/snapshot.json memory/snapshots/snapshot-$(date +%Y-%m-%d).json
```

Read `data/snapshot.json`. This is your compressed view of the account — use it for all analysis and decisions.

### Step 3: Score Previous Experiments

Read `memory/experiments.jsonl`. Find entries with `"status": "launched"`.
If there are none, this step is a no-op — skip to Step 4.

For each launched experiment, branch on `experiment_type`:

**`ad_variation`** — Google runs the A/B test; ask it for the verdict.
1. Call the `google-ads-write` MCP tool `get_experiment_status` with:
   - `customer_id` from `config.yaml`
   - `experiment_id` from the logged entry
2. The tool returns JSON with this shape:
   ```json
   {
     "experiment": {"resource_name": "...", "status": "RUNNING", ...},
     "arms": [
       {"name": "control",   "role": "control",   "metrics": {...}},
       {"name": "treatment", "role": "treatment", "metrics": {"conversion_rate": 0.034, ...}}
     ],
     "comparison": {
       "control_conversion_rate":   0.029,
       "treatment_conversion_rate": 0.034,
       "lift_vs_control":           0.172
     },
     "hint": "..."
   }
   ```
   The experiment status uses Google's enum: `SETUP`, `INITIATED`,
   `RUNNING`, `GRADUATED`, `HALTED`, `PROMOTED`, `REMOVED`.
3. Score using `comparison.lift_vs_control`:
   - `SETUP` / `INITIATED` / `RUNNING` → leave as `"launched"` (still collecting)
   - `lift_vs_control >= thresholds.winner` → status `"scored"`, outcome `"winner"`
   - `lift_vs_control <= thresholds.loser` → status `"scored"`, outcome `"loser"`
     (`thresholds.loser` is negative in `config.yaml`)
   - Otherwise → status `"scored"`, outcome `"inconclusive"`
4. Record `result_conversion_rate` = `comparison.treatment_conversion_rate`.
5. If `comparison.control_conversion_rate` is `0` or `null`, fall back to
   the **zero-original rules** (see direct_swap step 3 below) using the
   treatment arm's absolute metrics.
6. If outcome is `"winner"`, you may call `graduate_experiment` in Step 7
   of the NEXT cycle to promote it (always `validate_only: true` first).

**`direct_swap`** (default, and any legacy entry missing `experiment_type`)
— text-match against the snapshot.
1. **Normalize both `new_text` and the snapshot asset text** before
   comparing. Apply, in order:
   - Unicode NFKC normalization (`unicodedata.normalize("NFKC", s)`)
   - Lowercase
   - Strip leading/trailing whitespace
   - Strip trailing `.`, `!`, `?`, `,`, `:`, `;`
   - Replace smart quotes (`'`, `'`, `"`, `"`) with straight quotes
   - Replace en-dash (`–`) and em-dash (`—`) with hyphen (`-`)
2. **Scope the match to the entry's `ad_group`** — only compare against
   assets where `snapshot_asset["ad_group"] == entry["ad_group"]`. If
   multiple matches survive, pick the one with the most impressions.
3. If no asset found: leave as `"launched"`. If found but
   `impressions < thresholds.min_impressions`: leave as `"launched"`.
4. Compare `result_conversion_rate` (from the snapshot) to
   `original_conversion_rate`:
   - **If `original_conversion_rate > 0`** (the normal case):
     - **Winner**: `result >= original × (1 + thresholds.winner)`
     - **Loser**: `result <= original × (1 + thresholds.loser)` — note
       that `thresholds.loser` is negative in `config.yaml`
     - **Inconclusive**: between
   - **If `original_conversion_rate == 0`** (zero-original rules):
     The multiplicative thresholds collapse (`0 × anything == 0`), so
     use absolute floors instead:
     - **Winner**: `result_conversion_rate >= 0.02` AND `conversions >= 3`
     - **Loser**: `clicks >= 50` AND `conversions == 0`
     - **Inconclusive**: anything else (record `result_conversion_rate`
       anyway so the next cycle can re-score with more data)
5. Set `status` to `"scored"` and record the outcome and
   `result_conversion_rate`.

**Writing updates back to `memory/experiments.jsonl`** — use atomic
write semantics: write the new contents to a temp file in the same
directory, then `os.replace(temp_path, target_path)`. This guarantees
the file is never partially written even if the agent crashes mid-cycle.

```python
import os, tempfile
fd, temp_path = tempfile.mkstemp(
    prefix="experiments-",
    suffix=".jsonl.tmp",
    dir=os.path.dirname(EXPERIMENTS_PATH),
)
with os.fdopen(fd, "w") as f:
    for entry in entries:
        f.write(json.dumps(entry) + "\n")
os.replace(temp_path, EXPERIMENTS_PATH)
```

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

**Critical: only propose swaps on assets that are in a CURRENTLY-ENABLED
RSA.** The snapshot's `assets` and `conversion_insights` sections
include data from paused ads too — those ads still hold 30-day metrics
even though they no longer serve. If you propose replacing a headline
that lives in a paused ad, Step 7 will skip the proposal because there
is nothing to swap. Before writing each proposal, verify the original
text exists in the current winning ad by calling
`get_ad(ad_group_id, select_winning=true)` and checking its `headlines`
list. (You can batch this: call `get_ad` once per ad group you have
proposals for, then validate all your proposals against the returned
headlines.)

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

### Step 6: Review Gate

**STOP here and present your proposals to the human.** Print a clear summary:

```
═══════════════════════════════════════════════════
  PROPOSALS READY FOR REVIEW — Cycle N
═══════════════════════════════════════════════════

  [For each proposal:]
  AD GROUP: claude_code
  REPLACE:  "Old Headline Text" (conv_rate: 0.15%)
  WITH:     "New Headline Text" (27 chars)
  WHY:      Your hypothesis

  ───────────────────────────────────────────────
  Total: N proposals across M ad groups
═══════════════════════════════════════════════════
```

Wait for the human to respond. They will either:
- **Approve all**: proceed to Step 7 (Deploy)
- **Approve some**: they'll tell you which ones. Deploy only those.
- **Reject all**: skip Step 7, go straight to Step 8 (Log). Log proposals with status `"rejected"` instead of `"launched"`.
- **Request changes**: revise the proposals and present again.

Do NOT proceed to deployment without explicit human approval.

### Step 7: Deploy

**Background.** Google Ads blocks `AdService.MutateAds UPDATE` on responsive
search ad headlines and descriptions — they are immutable once the ad is
created. You cannot edit individual assets on an existing RSA. To change
copy, you must either (a) create a new RSA and pause the old one ("direct
swap") or (b) run an Ad Variation experiment (statistical A/B test).

Both paths go through the `google-ads-write` MCP, which handles all
reads and writes. It exposes:
- `search` — queries any Google Ads resource (campaigns, ad groups,
  keywords, search terms, assets, etc.)
- `get_ad` — fetches an RSA's full content (headlines, descriptions,
  final URLs, pinned positions). Used in Step 7.2 below.
- `create_responsive_search_ad` — creates a new RSA in an ad group
- `pause_ad` — pauses an existing ad by resource name
- `create_ad_variation` — creates an Ad Variation experiment against a base ad
- `get_experiment_status` — reads experiment status + per-arm metrics
  (used in Step 3)
- `graduate_experiment` — promotes a winning variation

**Decision: direct_swap vs ad_variation.**
- **direct_swap (default)** — Use for every deploy unless you have a
  specific reason to run a statistical test. Faster, simpler, produces an
  immediate copy change. The new RSA starts serving immediately and the old
  one stops.
- **ad_variation** — Use when you want statistical confidence on a small
  change (e.g. swapping a single headline) and you're willing to wait 1–2
  weeks for Google to collect data. The base RSA keeps serving alongside
  the variant as the control. Never pause the base ad in this path.

Default to `direct_swap` unless a proposal in `copy.json` explicitly sets
`"experiment_type": "ad_variation"`.

**1. Group approved proposals by `ad_group`.**
   All proposals for the same ad group become a single new RSA creation.
   You cannot swap different headlines on the same RSA in the same cycle
   with separate calls — you must build the full new ad.

**2. For each ad_group, fetch the current winning RSA.** Look up the
ad group's resource name from `snapshot.json` (`ad_groups[].id`) and
construct it as `customers/{customer_id}/adGroups/{id}`. Then call
the `google-ads-write` MCP tool `get_ad`:

```json
{
  "customer_id": "9232939339",
  "ad_group_id": "customers/9232939339/adGroups/191506291605",
  "select_winning": true
}
```

`get_ad` returns JSON with this shape:

```json
{
  "resource_name": "customers/9232939339/adGroupAds/191506291605~803604473915",
  "ad_id": "803604473915",
  "status": "ENABLED",
  "final_urls": ["https://www.example.com/landing"],
  "headlines": [
    {"text": "Headline One", "pinned_field": null},
    {"text": "Headline Two", "pinned_field": "HEADLINE_1"}
  ],
  "descriptions": [
    {"text": "Description One", "pinned_field": null}
  ],
  "metrics": {"impressions": 2232, "clicks": 69, "conversions": 0}
}
```

Call this the *base ad*. `resource_name` is `old_ad_id`; `headlines` /
`descriptions` are the starting set; preserve each headline's
`pinned_field` (already normalised — `null` means unpinned).

**3. Build the new RSA's copy.**
   - Start with the base ad's headlines and descriptions.
   - For each proposal in the group, **find the matching base asset by
     normalised text comparison**. Apply, in order, to both `original`
     and the base asset's `text`:
     - Unicode NFKC normalization
     - Lowercase
     - Strip leading/trailing whitespace
     - Strip trailing `.`, `!`, `?`, `,`, `:`, `;`
     - Replace smart quotes (`'`, `'`, `"`, `"`) with straight quotes
     - Replace en-dash (`–`) and em-dash (`—`) with hyphen (`-`)
     If no asset matches the proposal's `original`, log a warning and
     skip that proposal — do NOT silently invent the swap.
   - Replace the matched asset's `text` with `new_text` while
     preserving its `pinned_field`.
   - RSAs require 3–15 headlines and 2–4 descriptions; keep the base ad's
     count.
   - Final URL = `base.final_urls[0]`.
   - Count characters on every headline (≤ `constraints.headline_max_chars`)
     and description (≤ `constraints.description_max_chars`) before calling
     the API. Rewrite if over.

**4. Deploy — `direct_swap` path.**
   a. Call `create_responsive_search_ad` with `validate_only: true`. If it
      returns an error, fix the inputs and retry from step 3.
   b. Call `create_responsive_search_ad` with `validate_only: false`.
      Record the returned resource name as `new_ad_id`.
   c. Call `pause_ad` with `ad_id = old_ad_id` and `validate_only: true`
      first, then `validate_only: false`. Record success.
   d. If pause fails, DO NOT revert the new ad — you now have two enabled
      RSAs in the ad group, which is still better than zero. Log the
      failure and continue.

**5. Deploy — `ad_variation` path (only when explicitly requested).**
   a. Call `create_ad_variation` with `validate_only: true`.
   b. Call `create_ad_variation` with `validate_only: false`. Record the
      returned experiment resource name as `experiment_id` and the variant
      arm's new ad as `new_ad_id`. `old_ad_id` = the base ad whose variation
      this is.
   c. Do NOT call `pause_ad` — the base ad must keep serving as the control.

**6. Error handling.**
   Always run `validate_only: true` first on every mutate call. If any
   write step fails, log the failure (with `error_code` and `request_id`)
   and continue with the remaining ad groups. Partial deploys are
   acceptable; all-or-nothing is not required.

Log each action with full resource names as you go — these are the inputs
to Step 8 and to Step 3 of future cycles.

### Step 8: Log

1. **experiments.jsonl** — Append one entry per deployed proposal:
```json
{
  "id": "2026-04-08-001",
  "cycle": 5,
  "timestamp": "ISO-8601",
  "experiment_type": "direct_swap",
  "type": "headline",
  "ad_group": "claude_code",
  "original": "Free with Claude Code Sub",
  "original_conversion_rate": 0.028,
  "new_text": "Your proposed text here",
  "hypothesis": "Why you think this converts better",
  "old_ad_id": "customers/9232939339/adGroupAds/123~456",
  "new_ad_id": "customers/9232939339/adGroupAds/123~789",
  "experiment_id": null,
  "status": "launched",
  "result_conversion_rate": null,
  "outcome": null
}
```

Field reference for the write-MCP-era fields:
- `experiment_type` — `"direct_swap"` (default) or `"ad_variation"`.
- `old_ad_id` — resource name of the ad that was paused (direct_swap) or
  of the base ad the variation runs against (ad_variation). Never null on
  a successful deploy.
- `new_ad_id` — resource name of the newly created ad. Never null on a
  successful deploy.
- `experiment_id` — resource name of the `experiment` resource for
  ad_variation entries; always null for direct_swap.

If a proposal fails to deploy, append it anyway with
`"status": "deployment_failed"`, `"failure_reason": "<error_code> <message>"`,
and `new_ad_id` / `experiment_id` set to null. Legacy entries from before
this schema change (no `experiment_type` field) are treated as `direct_swap`
by Step 3.

2. **results.tsv** — Append one row for this cycle:
```
cycle	date	conv_rate	cost_per_conv	assets_deployed	winners	losers	status	description
```

3. **learnings.md** — Regenerate from experiments.jsonl. List:
   - Patterns that have won (with data)
   - Patterns that have lost (with data)
   - Rules derived from >= 3 data points

Git commit: `cycle N: deploy + log results`

### Step 9: Stop

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

Once the daily cycle begins (after setup), do NOT pause to ask the human if you should continue. Complete all steps — but always stop at Step 6 (Review Gate) for human approval before deploying. The human may be away from their computer. Run the full cycle autonomously. If an MCP query fails, retry once. If it fails again, log the failure and continue with what you have.

Between cycles (i.e., when you've completed Step 8), you stop. The human or a scheduler triggers the next cycle.
