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

        self.assertEqual(plan["mcp"]["arguments"]["resource"], "campaign")
        self.assertIn("campaign.status = 'ENABLED'", plan["mcp"]["arguments"]["conditions"])
        self.assertIn("campaign.advertising_channel_type = 'SEARCH'", plan["mcp"]["arguments"]["conditions"])


if __name__ == "__main__":
    unittest.main()