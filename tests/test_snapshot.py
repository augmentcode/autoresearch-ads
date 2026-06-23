import builtins
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import snapshot


class SnapshotConfigTests(unittest.TestCase):
    def test_read_config_uses_data_source_fallback_without_yaml(self):
        config_text = """
data_source:
  type: mcp
  customer_id: "9232939339"
  date_range: last_14_days
"""
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("No module named yaml")
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text(config_text)
            original_path = snapshot.CONFIG_PATH
            snapshot.CONFIG_PATH = str(path)
            try:
                with mock.patch("builtins.__import__", side_effect=fake_import):
                    config = snapshot.read_config()
            finally:
                snapshot.CONFIG_PATH = original_path

        self.assertEqual(config["data_source"]["customer_id"], "9232939339")
        self.assertEqual(config["data_source"]["date_range"], "last_14_days")

    def test_compute_date_range_custom_dates(self):
        config = {"data_source": {"start_date": "2026-06-01", "end_date": "2026-06-07"}}

        date_range = snapshot.compute_date_range(config)

        self.assertEqual(date_range, {"type": "custom", "start": "2026-06-01", "end": "2026-06-07"})


if __name__ == "__main__":
    unittest.main()