from datetime import date
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from xml.etree import ElementTree

path = Path(__file__).resolve().parents[1] / "scripts/build_activity_tab.py"
spec = importlib.util.spec_from_file_location("activity", path)
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)


def event(identifier, timestamp, kind="PushEvent", public=True, actor="rogerrrmalcolm"):
    return {"id": identifier, "created_at": timestamp, "type": kind,
            "public": public, "actor": {"login": actor}}


class ActivityTabTests(unittest.TestCase):
    def test_utc_boundaries_privacy_and_duplicates(self):
        records = [event("a", "2026-10-27T00:00:00Z"), event("a", "2026-10-27T00:00:00Z"),
                   event("b", "2026-11-23T23:59:59Z", "PullRequestEvent"),
                   event("c", "2026-10-26T23:59:59Z"), event("d", "2026-11-24T00:00:00Z"),
                   event("e", "2026-11-23T00:00:00Z", public=False),
                   event("f", "2026-11-23T00:00:00Z", actor="github-actions[bot]"),
                   event("g", "2026-10-26T20:30:00-04:00", "FutureEventType")]
        result = activity.build_snapshot(records, "rogerrrmalcolm", date(2026, 11, 23))
        self.assertEqual(result["total_events"], 3)
        self.assertEqual(result["rows"][0]["days"][0], 1)
        self.assertEqual(result["rows"][1]["days"][27], 1)
        self.assertEqual(result["rows"][5]["days"][0], 1)

    def test_api_failure_does_not_become_zero_activity(self):
        with patch.object(activity, "urlopen", side_effect=HTTPError("https://api.github.com", 403, "rate limit", {}, None)):
            with self.assertRaises(HTTPError):
                activity.fetch_events("rogerrrmalcolm", date(2026, 10, 27))

    def test_feed_limit_is_visible(self):
        records = [event(str(i), "2026-11-23T12:00:00Z") for i in range(300)]
        snapshot = activity.build_snapshot(records, "rogerrrmalcolm", date(2026, 11, 23))
        self.assertTrue(snapshot["limited_to_available_events"])
        self.assertIn("feed limit reached", activity.draw_svg(snapshot, "light"))

    def test_both_themes_and_quiet_period_are_valid_svg(self):
        snapshot = activity.build_snapshot([], "rogerrrmalcolm", date(2026, 11, 23))
        for theme in ["light", "dark"]:
            for mobile in [False, True]:
                svg = activity.draw_svg(snapshot, theme, mobile)
                root = ElementTree.fromstring(svg)
                self.assertEqual(root.get("viewBox"), "0 0 360 190" if mobile else "0 0 720 174")
                self.assertIn("quiet four weeks", svg.lower())
                self.assertIn("prefers-reduced-motion", svg)
                self.assertNotIn("<script", svg)
                self.assertNotIn("foreignObject", svg)
                self.assertEqual(svg.count('font-size="16"' if mobile else 'font-size="14"'), 6)


if __name__ == "__main__":
    unittest.main()
