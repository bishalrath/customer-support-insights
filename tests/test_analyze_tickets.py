import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from analyze_tickets import analyze, sentiment


class TestTicketAnalysis(unittest.TestCase):
    def test_sentiment(self):
        self.assertEqual(sentiment("excellent and helpful"), "positive")
        self.assertEqual(sentiment("urgent broken error"), "negative")
        self.assertEqual(sentiment("please add a filter"), "neutral")

    def test_analysis(self):
        rows = [
            {"category": "Login", "priority": "High", "status": "Resolved", "resolution_hours": "5", "message": "urgent error"},
            {"category": "Billing", "priority": "Low", "status": "Open", "resolution_hours": "2", "message": "thanks helpful"},
        ]
        result = analyze(rows)
        self.assertEqual(result["total_tickets"], 2)
        self.assertEqual(result["sla_breach_count"], 1)
        self.assertEqual(result["sentiment_counts"]["positive"], 1)


if __name__ == "__main__":
    unittest.main()
