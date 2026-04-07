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
    """Merge partial JSON files by concatenating arrays under each key."""
    merged = {k: [] for k in keys}
    files = sorted(glob.glob(os.path.join(PARTIALS_DIR, pattern)))
    for path in files:
        try:
            with open(path) as f:
                data = json.load(f)
            for key in keys:
                items = data.get(key, [])
                if isinstance(items, list):
                    merged[key].extend(items)
                elif isinstance(items, dict) and "result" in items:
                    merged[key].extend(items["result"])
        except (json.JSONDecodeError, Exception) as e:
            print(f"WARNING: Failed to read {path}: {e}")
    return merged, len(files)


def main():
    if not os.path.isdir(PARTIALS_DIR):
        print(f"ERROR: {PARTIALS_DIR} not found. Run data pull first.")
        return

    # Aggregate structure
    structure, n = merge_files("*-structure.json", ["campaigns", "ad_groups"])
    out = os.path.join(DATA_DIR, "raw-structure.json")
    with open(out, "w") as f:
        json.dump(structure, f, indent=2)
    print(f"raw-structure.json: {n} partials → {len(structure['campaigns'])} campaigns, {len(structure['ad_groups'])} ad groups")

    # Aggregate queries
    queries, n = merge_files("*-queries.json", ["keywords", "search_terms"])
    out = os.path.join(DATA_DIR, "raw-queries.json")
    with open(out, "w") as f:
        json.dump(queries, f, indent=2)
    print(f"raw-queries.json: {n} partials → {len(queries['keywords'])} keywords, {len(queries['search_terms'])} search terms")

    # Aggregate assets
    assets, n = merge_files("*-assets.json", ["assets"])
    out = os.path.join(DATA_DIR, "raw-assets.json")
    with open(out, "w") as f:
        json.dump(assets, f, indent=2)
    print(f"raw-assets.json: {n} partials → {len(assets['assets'])} assets")


if __name__ == "__main__":
    main()
