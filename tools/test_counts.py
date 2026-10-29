"""Tests for counts.py. Run: python3 -m unittest tools/test_counts.py (from the library repo root,
or tools/library_repo in Pie UI's repo)."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import counts  # noqa: E402


class Counts(unittest.TestCase):
    def test_versions_summed_and_strangers_ignored(self):
        rels = [
            {"tag_name": "stone-v1", "assets": [{"name": "stone.zip", "download_count": 10}]},
            {"tag_name": "stone-v2", "assets": [{"name": "stone.zip", "download_count": 5},
                                                 {"name": "notes.txt", "download_count": 99}]},
            {"tag_name": "ember-v1", "draft": True, "assets": [{"name": "ember.zip", "download_count": 7}]},
            {"tag_name": "v1.0.0.0", "assets": [{"name": "PieUI.dll", "download_count": 1000}]},
            {"tag_name": "glass-v1", "assets": [{"name": "stone.zip", "download_count": 3}]},
        ]
        self.assertEqual(counts.counts(rels), {"stone": 15})


if __name__ == "__main__":
    unittest.main()
