"""
Prepare and finalize Google Ads MCP data pulls for autoresearch-ads.

This script cannot call Cosmos MCP tools by itself. Instead, it makes the
expert workflow repeatable by generating the exact per-campaign MCP requests,
validating the partial JSON files written from those requests, then running the
aggregation and snapshot steps.

Usage:
  python3 pull_data.py plan
  python3 pull_data.py validate
  python3 pull_data.py finish
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
DATA_DIR = ROOT / "data"
PLAN_PATH = DATA_DIR / "pull-plan.json"

_NAMED_RANGES = {
    "last_7_days": 7,
    "last_14_days": 14,
    "last_30_days": 30,
    "last_60_days": 60,
    "last_90_days": 90,
}


def _strip_inline_comment(line):
    return line.split("#", 1)[0].rstrip()


def _parse_scalar(value):
    return value.strip().strip('"').strip("'")


def _fallback_config(path):
    """Parse the config sections needed for data pulls without PyYAML."""
    config = {"data_source": {}, "campaigns": [], "mcp_fields": {}}
    section = None
    current_resource = None

    with open(path) as f:
        for raw_line in f:
            line = _strip_inline_comment(raw_line)
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip())
            stripped = line.strip()

            if indent == 0:
                section = None
                current_resource = None
                if stripped.endswith(":"):
                    candidate = stripped[:-1]
                    if candidate in config:
                        section = candidate
                continue

            if section == "data_source" and ":" in stripped:
                key, value = stripped.split(":", 1)
                if value.strip():
                    config["data_source"][key.strip()] = _parse_scalar(value)
                continue

            if section == "campaigns" and stripped.startswith("- "):
                config["campaigns"].append(_parse_scalar(stripped[2:]))
                continue

            if section == "mcp_fields":
                if indent == 2 and stripped.endswith(":"):
                    current_resource = stripped[:-1]
                    config["mcp_fields"][current_resource] = []
                elif current_resource and stripped.startswith("- "):
                    config["mcp_fields"][current_resource].append(
                        _parse_scalar(stripped[2:])
                    )

    return config


def read_config(path=CONFIG_PATH):
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception as exc:
        print(f"WARNING: using fallback config parser: {exc}")
        return _fallback_config(path)


def compute_date_range(config, today=None):
    ds = config.get("data_source") or {}
    range_type = ds.get("date_range", "unknown")
    explicit_start = ds.get("start_date")
    explicit_end = ds.get("end_date")

    if explicit_start and explicit_end:
        return {"type": "custom", "start": str(explicit_start), "end": str(explicit_end)}

    if range_type in _NAMED_RANGES:
        today = today or date.today()
        end = today - timedelta(days=1)
        start = end - timedelta(days=_NAMED_RANGES[range_type] - 1)
        return {"type": range_type, "start": start.isoformat(), "end": end.isoformat()}

    return {"type": str(range_type), "start": None, "end": None}


def _customer_id(config):
    return str((config.get("data_source") or {}).get("customer_id", "")).replace("-", "")


def _slug(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def _campaign_condition(campaign_name):
    escaped = campaign_name.replace("'", "\\'")
    return f"campaign.name = '{escaped}'"


def _conditions(campaign_name, date_range, impression_floor, status_field=None, enabled_only=False):
    conditions = [_campaign_condition(campaign_name)]
    if enabled_only and status_field:
        conditions.append(f"{status_field} = 'ENABLED'")
    if date_range.get("start") and date_range.get("end"):
        conditions.extend([
            f"segments.date >= '{date_range['start']}'",
            f"segments.date <= '{date_range['end']}'",
        ])
    conditions.append(f"metrics.impressions > {impression_floor}")
    return conditions


def _request(config, campaign, date_range, partial_kind, target_key, resource, field_key,
             impression_floor=0, status_field=None, enabled_only=False):
    fields = (config.get("mcp_fields") or {}).get(field_key, [])
    return {
        "campaign": campaign,
        "partial": {
            "kind": partial_kind,
            "path": f"data/partials/{_slug(campaign)}-{partial_kind}.json",
            "key": target_key,
        },
        "mcp": {
            "tool": "search",
            "arguments": {
                "customer_id": _customer_id(config),
                "resource": resource,
                "fields": fields,
                "conditions": _conditions(
                    campaign,
                    date_range,
                    impression_floor,
                    status_field=status_field,
                    enabled_only=enabled_only,
                ),
                "orderings": ["metrics.impressions DESC"],
                "limit": 5000,
            },
        },
    }


def build_pull_plan(config, today=None, enabled_only=False):
    date_range = compute_date_range(config, today=today)
    requests = []
    partials = []

    for campaign in config.get("campaigns", []):
        slug = _slug(campaign)
        partials.append({
            "campaign": campaign,
            "files": {
                "structure": {"path": f"data/partials/{slug}-structure.json", "keys": ["campaigns", "ad_groups"]},
                "queries": {"path": f"data/partials/{slug}-queries.json", "keys": ["keywords", "search_terms"]},
                "assets": {"path": f"data/partials/{slug}-assets.json", "keys": ["assets"]},
            },
        })
        requests.extend([
            _request(config, campaign, date_range, "structure", "campaigns", "campaign", "campaign", 0, "campaign.status", enabled_only),
            _request(config, campaign, date_range, "structure", "ad_groups", "ad_group", "ad_group", 0, "ad_group.status", enabled_only),
            _request(config, campaign, date_range, "queries", "keywords", "keyword_view", "keyword", 0, None, enabled_only),
            _request(config, campaign, date_range, "queries", "search_terms", "search_term_view", "search_term", 10, None, enabled_only),
            _request(config, campaign, date_range, "assets", "assets", "ad_group_ad_asset_view", "asset", 0, None, enabled_only),
        ])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "customer_id": _customer_id(config),
        "date_range": date_range,
        "enabled_only": enabled_only,
        "campaign_count": len(config.get("campaigns", [])),
        "request_count": len(requests),
        "partials": partials,
        "requests": requests,
    }


def write_plan(plan, output_path=PLAN_PATH):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(plan, f, indent=2)
    return output_path


def load_plan(path=PLAN_PATH):
    with open(path) as f:
        return json.load(f)


def validate_partials(plan):
    errors = []
    summaries = []
    for partial in plan.get("partials", []):
        for kind, spec in partial.get("files", {}).items():
            path = ROOT / spec["path"]
            if not path.exists():
                errors.append(f"missing {spec['path']}")
                continue
            try:
                with open(path) as f:
                    data = json.load(f)
            except Exception as exc:
                errors.append(f"invalid JSON {spec['path']}: {exc}")
                continue
            counts = {}
            for key in spec.get("keys", []):
                value = data.get(key)
                if not isinstance(value, list):
                    errors.append(f"{spec['path']} missing list key {key}")
                    continue
                counts[key] = len(value)
            summaries.append((partial["campaign"], kind, spec["path"], counts))
    return errors, summaries


def cmd_plan(args):
    config = read_config(args.config)
    plan = build_pull_plan(config, enabled_only=args.enabled_only)
    output = write_plan(plan, args.output)
    print(f"Wrote {output}")
    print(f"Campaigns: {plan['campaign_count']} | MCP requests: {plan['request_count']}")
    print(f"Date range: {plan['date_range']['start']} → {plan['date_range']['end']}")
    print("Next: execute each plan['requests'] MCP search and write rows into data/partials/*.json")
    return 0


def cmd_validate(args):
    plan = load_plan(args.plan)
    errors, summaries = validate_partials(plan)
    for campaign, kind, path, counts in summaries:
        count_text = ", ".join(f"{key}={value}" for key, value in counts.items())
        print(f"OK {campaign} {kind}: {path} ({count_text})")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("All partials valid")
    return 0


def cmd_finish(args):
    status = cmd_validate(args)
    if status != 0:
        return status
    subprocess.run([sys.executable, "aggregate.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "snapshot.py"], cwd=ROOT, check=True)
    return 0


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Prepare and finalize autoresearch Google Ads MCP pulls")
    subparsers = parser.add_subparsers(dest="command")

    plan = subparsers.add_parser("plan", help="write data/pull-plan.json")
    plan.add_argument("--config", type=Path, default=CONFIG_PATH)
    plan.add_argument("--output", type=Path, default=PLAN_PATH)
    plan.add_argument("--enabled-only", action="store_true", help="add ENABLED status filters to structure requests")
    plan.set_defaults(func=cmd_plan)

    validate = subparsers.add_parser("validate", help="validate data/partials files from the pull plan")
    validate.add_argument("--plan", type=Path, default=PLAN_PATH)
    validate.set_defaults(func=cmd_validate)

    finish = subparsers.add_parser("finish", help="validate partials, aggregate, and snapshot")
    finish.add_argument("--plan", type=Path, default=PLAN_PATH)
    finish.set_defaults(func=cmd_finish)

    parser.set_defaults(func=cmd_plan, config=CONFIG_PATH, output=PLAN_PATH, enabled_only=False)
    return parser


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())