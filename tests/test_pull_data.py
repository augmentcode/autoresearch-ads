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


if __name__ == "__main__":
    unittest.main()