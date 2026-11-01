import unittest
from datetime import UTC, datetime

import main
from routing.admin_api import complete_months


class AdminAnalysisTests(unittest.TestCase):
    def test_six_month_series_fills_gaps_and_crosses_years(self):
        self.assertIsNotNone(main.app)
        result = complete_months(
            {"2025-11": 3, "2026-01": 2}, datetime(2026, 2, 12, tzinfo=UTC)
        )
        self.assertEqual(
            result,
            [
                {"month": "2025-09", "count": 0},
                {"month": "2025-10", "count": 0},
                {"month": "2025-11", "count": 3},
                {"month": "2025-12", "count": 0},
                {"month": "2026-01", "count": 2},
                {"month": "2026-02", "count": 0},
            ],
        )


if __name__ == "__main__":
    unittest.main()
