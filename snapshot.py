"""
Snapshot compression script for autoresearch-ads.
Reads raw MCP data files, computes baselines and classifications,
writes a compressed snapshot.json that fits in LLM context.

Usage: python snapshot.py
"""

import json
import os
import shutil
import statistics
import sys
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
CONFIG_PATH = os.path.join(ROOT, "config.yaml")
RAW_STRUCTURE = os.path.join(DATA_DIR, "raw-structure.json")
RAW_QUERIES = os.path.join(DATA_DIR, "raw-queries.json")
RAW_ASSETS = os.path.join(DATA_DIR, "raw-assets.json")
OUTPUT = os.path.join(DATA_DIR, "snapshot.json")


def load_json(path):
    if not os.path.exists(path):
        print(f"WARNING: {path} not found, using empty data")
        return {}
    with open(path) as f:
        return json.load(f)


def read_config():
    """Load config.yaml. Returns {} if not found or unparseable."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        import yaml
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"WARNING: failed to load config.yaml: {e}")
        return {}


_NAMED_RANGES = {
    "last_7_days": 7,
    "last_14_days": 14,
    "last_30_days": 30,
    "last_60_days": 60,
    "last_90_days": 90,
}


def compute_date_range(config):
    """Return {type, start, end} describing the snapshot's data window.

    Supports named ranges (last_N_days) and explicit start_date/end_date
    overrides in config.data_source. The agent should record the actual
    dates used at data-pull time; this function infers them based on
    'today' as a best-effort fallback.
    """
    ds = (config.get("data_source") or {})
    range_type = ds.get("date_range", "unknown")

    explicit_start = ds.get("start_date")
    explicit_end = ds.get("end_date")
    if explicit_start and explicit_end:
        return {
            "type": "custom",
            "start": str(explicit_start),
            "end": str(explicit_end),
        }

    if range_type in _NAMED_RANGES:
        days = _NAMED_RANGES[range_type]
        # Google Ads' most recent complete day is yesterday.
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=days - 1)
        return {
            "type": range_type,
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

    return {"type": str(range_type), "start": None, "end": None}


def safe_div(a, b, default=0.0):
    if b is None or b == 0:
        return default
    return a / b


def micros_to_dollars(micros):
    if micros is None:
        return 0.0
    return micros / 1_000_000


def median_of(values):
    if not values:
        return 0.0
    return statistics.median(values)


def extract_metric(row, field, default=None):
    """Extract a metric from an MCP row, handling nested dot-notation keys."""
    # MCP responses may use different key formats
    # Try direct key first, then dot-notation traversal
    if field in row:
        return row[field]
    parts = field.split(".")
    current = row
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current


def process_campaigns(raw):
    campaigns_raw = raw.get("campaigns", [])
    if not campaigns_raw:
        return [], 0.0, 0, 0

    campaigns = []
    total_spend_micros = 0
    total_conversions = 0
    total_clicks = 0

    for row in campaigns_raw:
        cost_micros = extract_metric(row, "metrics.cost_micros", 0)
        conversions = extract_metric(row, "metrics.conversions", 0) or 0
        clicks = extract_metric(row, "metrics.clicks", 0) or 0
        impressions = extract_metric(row, "metrics.impressions", 0) or 0
        ctr = extract_metric(row, "metrics.ctr", 0) or 0

        total_spend_micros += cost_micros
        total_conversions += conversions
        total_clicks += clicks

        spend = micros_to_dollars(cost_micros)
        conversion_rate = safe_div(conversions, clicks)
        cost_per_conversion = safe_div(spend, conversions)

        # Impression share
        is_captured = extract_metric(row, "metrics.search_impression_share", 0) or 0
        is_budget_lost = extract_metric(row, "metrics.search_budget_lost_impression_share", 0) or 0
        is_rank_lost = extract_metric(row, "metrics.search_rank_lost_impression_share", 0) or 0

        # Verdict
        if impressions < 100:
            verdict = "low-volume"
        elif is_budget_lost > 0.20:
            verdict = "budget-constrained"
        elif is_rank_lost > 0.30:
            verdict = "rank-constrained"
        else:
            verdict = "healthy"

        campaigns.append({
            "name": extract_metric(row, "campaign.name", "unknown"),
            "id": extract_metric(row, "campaign.id"),
            "status": extract_metric(row, "campaign.status"),
            "bidding_strategy": extract_metric(row, "campaign.bidding_strategy_type"),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 6),
            "spend": round(spend, 2),
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 6),
            "cost_per_conversion": round(cost_per_conversion, 2),
            "impression_share": {
                "captured": is_captured,
                "budget_lost": is_budget_lost,
                "rank_lost": is_rank_lost,
            },
            "verdict": verdict,
        })

    total_spend = micros_to_dollars(total_spend_micros)
    return campaigns, total_spend, total_conversions, total_clicks


def process_ad_groups(raw, total_spend):
    ad_groups_raw = raw.get("ad_groups", [])
    if not ad_groups_raw:
        return [], 0.0

    ad_groups = []
    conversion_rates = []

    for row in ad_groups_raw:
        cost_micros = extract_metric(row, "metrics.cost_micros", 0)
        conversions = extract_metric(row, "metrics.conversions", 0) or 0
        clicks = extract_metric(row, "metrics.clicks", 0) or 0
        impressions = extract_metric(row, "metrics.impressions", 0) or 0
        ctr = extract_metric(row, "metrics.ctr", 0) or 0
        avg_cpc = extract_metric(row, "metrics.average_cpc", 0) or 0

        cost = micros_to_dollars(cost_micros)
        cpc = micros_to_dollars(avg_cpc)
        conversion_rate = safe_div(conversions, clicks)
        cost_per_conversion = safe_div(cost, conversions)
        spend_share = safe_div(cost, total_spend)

        if clicks > 0:
            conversion_rates.append(conversion_rate)

        ad_groups.append({
            "name": extract_metric(row, "ad_group.name", "unknown"),
            "id": extract_metric(row, "ad_group.id"),
            "campaign": extract_metric(row, "campaign.name"),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 6),
            "cost": round(cost, 2),
            "cpc": round(cpc, 2),
            "spend_share": round(spend_share, 4),
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 6),
            "cost_per_conversion": round(cost_per_conversion, 2),
        })

    global_median_conv_rate = round(median_of(conversion_rates), 6)

    # Classify ad groups
    # When median is 0 (sparse conversions), use spend-weighted ranking instead
    for ag in ad_groups:
        cr = ag["conversion_rate"]
        if ag["clicks"] < 10:
            ag["classification"] = "low_volume"
        elif global_median_conv_rate == 0:
            # Sparse data: classify by whether they have any conversions
            if cr > 0:
                ag["classification"] = "converting"
            else:
                ag["classification"] = "no_conversions"
        elif cr >= global_median_conv_rate * 1.5:
            ag["classification"] = "top_performer"
        elif cr >= global_median_conv_rate:
            ag["classification"] = "above_median"
        else:
            ag["classification"] = "below_median"

        # Priority score: high spend + low/no conversions = high priority
        if global_median_conv_rate > 0:
            ag["priority_score"] = round(
                ag["spend_share"] * (1 - safe_div(cr, global_median_conv_rate, 1.0)),
                4
            )
        else:
            # Sparse data: prioritize by spend share * (1 if no conversions, 0.5 if converting)
            no_conv_penalty = 1.0 if ag["conversions"] == 0 else 0.5
            ag["priority_score"] = round(ag["spend_share"] * no_conv_penalty, 4)

    # Sort by priority score descending
    ad_groups.sort(key=lambda x: x["priority_score"], reverse=True)

    return ad_groups, global_median_conv_rate


def process_assets(raw):
    assets_raw = raw if isinstance(raw, list) else raw.get("assets", raw.get("results", []))
    if not assets_raw:
        return {"headlines": [], "descriptions": []}

    headlines = []
    descriptions = []

    for row in assets_raw:
        text = extract_metric(row, "asset.text_asset.text")
        if not text:
            continue

        field_type = extract_metric(row, "ad_group_ad_asset_view.field_type", "")
        impressions = extract_metric(row, "metrics.impressions", 0) or 0
        clicks = extract_metric(row, "metrics.clicks", 0) or 0
        ctr = extract_metric(row, "metrics.ctr", 0) or 0
        conversions = extract_metric(row, "metrics.conversions", 0) or 0
        conversion_rate = safe_div(conversions, clicks)

        asset = {
            "text": text,
            "asset_id": extract_metric(row, "asset.id"),
            "ad_group": extract_metric(row, "ad_group.name", "unknown"),
            "campaign": extract_metric(row, "campaign.name"),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr, 6),
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 6),
        }

        # Route by field type
        field_type_str = str(field_type).upper()
        if "HEADLINE" in field_type_str:
            headlines.append(asset)
        elif "DESCRIPTION" in field_type_str:
            descriptions.append(asset)
        else:
            # Unknown type — include in headlines as fallback
            headlines.append(asset)

    # Classify assets by conversion performance.
    #
    # Two modes:
    #  (1) NORMAL — when there are enough conversions across the cohort
    #      that the median conversion rate is non-zero. Tier by deviation
    #      from median (winner >= 1.2x median, underperformer < 0.8x).
    #  (2) SPARSE — when global median is 0 (most assets have no
    #      conversions). Median-relative classification produces every
    #      asset = winner, which is useless. Fall back to absolute
    #      signal: any asset with conversions > 0 is a winner; assets
    #      with >=50 clicks and 0 conversions are underperformers; the
    #      rest are rotation.
    def classify_assets(assets):
        conv_rates = [a["conversion_rate"] for a in assets if a["clicks"] >= 10]
        median_cr = median_of(conv_rates) if conv_rates else 0
        sparse_mode = (median_cr == 0)

        for asset in assets:
            cr = asset["conversion_rate"]
            clicks = asset["clicks"]
            impressions = asset["impressions"]
            conversions = asset["conversions"]

            if impressions < 100 or clicks < 10:
                asset["tier"] = "insufficient_data"
            elif sparse_mode:
                if conversions > 0:
                    asset["tier"] = "winner"
                elif clicks >= 50:
                    asset["tier"] = "underperformer"
                else:
                    asset["tier"] = "rotation"
            elif cr >= median_cr * 1.2:
                asset["tier"] = "winner"
            elif cr < median_cr * 0.8:
                asset["tier"] = "underperformer"
            else:
                asset["tier"] = "rotation"

            # Conversion impact: deviation from median in normal mode,
            # absolute signal (1.0 if converting, 0.0 if not) in sparse.
            if median_cr > 0:
                asset["conversion_impact"] = round(safe_div(cr, median_cr, 1.0), 3)
            else:
                asset["conversion_impact"] = 1.0 if conversions > 0 else 0.0

        # Sort: underperformers first (highest replacement priority),
        # then winners (success patterns to learn from), then rotation,
        # then insufficient_data. Within each tier, highest impressions
        # first.
        tier_order = {
            "underperformer": 0,
            "winner": 1,
            "rotation": 2,
            "insufficient_data": 3,
        }
        assets.sort(
            key=lambda x: (tier_order.get(x["tier"], 9), -x.get("impressions", 0))
        )
        return assets, median_cr

    headlines, headline_median_cr = classify_assets(headlines)
    descriptions, desc_median_cr = classify_assets(descriptions)

    # Track raw counts before trimming so the agent knows whether
    # what it's looking at is the full set or a sample.
    n_headlines_raw = len(headlines)
    n_descriptions_raw = len(descriptions)

    # Hard cap on assets in the snapshot to keep it under ~30K chars.
    # The cap is enforced even when winners + underperformers exceed
    # the limit (which happens in sparse mode with many converting
    # assets, or in healthy accounts with many high performers).
    MAX_HEADLINES = 60
    MAX_DESCRIPTIONS = 30

    def trim_assets(assets, limit):
        """Hard cap. assets are already sorted by tier priority then
        impressions desc, so simple slicing keeps the most actionable
        items."""
        return assets[:limit]

    headlines = trim_assets(headlines, MAX_HEADLINES)
    descriptions = trim_assets(descriptions, MAX_DESCRIPTIONS)

    return {
        "headlines": headlines,
        "headline_median_conversion_rate": round(headline_median_cr, 6),
        "headline_total_count": n_headlines_raw,
        "headline_shown_count": len(headlines),
        "descriptions": descriptions,
        "description_median_conversion_rate": round(desc_median_cr, 6),
        "description_total_count": n_descriptions_raw,
        "description_shown_count": len(descriptions),
    }


def process_keywords(raw):
    keywords_raw = raw.get("keywords", [])
    if not keywords_raw:
        return []

    keywords = []
    for row in keywords_raw:
        cost_micros = extract_metric(row, "metrics.cost_micros", 0)
        conversions = extract_metric(row, "metrics.conversions", 0) or 0
        clicks = extract_metric(row, "metrics.clicks", 0) or 0
        impressions = extract_metric(row, "metrics.impressions", 0) or 0

        cost = micros_to_dollars(cost_micros)
        conversion_rate = safe_div(conversions, clicks)

        keywords.append({
            "text": extract_metric(row, "ad_group_criterion.keyword.text", ""),
            "match_type": extract_metric(row, "ad_group_criterion.keyword.match_type", ""),
            "ad_group": extract_metric(row, "ad_group.name", ""),
            "campaign": extract_metric(row, "campaign.name", ""),
            "impressions": impressions,
            "clicks": clicks,
            "cost": round(cost, 2),
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 6),
        })

    # Flag waste: high spend, zero or low conversions
    for kw in keywords:
        flags = []
        if kw["cost"] > 10 and kw["conversions"] == 0:
            flags.append("spend_no_conversions")
        if kw["clicks"] > 20 and kw["conversions"] == 0:
            flags.append("clicks_no_conversions")
        kw["flags"] = flags

    # Sort by cost descending (highest spend first)
    keywords.sort(key=lambda x: x["cost"], reverse=True)

    # Keep top 50 by spend to limit snapshot size
    return keywords[:50]


def process_search_terms(raw):
    terms_raw = raw.get("search_terms", [])
    if not terms_raw:
        return []

    terms = []
    for row in terms_raw:
        cost_micros = extract_metric(row, "metrics.cost_micros", 0)
        conversions = extract_metric(row, "metrics.conversions", 0) or 0
        clicks = extract_metric(row, "metrics.clicks", 0) or 0
        impressions = extract_metric(row, "metrics.impressions", 0) or 0

        cost = micros_to_dollars(cost_micros)
        conversion_rate = safe_div(conversions, clicks)

        terms.append({
            "term": extract_metric(row, "search_term_view.search_term", ""),
            "ad_group": extract_metric(row, "ad_group.name", ""),
            "campaign": extract_metric(row, "campaign.name", ""),
            "impressions": impressions,
            "clicks": clicks,
            "cost": round(cost, 2),
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 6),
        })

    # Sort by cost descending
    terms.sort(key=lambda x: x["cost"], reverse=True)

    # Keep top 50 by spend
    return terms[:50]


def build_conversion_insights(ad_groups, assets, search_terms):
    """Extract key conversion signals for quick agent consumption."""
    insights = {}

    # Best/worst converting ad groups
    groups_with_conv = [ag for ag in ad_groups if ag["clicks"] >= 10]
    if groups_with_conv:
        best = max(groups_with_conv, key=lambda x: x["conversion_rate"])
        worst = min(groups_with_conv, key=lambda x: x["conversion_rate"])
        insights["best_converting_ad_group"] = {
            "name": best["name"], "conversion_rate": best["conversion_rate"],
            "conversions": best["conversions"]
        }
        insights["worst_converting_ad_group"] = {
            "name": worst["name"], "conversion_rate": worst["conversion_rate"],
            "conversions": worst["conversions"]
        }

    # High-click, low-conversion assets (wasted potential)
    all_assets = assets.get("headlines", []) + assets.get("descriptions", [])
    wasted = [
        {"text": a["text"], "ad_group": a["ad_group"],
         "clicks": a["clicks"], "conversions": a["conversions"]}
        for a in all_assets
        if a["clicks"] >= 20 and a["conversions"] == 0
    ]
    wasted.sort(key=lambda x: x["clicks"], reverse=True)
    insights["high_click_zero_conversion_assets"] = wasted[:10]

    # Best converting assets
    converting = [
        {"text": a["text"], "ad_group": a["ad_group"],
         "conversion_rate": a["conversion_rate"], "conversions": a["conversions"]}
        for a in all_assets
        if a["conversions"] >= 2 and a["clicks"] >= 10
    ]
    converting.sort(key=lambda x: x["conversion_rate"], reverse=True)
    insights["best_converting_assets"] = converting[:10]

    # Top converting search terms
    converting_terms = [
        {"term": t["term"], "ad_group": t["ad_group"],
         "conversion_rate": t["conversion_rate"], "conversions": t["conversions"]}
        for t in search_terms
        if t["conversions"] >= 1
    ]
    converting_terms.sort(key=lambda x: x["conversions"], reverse=True)
    insights["top_converting_search_terms"] = converting_terms[:10]

    # Wasted search terms (high spend, no conversions)
    wasted_terms = [
        {"term": t["term"], "ad_group": t["ad_group"],
         "cost": t["cost"], "clicks": t["clicks"]}
        for t in search_terms
        if t["cost"] > 5 and t["conversions"] == 0
    ]
    wasted_terms.sort(key=lambda x: x["cost"], reverse=True)
    insights["wasted_search_terms"] = wasted_terms[:10]

    return insights


def main():
    print("Loading config and raw MCP data...")
    config = read_config()
    date_range = compute_date_range(config)
    raw_structure = load_json(RAW_STRUCTURE)
    raw_queries = load_json(RAW_QUERIES)
    raw_assets = load_json(RAW_ASSETS)

    print("Processing campaigns...")
    campaigns, total_spend, total_conversions, total_clicks = process_campaigns(raw_structure)

    print("Processing ad groups...")
    ad_groups, global_median_conv_rate = process_ad_groups(raw_structure, total_spend)

    print("Processing assets...")
    assets = process_assets(raw_assets)

    print("Processing keywords...")
    keywords = process_keywords(raw_queries)

    print("Processing search terms...")
    search_terms = process_search_terms(raw_queries)

    print("Building conversion insights...")
    conversion_insights = build_conversion_insights(ad_groups, assets, search_terms)

    # Compute account summary
    avg_conversion_rate = safe_div(total_conversions, total_clicks)
    avg_cost_per_conversion = safe_div(total_spend, total_conversions)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date_range": date_range,
        "account_summary": {
            "total_spend": round(total_spend, 2),
            "total_clicks": total_clicks,
            "total_conversions": round(total_conversions, 4),
            "avg_conversion_rate": round(avg_conversion_rate, 6),
            "avg_cost_per_conversion": round(avg_cost_per_conversion, 2),
        },
        "global_median_conversion_rate": global_median_conv_rate,
        "campaigns": campaigns,
        "ad_groups": ad_groups,
        "assets": assets,
        "keywords": keywords,
        "search_terms": search_terms,
        "conversion_insights": conversion_insights,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(snapshot, f, indent=2)

    # Auto-archive: copy snapshot to memory/snapshots/snapshot-{date}.json
    # so historical comparisons are always available regardless of whether
    # the agent remembers to run the cp command.
    snapshots_dir = os.path.join(ROOT, "memory", "snapshots")
    os.makedirs(snapshots_dir, exist_ok=True)
    archive_name = f"snapshot-{date.today().isoformat()}.json"
    archive_path = os.path.join(snapshots_dir, archive_name)
    shutil.copy2(OUTPUT, archive_path)
    print(f"Archived: {archive_path}")

    # Print summary using full (untrimmed) tier counts so the human
    # gets an honest view of the underlying classification.
    headlines_shown = assets.get("headlines", [])
    descriptions_shown = assets.get("descriptions", [])
    n_headlines_total = assets.get("headline_total_count", len(headlines_shown))
    n_descriptions_total = assets.get("description_total_count", len(descriptions_shown))

    def count_tier(tier):
        return sum(
            1
            for a in headlines_shown + descriptions_shown
            if a.get("tier") == tier
        )

    n_winners = count_tier("winner")
    n_underperformers = count_tier("underperformer")
    n_rotation = count_tier("rotation")
    n_insufficient = count_tier("insufficient_data")

    range_label = date_range.get("type", "unknown")
    if date_range.get("start") and date_range.get("end"):
        range_label = f'{date_range["type"]} ({date_range["start"]} → {date_range["end"]})'

    print(f"\n--- Snapshot Complete ---")
    print(f"Date range: {range_label}")
    print(f"Campaigns: {len(campaigns)} | Total spend: ${total_spend:,.2f}")
    print(f"Ad groups: {len(ad_groups)} | Median conversion rate: {global_median_conv_rate:.4%}")
    print(
        f"Assets: {len(headlines_shown)}/{n_headlines_total} headlines, "
        f"{len(descriptions_shown)}/{n_descriptions_total} descriptions (shown/total)"
    )
    print(
        f"  In view → winners: {n_winners} | underperformers: {n_underperformers} | "
        f"rotation: {n_rotation} | insufficient_data: {n_insufficient}"
    )
    print(
        f"Conversions: {total_conversions:.2f} | Avg rate: {avg_conversion_rate:.4%} | "
        f"Avg cost: ${avg_cost_per_conversion:,.2f}"
    )
    print(f"Keywords: {len(keywords)} (top 50 by spend)")
    print(f"Search terms: {len(search_terms)} (top 50 by spend)")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
