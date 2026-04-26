# src/query/parser.py

def parse_tag(raw_tag):
    raw_tag = (
        raw_tag or ""
    ).strip()

    if not raw_tag:
        return []

    parts = [
        p.strip()
        for p in raw_tag.split("|")
        if p.strip()
    ]

    return parts