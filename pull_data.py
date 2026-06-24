"""
Prepare and finalize Google Ads MCP data pulls for autoresearch-ads.

This script cannot call Cosmos MCP tools by itself. Instead, it makes the
expert workflow repeatable by generating the exact per-campaign MCP requests,
validating the partial JSON files written from those requests, then running the
aggregation and snapshot steps.

Usage:
  python3 pull_data.py discover [--data-root <run-dir>]
  python3 pull_data.py reconcile [--data-root <run-dir>]
  python3 pull_data.py plan [--data-root <run-dir>]
  python3 pull_data.py materialize [--data-root <run-dir>]
  python3 pull_data.py write-partial [--data-root <run-dir>] --request-index N --response-file <file>
  python3 pull_data.py validate [--data-root <run-dir>]
  python3 pull_data.py finish [--data-root <run-dir>]

Generated artifacts default to data/ or $AUTORESEARCH_DATA_ROOT when set.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
ENV_DATA_ROOT = "AUTORESEARCH_DATA_ROOT"
DEFAULT_DATA_DIR = ROOT / "data"
DATA_DIR = DEFAULT_DATA_DIR
ARTIFACT_TOOL = "search_to_artifact"
ARTIFACT_COMPRESSION = "none"
PLAN_PATH = DATA_DIR / "pull-plan.json"
DISCOVERY_PLAN_PATH = DATA_DIR / "campaign-discovery-plan.json"
LIVE_CAMPAIGNS_PATH = DATA_DIR / "live-campaigns.json"
RECONCILIATION_PATH = DATA_DIR / "campaign-reconciliation.json"


def resolve_data_root(data_root=None):
    """Return the directory that stores generated pull artifacts."""
    value = data_root or os.environ.get(ENV_DATA_ROOT) or DEFAULT_DATA_DIR
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def data_path(filename, data_root=None):
    return resolve_data_root(data_root) / filename


def _resolve_data_path(path, data_root=None):
    """Resolve a plan path, supporting legacy repo-relative data/... paths."""
    path = Path(path)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] == "data":
        return ROOT / path
    return resolve_data_root(data_root) / path


def _arg_data_root(args):
    return resolve_data_root(getattr(args, "data_root", None))


def _default_arg_path(args, attr, filename):
    explicit = getattr(args, attr, None)
    return explicit if explicit is not None else data_path(filename, _arg_data_root(args))

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
        "storage": {"path_mode": "data-root-relative", "data_root_env": ENV_DATA_ROOT},
        "customer_id": _customer_id(config),
        "name_pattern": name_pattern,
        "mcp": {
            "tool": ARTIFACT_TOOL,
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
                "compression": ARTIFACT_COMPRESSION,
            },
        },
        "output": {"path": "live-campaigns.json", "key": "campaigns"},
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
            "path": f"partials/{_slug(campaign)}-{partial_kind}.json",
            "key": target_key,
        },
        "mcp": {
            "tool": ARTIFACT_TOOL,
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
                "compression": ARTIFACT_COMPRESSION,
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
                "structure": {"path": f"partials/{slug}-structure.json", "keys": ["campaigns", "ad_groups"]},
                "queries": {"path": f"partials/{slug}-queries.json", "keys": ["keywords", "search_terms"]},
                "assets": {"path": f"partials/{slug}-assets.json", "keys": ["assets"]},
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
        "storage": {"path_mode": "data-root-relative", "data_root_env": ENV_DATA_ROOT},
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


def _normalize_response_data(response_data, key):
    """Normalize response data to a list of rows."""
    if isinstance(response_data, dict):
        if "rows" in response_data:
            return response_data["rows"]
        elif key in response_data:
            return response_data[key]
        else:
            # Wrap single row dict in a list
            return [response_data]
    return response_data


def write_partial(plan, request_index, response_data, output_path=None, output_key=None, data_root=None):
    """Write response data into the correct partial file/key from a plan request."""
    if output_path is not None:
        # Discovery or generic mode
        target_path = _resolve_data_path(output_path, data_root)
        key = output_key
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            with open(target_path) as f:
                data = json.load(f)
        else:
            data = {}
        data[key] = response_data
        with open(target_path, "w") as f:
            json.dump(data, f, indent=2)
        return target_path, key, len(response_data)

    # Plan mode
    request = plan["requests"][request_index]
    partial = request["partial"]
    target_path = _resolve_data_path(partial["path"], data_root)
    key = partial["key"]

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        with open(target_path) as f:
            data = json.load(f)
    else:
        data = {}

    data[key] = response_data
    with open(target_path, "w") as f:
        json.dump(data, f, indent=2)

    return target_path, key, len(response_data)


def validate_partials(plan, data_root=None):
    errors = []
    summaries = []
    for partial in plan.get("partials", []):
        for kind, spec in partial.get("files", {}).items():
            path = _resolve_data_path(spec["path"], data_root)
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
    data_root = _arg_data_root(args)
    output_path = _default_arg_path(args, "output", "pull-plan.json")
    reconciliation_path = _default_arg_path(args, "reconciliation", "campaign-reconciliation.json")
    reconciliation = None
    if reconciliation_path.exists():
        with open(reconciliation_path) as f:
            reconciliation = json.load(f)
    plan = build_pull_plan(config, enabled_only=args.enabled_only, reconciliation=reconciliation)
    output = write_plan(plan, output_path)
    print(f"Wrote {output}")
    print(f"Data root: {data_root}")
    print(f"Campaigns: {plan['campaign_count']} | MCP requests: {plan['request_count']}")
    if reconciliation and reconciliation.get("drift"):
        print(
            "Campaign drift: "
            f"+{len(reconciliation.get('live_not_configured', []))} live not configured, "
            f"-{len(reconciliation.get('configured_not_live', []))} configured not live"
        )
    print(f"Date range: {plan['date_range']['start']} → {plan['date_range']['end']}")
    print(
        f"Next: run materialize to see missing partials and required {ARTIFACT_TOOL} requests, "
        "download each artifact JSON, then use write-partial per request"
    )
    return 0


def cmd_discover(args):
    config = read_config(args.config)
    plan = build_discovery_plan(config, name_pattern=args.name_pattern)
    output_path = _default_arg_path(args, "output", "campaign-discovery-plan.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"Wrote {output_path}")
    print(f"Data root: {_arg_data_root(args)}")
    print(
        f"Next: execute plan['mcp'] via {ARTIFACT_TOOL}, download the artifact JSON, "
        "and run write-partial --discovery --response-file <path> to persist rows"
    )
    return 0


def cmd_reconcile(args):
    config = read_config(args.config)
    live_campaigns_path = _default_arg_path(args, "live_campaigns", "live-campaigns.json")
    output_path = _default_arg_path(args, "output", "campaign-reconciliation.json")
    if not live_campaigns_path.exists():
        print(f"ERROR: missing {live_campaigns_path}. Run discover and write live campaigns first.")
        return 1
    with open(live_campaigns_path) as f:
        live_payload = json.load(f)
    reconciliation = build_campaign_reconciliation(config, live_payload, name_pattern=args.name_pattern)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(reconciliation, f, indent=2)
    print(f"Wrote {output_path}")
    print(f"Configured: {len(reconciliation['configured_campaigns'])} | Live: {len(reconciliation['live_campaigns'])} | Plan: {len(reconciliation['plan_campaigns'])}")
    if reconciliation["live_not_configured"]:
        print("Live not configured: " + ", ".join(reconciliation["live_not_configured"]))
    if reconciliation["configured_not_live"]:
        print("Configured not live: " + ", ".join(reconciliation["configured_not_live"]))
    return 0


def cmd_write_partial(args):
    data_root = _arg_data_root(args)
    # Read response data
    if args.response_file:
        with open(args.response_file) as f:
            response_data = json.load(f)
    elif args.response_json:
        response_data = json.loads(args.response_json)
    else:
        print("ERROR: --response-file or --response-json required")
        return 1

    if args.discovery:
        discovery_plan_path = _default_arg_path(args, "discovery_plan", "campaign-discovery-plan.json")
        plan = load_plan(discovery_plan_path)
        target_path = _resolve_data_path(plan["output"]["path"], data_root)
        key = plan["output"]["key"]
        response_data = _normalize_response_data(response_data, key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            with open(target_path) as f:
                data = json.load(f)
        else:
            data = {}
        data[key] = response_data
        with open(target_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote {len(response_data)} rows to {target_path} under key {key}")
        return 0

    if args.request_index is None:
        print("ERROR: --request-index required (unless --discovery)")
        return 1

    plan_path = _default_arg_path(args, "plan", "pull-plan.json")
    plan = load_plan(plan_path)
    try:
        request = plan["requests"][args.request_index]
    except IndexError:
        print(f"ERROR: invalid request index {args.request_index}")
        return 1

    partial = request["partial"]
    target_path = _resolve_data_path(partial["path"], data_root)
    key = partial["key"]
    response_data = _normalize_response_data(response_data, key)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        with open(target_path) as f:
            data = json.load(f)
    else:
        data = {}

    data[key] = response_data
    with open(target_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote {len(response_data)} rows to {target_path} under key {key}")
    return 0


def cmd_materialize(args):
    data_root = _arg_data_root(args)
    plan = load_plan(_default_arg_path(args, "plan", "pull-plan.json"))
    errors = []
    missing_keys_map = {}

    for partial in plan.get("partials", []):
        for kind, spec in partial.get("files", {}).items():
            path = _resolve_data_path(spec["path"], data_root)
            missing_keys = []
            if not path.exists():
                errors.append(f"missing {spec['path']}")
                missing_keys = spec.get("keys", [])
            else:
                try:
                    with open(path) as f:
                        data = json.load(f)
                except Exception as exc:
                    errors.append(f"invalid JSON {spec['path']}: {exc}")
                    missing_keys = spec.get("keys", [])
                else:
                    for key in spec.get("keys", []):
                        value = data.get(key)
                        if not isinstance(value, list):
                            errors.append(f"{spec['path']} missing list key {key}")
                            missing_keys.append(key)

            missing_keys_map[spec["path"]] = missing_keys

    # Find requests that write to missing file/keys
    missing_requests = []
    for i, req in enumerate(plan.get("requests", [])):
        req_partial = req["partial"]
        if req_partial["path"] in missing_keys_map and req_partial["key"] in missing_keys_map[req_partial["path"]]:
            missing_requests.append((i, req))

    # Remove duplicates while preserving order
    seen = set()
    unique_missing = []
    for item in missing_requests:
        if item[0] not in seen:
            seen.add(item[0])
            unique_missing.append(item)

    if not errors:
        print("All partials present and valid. Nothing to materialize.")
        return 0

    if args.dry_run:
        print("Missing partials (dry-run):")
        for error in errors:
            print(f"  {error}")
        print(f"\nMissing requests: {len(unique_missing)}")
        for i, req in unique_missing:
            print(f"  [{i}] {req['campaign']} {req['partial']['key']}: {req['mcp']['arguments']['resource']}")
        return 0

    print("Missing partials:")
    for error in errors:
        print(f"  {error}")
    print(f"\nTo materialize missing requests, run each {ARTIFACT_TOOL} request, download the artifact JSON, and then:")
    for i, req in unique_missing:
        print(f"  python3 pull_data.py write-partial --data-root {data_root} --request-index {i} --response-file /tmp/resp_{i}.json")
    print("\nOr use --dry-run to see the full request list.")
    return 1


def cmd_validate(args):
    data_root = _arg_data_root(args)
    plan = load_plan(_default_arg_path(args, "plan", "pull-plan.json"))
    errors, summaries = validate_partials(plan, data_root=data_root)
    for campaign, kind, path, counts in summaries:
        count_text = ", ".join(f"{key}={value}" for key, value in counts.items())
        print(f"OK {campaign} {kind}: {path} ({count_text})")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("\nRun 'python3 pull_data.py materialize' to see missing requests and how to persist them.")
        return 1
    print("All partials valid")
    return 0


def _write_run_manifest(data_root, plan, summaries):
    row_counts = {}
    partial_files = set()
    for _campaign, _kind, path, counts in summaries:
        partial_files.add(path)
        for key, value in counts.items():
            row_counts[key] = row_counts.get(key, 0) + value

    snapshot_path = data_root / "snapshot.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_root": str(data_root),
        "date_range": plan.get("date_range"),
        "campaign_count": plan.get("campaign_count"),
        "request_count": plan.get("request_count"),
        "partial_file_count": len(partial_files),
        "row_counts": row_counts,
        "validation_status": "passed",
        "snapshot_path": str(snapshot_path),
    }

    manifest_path = data_root / "run-manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    latest_root = data_root.parent.parent if data_root.parent.name == "runs" else data_root
    latest_path = latest_root / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(latest_path, "w") as f:
        json.dump({"latest_run": str(data_root), "manifest": str(manifest_path)}, f, indent=2)

    print(f"Run manifest: {manifest_path}")
    print(f"Latest pointer: {latest_path}")


def cmd_finish(args):
    data_root = _arg_data_root(args)
    status = cmd_validate(args)
    if status != 0:
        return status
    subprocess.run([sys.executable, "aggregate.py", "--data-root", str(data_root)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "snapshot.py", "--data-root", str(data_root)], cwd=ROOT, check=True)
    plan = load_plan(_default_arg_path(args, "plan", "pull-plan.json"))
    _, summaries = validate_partials(plan, data_root=data_root)
    _write_run_manifest(data_root, plan, summaries)
    return 0


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Prepare and finalize autoresearch Google Ads MCP pulls")
    subparsers = parser.add_subparsers(dest="command")
    data_root_parent = argparse.ArgumentParser(add_help=False)
    data_root_parent.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help=f"generated artifact root; defaults to ${ENV_DATA_ROOT} or data/",
    )

    discover = subparsers.add_parser("discover", parents=[data_root_parent], help="write Google Ads campaign discovery MCP request plan")
    discover.add_argument("--config", type=Path, default=CONFIG_PATH)
    discover.add_argument("--output", type=Path, default=None)
    discover.add_argument("--name-pattern", default="_cosmos")
    discover.set_defaults(func=cmd_discover)

    reconcile = subparsers.add_parser("reconcile", parents=[data_root_parent], help="compare live campaigns to config and write reconciliation")
    reconcile.add_argument("--config", type=Path, default=CONFIG_PATH)
    reconcile.add_argument("--live-campaigns", type=Path, default=None)
    reconcile.add_argument("--output", type=Path, default=None)
    reconcile.add_argument("--name-pattern", default="_cosmos")
    reconcile.set_defaults(func=cmd_reconcile)

    plan = subparsers.add_parser("plan", parents=[data_root_parent], help="write pull-plan.json in the data root")
    plan.add_argument("--config", type=Path, default=CONFIG_PATH)
    plan.add_argument("--output", type=Path, default=None)
    plan.add_argument("--reconciliation", type=Path, default=None)
    plan.add_argument("--enabled-only", action="store_true", help="add ENABLED status filters to structure requests")
    plan.set_defaults(func=cmd_plan)

    write_partial = subparsers.add_parser("write-partial", parents=[data_root_parent], help="write an MCP response into a plan partial file")
    write_partial.add_argument("--plan", type=Path, default=None)
    write_partial.add_argument("--discovery", action="store_true", help="use discovery plan instead of pull plan")
    write_partial.add_argument("--discovery-plan", type=Path, default=None)
    write_partial.add_argument("--request-index", type=int, default=None)
    write_partial.add_argument("--response-file", type=Path, default=None)
    write_partial.add_argument("--response-json", type=str, default=None)
    write_partial.set_defaults(func=cmd_write_partial)

    materialize = subparsers.add_parser("materialize", parents=[data_root_parent], help="check missing partials and report required MCP requests")
    materialize.add_argument("--plan", type=Path, default=None)
    materialize.add_argument("--dry-run", action="store_true", help="print missing requests without generating commands")
    materialize.set_defaults(func=cmd_materialize)

    validate = subparsers.add_parser("validate", parents=[data_root_parent], help="validate partial files from the pull plan")
    validate.add_argument("--plan", type=Path, default=None)
    validate.set_defaults(func=cmd_validate)

    finish = subparsers.add_parser("finish", parents=[data_root_parent], help="validate partials, aggregate, and snapshot")
    finish.add_argument("--plan", type=Path, default=None)
    finish.set_defaults(func=cmd_finish)

    parser.set_defaults(func=cmd_plan, config=CONFIG_PATH, output=None, reconciliation=None, enabled_only=False, data_root=None)
    return parser


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())