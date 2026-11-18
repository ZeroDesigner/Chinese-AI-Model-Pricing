import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PricingTests(unittest.TestCase):
    def setUp(self):
        self.pricing = json.loads((ROOT / "data" / "pricing.json").read_text())
        self.sources = json.loads((ROOT / "data" / "sources.json").read_text())

    def test_unique_model_ids(self):
        ids = [model["model_id"] for model in self.pricing["models"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_required_fields(self):
        required = {"provider", "name", "model_id", "source_url"}
        for model in self.pricing["models"]:
            self.assertTrue(required <= model.keys(), model)

    def test_sources_have_urls(self):
        self.assertGreaterEqual(len(self.sources["sources"]), 10)
        for source in self.sources["sources"]:
            self.assertTrue(source["official_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
