"""
Slack notification for autoresearch-ads cycle completion.
Reads snapshot.json + results.tsv + experiments.jsonl, sends a cycle summary.

Usage: python notify.py
Requires SLACK_WEBHOOK_URL env var (or in .env file).
"""

import json
import os
import ssl
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(ROOT, "data", "snapshot.json")
RESULTS = os.path.join(ROOT, "results.tsv")
EXPERIMENTS = os.path.join(ROOT, "memory", "experiments.jsonl")


def load_env():
    env_path = os.path.join(ROOT, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def read_json(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def read_last_tsv_row(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    if len(lines) < 2:
        return None
    header = lines[0].split("\t")
    values = lines[-1].split("\t")
    return dict(zip(header, values))


def count_experiments():
    if not os.path.exists(EXPERIMENTS):
        return {"total": 0, "launched": 0, "winners": 0, "losers": 0}
    counts = {"total": 0, "launched": 0, "winners": 0, "losers": 0}
    with open(EXPERIMENTS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                exp = json.loads(line)
                counts["total"] += 1
                outcome = exp.get("outcome")
                status = exp.get("status")
                if status == "launched":
                    counts["launched"] += 1
                elif outcome == "winner":
                    counts["winners"] += 1
                elif outcome == "loser":
                    counts["losers"] += 1
            except json.JSONDecodeError:
                continue
    return counts


def fmt_pct(value):
    if value is None:
        return "—"
    return f"{float(value) * 100:.2f}%"


def fmt_money(value):
    if value is None:
        return "—"
    return f"${float(value):,.2f}"


def build_message():
    snapshot = read_json(SNAPSHOT)
    last_cycle = read_last_tsv_row(RESULTS)
    exp_counts = count_experiments()

    if not snapshot or not last_cycle:
        return {
            "text": "autoresearch-ads cycle completed (no data to summarize)",
            "blocks": [
                {"type": "header", "text": {"type": "plain_text",
                    "text": "autoresearch-ads — Cycle Complete"}},
                {"type": "section", "text": {"type": "mrkdwn",
                    "text": "No snapshot or results data found."}},
            ]
        }

    summary = snapshot.get("account_summary", {})
    cycle = last_cycle.get("cycle", "?")
    date = last_cycle.get("date", "?")
    status = last_cycle.get("status", "?")
    description = last_cycle.get("description", "")
    assets_deployed = last_cycle.get("assets_deployed", "0")

    conv_rate = summary.get("avg_conversion_rate")
    cost_per_conv = summary.get("avg_cost_per_conversion")
    total_spend = summary.get("total_spend")
    total_conversions = summary.get("total_conversions", 0)

    # Status emoji
    status_emoji = {"baseline": "📊", "keep": "✅", "discard": "❌"}.get(status, "❓")

    blocks = []

    # Header
    blocks.append({"type": "header", "text": {"type": "plain_text",
        "text": f"autoresearch-ads — Cycle {cycle}"}})

    # Main metrics
    blocks.append({"type": "section", "text": {"type": "mrkdwn",
        "text": (
            f"*Date:* {date}  |  *Status:* {status_emoji} {status}\n"
            f"*Conversion Rate:* {fmt_pct(conv_rate)}  |  "
            f"*Cost/Conversion:* {fmt_money(cost_per_conv)}\n"
            f"*Spend:* {fmt_money(total_spend)}  |  "
            f"*Conversions:* {total_conversions}"
        )}})

    blocks.append({"type": "divider"})

    # What happened this cycle
    blocks.append({"type": "section", "text": {"type": "mrkdwn",
        "text": (
            f"*This cycle:* {description}\n"
            f"*Assets deployed:* {assets_deployed}\n"
            f"*Experiments:* {exp_counts['total']} total — "
            f"{exp_counts['winners']} winners, {exp_counts['losers']} losers, "
            f"{exp_counts['launched']} pending"
        )}})

    # Top ad groups by conversion rate
    ad_groups = snapshot.get("ad_groups", [])
    if ad_groups:
        blocks.append({"type": "divider"})
        ag_lines = []
        for ag in ad_groups[:6]:
            cr = ag.get("conversion_rate", 0)
            conv = ag.get("conversions", 0)
            cls = ag.get("classification", "")
            emoji = {"top_performer": "🟢", "above_median": "🟡",
                     "below_median": "🔴", "low_volume": "⚪"}.get(cls, "⚪")
            ag_lines.append(
                f"{emoji} *{ag['name']}* — {cr:.2%} conv rate, {conv} conversions"
            )
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": "*Ad Group Performance*\n" + "\n".join(ag_lines)}})

    # Footer
    blocks.append({"type": "context", "elements": [
        {"type": "mrkdwn",
         "text": "autoresearch-ads | autonomous ad optimization"}
    ]})

    return {
        "text": f"autoresearch-ads cycle {cycle} — conv rate {fmt_pct(conv_rate)} — {status}",
        "blocks": blocks[:50],
    }


def send_slack(webhook_url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except (ImportError, Exception):
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return True
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"Slack error: {e}", file=sys.stderr)
        return False


def main():
    load_env()
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set — skipping notification")
        sys.exit(0)

    payload = build_message()
    if send_slack(webhook_url, payload):
        print("Slack notification sent")
    else:
        print("Slack notification failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
