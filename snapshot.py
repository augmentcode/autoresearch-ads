"""
Snapshot compression script for autoresearch-ads.
Reads raw MCP data files, computes baselines and classifications,
writes a compressed snapshot.json that fits in LLM context.

Usage: python snapshot.py
"""

import json
import os
import statistics
import sys
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
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

    # Classify assets by conversion performance
    def classify_assets(assets):
        conv_rates = [a["conversion_rate"] for a in assets if a["clicks"] >= 10]
        median_cr = median_of(conv_rates) if conv_rates else 0

        for asset in assets:
            cr = asset["conversion_rate"]
            if asset["impressions"] < 100:
                asset["tier"] = "insufficient_data"
            elif cr >= median_cr * 1.2 and asset["clicks"] >= 10:
                asset["tier"] = "winner"
            elif cr < median_cr * 0.8 and asset["clicks"] >= 10:
                asset["tier"] = "underperformer"
            else:
                asset["tier"] = "rotation"

            # Conversion impact: how much conversion rate deviates from median
            asset["conversion_impact"] = round(safe_div(cr, median_cr, 1.0), 3) if median_cr > 0 else 0

        # Sort: underperformers first (highest priority for replacement)
        tier_order = {"underperformer": 0, "rotation": 1, "insufficient_data": 2, "winner": 3}
        assets.sort(key=lambda x: (tier_order.get(x["tier"], 9), -x.get("impressions", 0)))
        return assets, median_cr

    headlines, headline_median_cr = classify_assets(headlines)
    descriptions, desc_median_cr = classify_assets(descriptions)

    # Trim to keep snapshot under ~30K chars for assets
    # Keep: all winners, all underperformers, top rotation by impressions
    MAX_HEADLINES = 60
    MAX_DESCRIPTIONS = 30

    def trim_assets(assets, limit):
        # Always keep winners and underperformers
        keep = [a for a in assets if a["tier"] in ("winner", "underperformer")]
        rest = [a for a in assets if a["tier"] not in ("winner", "underperformer")]
        # Fill remaining slots with highest-impression rotation/insufficient
        rest.sort(key=lambda x: x["impressions"], reverse=True)
        remaining = limit - len(keep)
        if remaining > 0:
            keep.extend(rest[:remaining])
        return keep

    headlines = trim_assets(headlines, MAX_HEADLINES)
    descriptions = trim_assets(descriptions, MAX_DESCRIPTIONS)

    return {
        "headlines": headlines,
        "headline_median_conversion_rate": round(headline_median_cr, 6),
        "headline_total_count": len(headlines),
        "descriptions": descriptions,
        "description_median_conversion_rate": round(desc_median_cr, 6),
        "description_total_count": len(descriptions),
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
    print("Loading raw MCP data...")
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
        "account_summary": {
            "total_spend": round(total_spend, 2),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
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

    # Print summary
    n_headlines = len(assets.get("headlines", []))
    n_descriptions = len(assets.get("descriptions", []))
    n_winners = sum(1 for a in assets.get("headlines", []) + assets.get("descriptions", [])
                    if a.get("tier") == "winner")
    n_underperformers = sum(1 for a in assets.get("headlines", []) + assets.get("descriptions", [])
                           if a.get("tier") == "underperformer")

    print(f"\n--- Snapshot Complete ---")
    print(f"Campaigns: {len(campaigns)} | Total spend: ${total_spend:,.2f}")
    print(f"Ad groups: {len(ad_groups)} | Median conversion rate: {global_median_conv_rate:.4%}")
    print(f"Assets: {n_headlines} headlines, {n_descriptions} descriptions")
    print(f"  Winners: {n_winners} | Underperformers: {n_underperformers}")
    print(f"Conversions: {total_conversions} | Avg rate: {avg_conversion_rate:.4%} | Avg cost: ${avg_cost_per_conversion:,.2f}")
    print(f"Keywords: {len(keywords)} (top 50 by spend)")
    print(f"Search terms: {len(search_terms)} (top 50 by spend)")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
