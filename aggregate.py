"""
Aggregates per-campaign partial JSON files into merged raw data files.
Reads data/partials/*-structure.json, *-queries.json, *-assets.json
Writes data/raw-structure.json, data/raw-queries.json, data/raw-assets.json

Usage: python aggregate.py
"""

import glob
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PARTIALS_DIR = os.path.join(DATA_DIR, "partials")


def merge_files(pattern, keys):
    """Merge partial JSON files by concatenating arrays under each key.

    Returns (merged_dict, file_count, per_file_counts) where
    per_file_counts is a list of {file, counts: {key: n}} dicts so the
    caller can detect campaigns whose pull returned zero rows.
    """
    merged = {k: [] for k in keys}
    files = sorted(glob.glob(os.path.join(PARTIALS_DIR, pattern)))
    per_file_counts = []
    for path in files:
        per_file = {"file": os.path.basename(path), "counts": {k: 0 for k in keys}}
        try:
            with open(path) as f:
                data = json.load(f)
            for key in keys:
                items = data.get(key, [])
                if isinstance(items, list):
                    merged[key].extend(items)
                    per_file["counts"][key] = len(items)
                elif isinstance(items, dict) and "result" in items:
                    merged[key].extend(items["result"])
                    per_file["counts"][key] = len(items["result"])
        except (json.JSONDecodeError, Exception) as e:
            print(f"WARNING: Failed to read {path}: {e}")
            per_file["error"] = str(e)
        per_file_counts.append(per_file)
    return merged, len(files), per_file_counts


def _warn_empty(per_file_counts, label):
    """Log a warning for any partial whose row counts are all zero.

    A zero-row partial usually means: (a) the campaign name in
    config.yaml doesn't match anything in the live account, (b) the
    campaign was paused for the entire date range, or (c) the data
    pull silently failed. Either way, the agent should know.
    """
    for entry in per_file_counts:
        counts = entry.get("counts", {})
        total = sum(counts.values())
        if total == 0 and "error" not in entry:
            print(
                f"  ⚠️  {entry['file']}: 0 rows for {label}. "
                "Campaign may be paused, misnamed, or have no data in range."
            )


FIELD_TYPE_MAP = {2: "HEADLINE", 3: "DESCRIPTION"}


def _normalize_structure(data):
    """Ensure structure rows use MCP-style nested objects.

    The agent may write flat rows like {"name": "...", "metrics": {...}}
    instead of {"campaign": {"name": "..."}, "metrics": {...}}.  This
    detects flat rows and wraps them so snapshot.py's dot-notation
    traversal works correctly.
    """
    # Fix campaigns
    fixed_campaigns = []
    for row in data.get("campaigns", []):
        if "campaign" in row and isinstance(row["campaign"], dict):
            fixed_campaigns.append(row)  # already nested
        elif "name" in row and "metrics" in row:
            metrics = row.pop("metrics")
            fixed_campaigns.append({"campaign": row, "metrics": metrics})
        else:
            fixed_campaigns.append(row)

    # Build campaign name lookup for ad groups
    campaign_names = {}
    for row in fixed_campaigns:
        c = row.get("campaign", {})
        rn = c.get("resource_name")
        name = c.get("name")
        if rn and name:
            campaign_names[rn] = name

    # Fix ad groups
    fixed_ad_groups = []
    for row in data.get("ad_groups", []):
        if "ad_group" in row and isinstance(row["ad_group"], dict):
            # Already nested — ensure campaign name is populated
            rn = row.get("campaign", {}).get("resource_name")
            if rn and rn in campaign_names and "name" not in row.get("campaign", {}):
                row["campaign"]["name"] = campaign_names[rn]
            fixed_ad_groups.append(row)
        elif "name" in row and "metrics" in row:
            metrics = row.pop("metrics")
            campaign_rn = row.pop("campaign", None)
            campaign_obj = {"resource_name": campaign_rn} if campaign_rn else {}
            if campaign_rn and campaign_rn in campaign_names:
                campaign_obj["name"] = campaign_names[campaign_rn]
            fixed_ad_groups.append({
                "ad_group": row,
                "campaign": campaign_obj,
                "metrics": metrics,
            })
        else:
            fixed_ad_groups.append(row)

    return {"campaigns": fixed_campaigns, "ad_groups": fixed_ad_groups}


