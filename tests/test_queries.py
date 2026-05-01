import json
import unittest

from freakquery import query
from freakquery.loader import load_journal
from freakquery.units import to_mg


ROWS = [
    {
        "time": 1710000000000,
        "substance": "Alprazolam",
        "dose": 0.5,
        "unit": "mg",
        "route": "oral",
    },
    {
        "time": 1710000000000,
        "substance": "Caffeine",
        "dose": 100,
        "unit": "mg",
        "route": "oral",
    },
    {
        "time": 1710003600000,
        "substance": "Alprazolam",
        "dose": 1,
        "unit": "mg",
        "route": "intranasal",
    },
    {
        "time": 1741626000000,
        "substance": "Caffeine",
        "dose": 0.2,
        "unit": "g",
        "route": "oral",
    },
]


class QueryTests(unittest.TestCase):
    def test_core_query_pipeline(self):
        self.assertEqual(query("count", ROWS), "4")
        self.assertEqual(query("last|dose", ROWS), "0.2 g")
        self.assertEqual(
            query("ratio=route", ROWS),
            "oral 75%\nintranasal 25%",
        )

    def test_dynamic_sequence_metrics(self):
        self.assertEqual(
            query("sequence=combo", ROWS),
            "Alprazolam + Caffeine (1)",
        )
        self.assertEqual(
            query("sequence=escalation", ROWS),
            "Alprazolam 0.5mg -> 1mg (1)\n"
            "Caffeine 100mg -> 200mg (1)",
        )

    def test_trend_metrics(self):
        self.assertEqual(
            query("trend_month", ROWS),
            "2024-03 (3)\n2025-03 (1)",
        )
        self.assertEqual(
            query("trend_year", ROWS),
            "2024 (3)\n2025 (1)",
        )

    def test_json_output_and_field_aliases(self):
        out = json.loads(query("last|json", ROWS))

        self.assertEqual(out[0]["substance"], "Caffeine")
        self.assertEqual(query("last|field=substanceName", ROWS), "Caffeine")

    def test_journal_loader_and_microgram_units(self):
        journal = {
            "experiences": [
                {
                    "ingestions": [
                        {
                            "time": 1710000000000,
                            "substanceName": "Caffeine",
                            "administrationRoute": "oral",
                            "dose": 500,
                            "units": "\u00b5g",
                        }
                    ]
                }
            ]
        }

        rows = load_journal(journal)

        self.assertEqual(rows[0]["unit"], "ug")
        self.assertEqual(to_mg(500, "\u00b5g"), 0.5)
        self.assertEqual(to_mg(500, "\u03bcg"), 0.5)


if __name__ == "__main__":
    unittest.main()
