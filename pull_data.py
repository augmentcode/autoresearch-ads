"""
Prepare and finalize Google Ads MCP data pulls for autoresearch-ads.

This script cannot call Cosmos MCP tools by itself. Instead, it makes the
expert workflow repeatable by generating the exact per-campaign MCP requests,
validating the partial JSON files written from those requests, then running the
aggregation and snapshot steps.

Usage:
  python3 pull_data.py discover
  python3 pull_data.py reconcile
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
DISCOVERY_PLAN_PATH = DATA_DIR / "campaign-discovery-plan.json"
LIVE_CAMPAIGNS_PATH = DATA_DIR / "live-campaigns.json"
RECONCILIATION_PATH = DATA_DIR / "campaign-reconciliation.json"

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


def _campaigns_from_config(config):
    return list(dict.fromkeys(config.get("campaigns", [])))


def _nested_get(value, path):
    if not isinstance(value, dict):
        return None
    if path in value:
        return value[path]
    current = value
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        if part in current:
            current = current[part]
            continue
        camel = re.sub(r"_([a-z])", lambda match: match.group(1).upper(), part)
        if camel in current:
            current = current[camel]
            continue
        return None
    return current


def _campaign_name_from_row(row):
    if isinstance(row, str):
        return row
    if not isinstance(row, dict):
        return None
    for path in ("campaign.name", "name"):
        value = _nested_get(row, path)
        if value:
            return str(value)
    return None


def extract_live_campaign_names(payload, name_pattern="_cosmos"):
    rows = payload.get("campaigns", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return []
    names = []
    for row in rows:
        name = _campaign_name_from_row(row)
        if name and name_pattern in name:
            names.append(name)
    return sorted(dict.fromkeys(names))


def build_discovery_plan(config, name_pattern="_cosmos"):
    fields = ["campaign.name", "campaign.id", "campaign.status", "campaign.advertising_channel_type"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "customer_id": _customer_id(config),
        "name_pattern": name_pattern,
        "mcp": {
            "tool": "search",
            "arguments": {
                "customer_id": _customer_id(config),
                "resource": "campaign",
                "fields": fields,
                "conditions": [
                    "campaign.status = 'ENABLED'",
                    "campaign.advertising_channel_type = 'SEARCH'",
                    f"campaign.name LIKE '%{name_pattern}%'",
                ],
                "orderings": ["campaign.name ASC"],
                "limit": 1000,
            },
        },
        "output": {"path": str(LIVE_CAMPAIGNS_PATH.relative_to(ROOT)), "key": "campaigns"},
    }


def build_campaign_reconciliation(config, live_payload, name_pattern="_cosmos"):
    configured = _campaigns_from_config(config)
    live = extract_live_campaign_names(live_payload, name_pattern=name_pattern)
    configured_set = set(configured)
    live_set = set(live)
    live_not_configured = sorted(live_set - configured_set)
    configured_not_live = sorted(configured_set - live_set)
    plan_campaigns = list(dict.fromkeys(configured + live_not_configured))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "name_pattern": name_pattern,
        "configured_campaigns": configured,
        "live_campaigns": live,
        "live_not_configured": live_not_configured,
        "configured_not_live": configured_not_live,
        "plan_campaigns": plan_campaigns,
        "drift": bool(live_not_configured or configured_not_live),
    }


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


def build_pull_plan(config, today=None, enabled_only=False, reconciliation=None):
    date_range = compute_date_range(config, today=today)
    requests = []
    partials = []
    campaigns = _campaigns_from_config(config)
    if reconciliation and reconciliation.get("plan_campaigns"):
        campaigns = list(dict.fromkeys(reconciliation["plan_campaigns"]))

    for campaign in campaigns:
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
        "campaign_count": len(campaigns),
        "configured_campaign_count": len(_campaigns_from_config(config)),
        "campaign_reconciliation": reconciliation,
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
    reconciliation = None
    if args.reconciliation and args.reconciliation.exists():
        with open(args.reconciliation) as f:
            reconciliation = json.load(f)
    plan = build_pull_plan(config, enabled_only=args.enabled_only, reconciliation=reconciliation)
    output = write_plan(plan, args.output)
    print(f"Wrote {output}")
    print(f"Campaigns: {plan['campaign_count']} | MCP requests: {plan['request_count']}")
    if reconciliation and reconciliation.get("drift"):
        print(
            "Campaign drift: "
            f"+{len(reconciliation.get('live_not_configured', []))} live not configured, "
            f"-{len(reconciliation.get('configured_not_live', []))} configured not live"
        )
    print(f"Date range: {plan['date_range']['start']} → {plan['date_range']['end']}")
    print("Next: execute each plan['requests'] MCP search and write rows into data/partials/*.json")
    return 0


def cmd_discover(args):
    config = read_config(args.config)
    plan = build_discovery_plan(config, name_pattern=args.name_pattern)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"Wrote {args.output}")
    print(f"Next: execute plan['mcp'] and write rows to {plan['output']['path']} under key {plan['output']['key']}")
    return 0


def cmd_reconcile(args):
    config = read_config(args.config)
    if not args.live_campaigns.exists():
        print(f"ERROR: missing {args.live_campaigns}. Run discover and write live campaigns first.")
        return 1
    with open(args.live_campaigns) as f:
        live_payload = json.load(f)
    reconciliation = build_campaign_reconciliation(config, live_payload, name_pattern=args.name_pattern)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(reconciliation, f, indent=2)
    print(f"Wrote {args.output}")
    print(f"Configured: {len(reconciliation['configured_campaigns'])} | Live: {len(reconciliation['live_campaigns'])} | Plan: {len(reconciliation['plan_campaigns'])}")
    if reconciliation["live_not_configured"]:
        print("Live not configured: " + ", ".join(reconciliation["live_not_configured"]))
    if reconciliation["configured_not_live"]:
        print("Configured not live: " + ", ".join(reconciliation["configured_not_live"]))
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

    discover = subparsers.add_parser("discover", help="write Google Ads campaign discovery MCP request plan")
    discover.add_argument("--config", type=Path, default=CONFIG_PATH)
    discover.add_argument("--output", type=Path, default=DISCOVERY_PLAN_PATH)
    discover.add_argument("--name-pattern", default="_cosmos")
    discover.set_defaults(func=cmd_discover)

    reconcile = subparsers.add_parser("reconcile", help="compare live campaigns to config and write reconciliation")
    reconcile.add_argument("--config", type=Path, default=CONFIG_PATH)
    reconcile.add_argument("--live-campaigns", type=Path, default=LIVE_CAMPAIGNS_PATH)
    reconcile.add_argument("--output", type=Path, default=RECONCILIATION_PATH)
    reconcile.add_argument("--name-pattern", default="_cosmos")
    reconcile.set_defaults(func=cmd_reconcile)

    plan = subparsers.add_parser("plan", help="write data/pull-plan.json")
    plan.add_argument("--config", type=Path, default=CONFIG_PATH)
    plan.add_argument("--output", type=Path, default=PLAN_PATH)
    plan.add_argument("--reconciliation", type=Path, default=RECONCILIATION_PATH)
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