def _normalize_queries(data):
    """Ensure query rows use MCP-style nested objects."""
    fixed_keywords = []
    for row in data.get("keywords", []):
        if "ad_group_criterion" in row:
            fixed_keywords.append(row)  # already nested
        elif "text" in row:
            metrics = row.pop("metrics", {})
            fixed_keywords.append({
                "ad_group_criterion": {
                    "keyword": {
                        "text": row.pop("text", ""),
                        "match_type": row.pop("match_type", None),
                    }
                },
                "ad_group": {"name": row.pop("ad_group", "")},
                "campaign": {"name": row.pop("campaign", "")},
                "metrics": metrics,
            })
        else:
            fixed_keywords.append(row)

    fixed_search_terms = []
    for row in data.get("search_terms", []):
        if "search_term_view" in row:
            fixed_search_terms.append(row)  # already nested
        elif "search_term" in row:
            metrics = row.pop("metrics", {})
            fixed_search_terms.append({
                "search_term_view": {
                    "search_term": row.pop("search_term", ""),
                    "status": row.pop("status", None),
                },
                "ad_group": {"name": row.pop("ad_group", "")},
                "campaign": {"name": row.pop("campaign", "")},
                "metrics": metrics,
            })
        else:
            fixed_search_terms.append(row)

    return {"keywords": fixed_keywords, "search_terms": fixed_search_terms}


def _normalize_assets(data):
    """Ensure asset rows use MCP-style nested objects and string field_type."""
    fixed = []
    for row in data.get("assets", []):
        # Wrap flat rows
        if "asset" not in row and "text" in row:
            metrics = row.pop("metrics", {})
            field_type = row.pop("field_type", None)
            row = {
                "asset": {
                    "text_asset": {"text": row.pop("text", "")},
                    "id": row.pop("asset_id", None),
                },
                "ad_group": {"name": row.pop("ad_group", "")},
                "ad_group_ad_asset_view": {"field_type": field_type},
                "campaign": {"name": row.pop("campaign", "")},
                "metrics": metrics,
            }

        # Convert numeric field_type to string
        view = row.get("ad_group_ad_asset_view", {})
        ft = view.get("field_type")
        if ft in FIELD_TYPE_MAP:
            view["field_type"] = FIELD_TYPE_MAP[ft]

        fixed.append(row)
    return {"assets": fixed}


def main():
    if not os.path.isdir(PARTIALS_DIR):
        print(f"ERROR: {PARTIALS_DIR} not found. Run data pull first.")
        return

    # Aggregate structure
    structure, n, struct_counts = merge_files(
        "*-structure.json", ["campaigns", "ad_groups"]
    )
    structure = _normalize_structure(structure)
    out = os.path.join(DATA_DIR, "raw-structure.json")
    with open(out, "w") as f:
        json.dump(structure, f, indent=2)
    print(
        f"raw-structure.json: {n} partials → "
        f"{len(structure['campaigns'])} campaigns, {len(structure['ad_groups'])} ad groups"
    )
    _warn_empty(struct_counts, "campaigns/ad_groups")

    # Aggregate queries
    queries, n, query_counts = merge_files(
        "*-queries.json", ["keywords", "search_terms"]
    )
    queries = _normalize_queries(queries)
    out = os.path.join(DATA_DIR, "raw-queries.json")
    with open(out, "w") as f:
        json.dump(queries, f, indent=2)
    print(
        f"raw-queries.json: {n} partials → "
        f"{len(queries['keywords'])} keywords, {len(queries['search_terms'])} search terms"
    )
    _warn_empty(query_counts, "keywords/search_terms")

    # Aggregate assets
    assets, n, asset_counts = merge_files("*-assets.json", ["assets"])
    assets = _normalize_assets(assets)
    out = os.path.join(DATA_DIR, "raw-assets.json")
    with open(out, "w") as f:
        json.dump(assets, f, indent=2)
    print(f"raw-assets.json: {n} partials → {len(assets['assets'])} assets")
    _warn_empty(asset_counts, "assets")


if __name__ == "__main__":
    main()
