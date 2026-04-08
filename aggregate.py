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


def main():
    if not os.path.isdir(PARTIALS_DIR):
        print(f"ERROR: {PARTIALS_DIR} not found. Run data pull first.")
        return

    # Aggregate structure
    structure, n, struct_counts = merge_files(
        "*-structure.json", ["campaigns", "ad_groups"]
    )
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
    out = os.path.join(DATA_DIR, "raw-assets.json")
    with open(out, "w") as f:
        json.dump(assets, f, indent=2)
    print(f"raw-assets.json: {n} partials → {len(assets['assets'])} assets")
    _warn_empty(asset_counts, "assets")


if __name__ == "__main__":
    main()
