import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from freakquery import query


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "USEFUL_TAG_COMBINATIONS.md"


def ms(dt):
    return int(dt.timestamp() * 1000)


def sample_rows():
    now = datetime.now().replace(microsecond=0)

    return [
        {
            "time": ms(now - timedelta(hours=1)),
            "substance": "Alprazolam",
            "dose": 0.5,
            "unit": "mg",
            "route": "oral",
            "site": "mouth",
            "notes": "baseline",
        },
        {
            "time": ms(now - timedelta(hours=1)),
            "substance": "Caffeine",
            "dose": 100,
            "unit": "mg",
            "route": "oral",
            "site": "mouth",
            "notes": "same timestamp combo",
        },
        {
            "time": ms(now - timedelta(minutes=30)),
            "substance": "Alprazolam",
            "dose": 1,
            "unit": "mg",
            "route": "intranasal",
            "site": "left nostril",
            "notes": "escalation",
        },
        {
            "time": ms(now - timedelta(minutes=10)),
            "substance": "Ketamine",
            "dose": 25,
            "unit": "mg",
            "route": "intranasal",
            "site": "right nostril",
            "notes": "sequence target",
        },
        {
            "time": ms(now - timedelta(days=1)),
            "substance": "Caffeine",
            "dose": 0.2,
            "unit": "g",
            "route": "oral",
            "site": "mouth",
            "notes": "previous day",
        },
        {
            "time": ms(now - timedelta(days=2)),
            "substance": "Delta-8-THC",
            "dose": 500,
            "unit": "ug",
            "route": "smoked",
            "site": "lung",
            "notes": "current week",
        },
        {
            "time": ms(now - timedelta(days=8)),
            "substance": "Ketamine",
            "dose": 40,
            "unit": "mg",
            "route": "intravenous",
            "site": "arm",
            "notes": "current month",
        },
        {
            "time": ms(now - timedelta(days=20)),
            "substance": "Alprazolam",
            "dose": 1.5,
            "unit": "mg",
            "route": "sublingual",
            "site": "mouth",
            "notes": "current month escalation",
        },
        {
            "time": ms(now - timedelta(days=80)),
            "substance": "Caffeine",
            "dose": 50,
            "unit": "mg",
            "route": "oral",
            "site": "mouth",
            "notes": "current year",
        },
        {
            "time": ms(now - timedelta(days=400)),
            "substance": "Alprazolam",
            "dose": 0.25,
            "unit": "mg",
            "route": "oral",
            "site": "mouth",
            "notes": "previous year",
        },
        {
            "time": ms(now - timedelta(days=401)),
            "substance": "Ketamine",
            "dose": 10,
            "unit": "mg",
            "route": "intranasal",
            "site": "left nostril",
            "notes": "previous year streak",
        },
    ]


def documented_queries():
    text = DOC.read_text(encoding="utf-8")

    return re.findall(r"^- `([^`]+)` - ", text, flags=re.MULTILINE)


class DocumentedCombinationTests(unittest.TestCase):
    def test_documented_queries_execute_without_errors(self):
        rows = sample_rows()
        queries = documented_queries()

        self.assertGreater(len(queries), 200)

        failures = []

        for q in queries:
            try:
                result = query(q, rows)
            except Exception as exc:
                failures.append(f"{q}: raised {exc!r}")
                continue

            if "[error:" in str(result):
                failures.append(f"{q}: returned {result!r}")

        if failures:
            self.fail("\n".join(failures))


if __name__ == "__main__":
    unittest.main()
