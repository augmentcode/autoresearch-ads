import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import pull_data


CONFIG = """
data_source:
  type: mcp
  customer_id: "123-456-7890"
  date_range: last_30_days

campaigns:
  - campaign_one
  - campaign_two

mcp_fields:
  campaign:
    - campaign.name
    - metrics.clicks
  ad_group:
    - ad_group.name
  keyword:
    - ad_group_criterion.keyword.text
  search_term:
    - search_term_view.search_term
  asset:
    - asset.text_asset.text
"""


class PullDataTests(unittest.TestCase):
    def test_fallback_config_reads_pull_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(CONFIG)

            config = pull_data._fallback_config(path)

        self.assertEqual(config["data_source"]["customer_id"], "123-456-7890")
        self.assertEqual(config["campaigns"], ["campaign_one", "campaign_two"])
        self.assertEqual(config["mcp_fields"]["campaign"], ["campaign.name", "metrics.clicks"])

    def test_build_pull_plan_has_expected_requests_and_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(CONFIG)
            config = pull_data._fallback_config(path)

        plan = pull_data.build_pull_plan(config, today=date(2026, 6, 23))

        self.assertEqual(plan["customer_id"], "1234567890")
        self.assertEqual(plan["date_range"]["start"], "2026-05-24")
        self.assertEqual(plan["date_range"]["end"], "2026-06-22")
        self.assertEqual(plan["campaign_count"], 2)
        self.assertEqual(plan["request_count"], 10)
        self.assertEqual(plan["requests"][0]["partial"]["key"], "campaigns")
        self.assertEqual(plan["requests"][0]["partial"]["path"], "partials/campaign_one-structure.json")
        self.assertEqual(plan["requests"][0]["mcp"]["tool"], "search_to_artifact")
        self.assertEqual(plan["requests"][0]["mcp"]["arguments"]["compression"], "none")
        self.assertEqual(plan["storage"]["path_mode"], "data-root-relative")

    def test_campaign_reconciliation_adds_live_not_configured_to_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(CONFIG)
            config = pull_data._fallback_config(path)
        live_payload = {
            "campaigns": [
                {"campaign": {"name": "campaign_two"}},
                {"campaign": {"name": "campaign_three_cosmos"}},
                {"campaign": {"name": "ignore_me"}},
            ]
        }

        reconciliation = pull_data.build_campaign_reconciliation(config, live_payload, name_pattern="campaign")
        plan = pull_data.build_pull_plan(config, today=date(2026, 6, 23), reconciliation=reconciliation)

        self.assertEqual(reconciliation["live_not_configured"], ["campaign_three_cosmos"])
        self.assertEqual(reconciliation["configured_not_live"], ["campaign_one"])
        self.assertEqual(plan["campaign_count"], 3)
        self.assertEqual(plan["request_count"], 15)

    def test_discovery_plan_contains_active_search_campaign_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(CONFIG)
            config = pull_data._fallback_config(path)

        plan = pull_data.build_discovery_plan(config)

        self.assertEqual(plan["mcp"]["tool"], "search_to_artifact")
        self.assertEqual(plan["mcp"]["arguments"]["resource"], "campaign")
        self.assertEqual(plan["mcp"]["arguments"]["compression"], "none")
        self.assertIn("campaign.status = 'ENABLED'", plan["mcp"]["arguments"]["conditions"])
        self.assertIn("campaign.advertising_channel_type = 'SEARCH'", plan["mcp"]["arguments"]["conditions"])

    def test_write_partial_creates_file_with_plan_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            original_root = pull_data.ROOT
            pull_data.ROOT = tmp_path
            try:
                plan = {
                    "requests": [
                        {
                            "partial": {
                                "path": "data/partials/campaign-one-structure.json",
                                "key": "campaigns",
                            },
                            "campaign": "campaign_one",
                            "mcp": {"arguments": {"resource": "campaign"}},
                        }
                    ]
                }
                response_data = [{"campaign": {"name": "campaign_one"}}]
                target_path, key, count = pull_data.write_partial(
                    plan, request_index=0, response_data=response_data
                )
                self.assertEqual(target_path, tmp_path / "data/partials/campaign-one-structure.json")
                self.assertEqual(key, "campaigns")
                self.assertEqual(count, 1)
                written = json.loads(target_path.read_text())
                self.assertEqual(written["campaigns"], response_data)
            finally:
                pull_data.ROOT = original_root

    def test_write_partial_uses_configured_data_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "vfs-run"
            plan = {
                "requests": [{
                    "partial": {"path": "partials/campaign-one-structure.json", "key": "campaigns"},
                    "campaign": "campaign_one",
                    "mcp": {"arguments": {"resource": "campaign"}},
                }]
            }

            target_path, key, count = pull_data.write_partial(
                plan,
                request_index=0,
                response_data=[{"campaign": {"name": "campaign_one"}}],
                data_root=data_root,
            )

            self.assertEqual(target_path, data_root / "partials/campaign-one-structure.json")
            self.assertEqual(key, "campaigns")
            self.assertEqual(count, 1)
            self.assertTrue(target_path.exists())

    def test_discovery_write_partial_uses_data_root_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "run"
            data_root.mkdir()
            plan_path = data_root / "campaign-discovery-plan.json"
            plan_path.write_text(json.dumps({
                "output": {"path": "live-campaigns.json", "key": "campaigns"}
            }))
            response_path = Path(tmp) / "response.json"
            response_path.write_text(json.dumps([{"campaign": {"name": "campaign_one"}}]))

            args = pull_data.build_arg_parser().parse_args([
                "write-partial",
                "--data-root", str(data_root),
                "--discovery",
                "--response-file", str(response_path),
            ])
            result = pull_data.cmd_write_partial(args)

            self.assertEqual(result, 0)
            written = json.loads((data_root / "live-campaigns.json").read_text())
            self.assertEqual(len(written["campaigns"]), 1)

    def test_materialize_reports_all_valid_when_partials_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            original_root = pull_data.ROOT
            pull_data.ROOT = tmp_path
            try:
                plan = {
                    "partials": [
                        {
                            "campaign": "campaign_one",
                            "files": {
                                "structure": {
                                    "path": "data/partials/campaign-one-structure.json",
                                    "keys": ["campaigns", "ad_groups"],
                                }
                            },
                        }
                    ],
                    "requests": [],
                }
                partial_file = tmp_path / "data/partials/campaign-one-structure.json"
                partial_file.parent.mkdir(parents=True, exist_ok=True)
                partial_file.write_text(json.dumps({"campaigns": [{}], "ad_groups": [{}]}))

                plan_path = tmp_path / "plan.json"
                plan_path.write_text(json.dumps(plan))

                args = pull_data.build_arg_parser().parse_args(["materialize", "--plan", str(plan_path)])
                result = pull_data.cmd_materialize(args)
                self.assertEqual(result, 0)
            finally:
                pull_data.ROOT = original_root

    def test_materialize_reports_missing_requests_when_partials_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            original_root = pull_data.ROOT
            pull_data.ROOT = tmp_path
            try:
                plan = {
                    "partials": [
                        {
                            "campaign": "campaign_one",
                            "files": {
                                "structure": {
                                    "path": "data/partials/campaign-one-structure.json",
                                    "keys": ["campaigns", "ad_groups"],
                                },
                                "queries": {
                                    "path": "data/partials/campaign-one-queries.json",
                                    "keys": ["keywords", "search_terms"],
                                },
                            },
                        }
                    ],
                    "requests": [
                        {
                            "partial": {
                                "path": "data/partials/campaign-one-structure.json",
                                "key": "campaigns",
                            },
                            "campaign": "campaign_one",
                            "mcp": {"arguments": {"resource": "campaign"}},
                        },
                        {
                            "partial": {
                                "path": "data/partials/campaign-one-structure.json",
                                "key": "ad_groups",
                            },
                            "campaign": "campaign_one",
                            "mcp": {"arguments": {"resource": "ad_group"}},
                        },
                        {
                            "partial": {
                                "path": "data/partials/campaign-one-queries.json",
                                "key": "keywords",
                            },
                            "campaign": "campaign_one",
                            "mcp": {"arguments": {"resource": "keyword_view"}},
                        },
                    ],
                }
                # Only write structure file, leave queries missing
                partial_file = tmp_path / "data/partials/campaign-one-structure.json"
                partial_file.parent.mkdir(parents=True, exist_ok=True)
                partial_file.write_text(json.dumps({"campaigns": [{}], "ad_groups": [{}]}))

                plan_path = tmp_path / "plan.json"
                plan_path.write_text(json.dumps(plan))

                args = pull_data.build_arg_parser().parse_args(["materialize", "--plan", str(plan_path), "--dry-run"])
                result = pull_data.cmd_materialize(args)
                self.assertEqual(result, 0)
                # Re-run without dry-run to get missing commands
                args = pull_data.build_arg_parser().parse_args(["materialize", "--plan", str(plan_path)])
                result = pull_data.cmd_materialize(args)
                self.assertEqual(result, 1)
            finally:
                pull_data.ROOT = original_root



if __name__ == "__main__":
    unittest.main()