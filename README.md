## FreakQuery

Query personal logs with a compact DSL.

FreakQuery lets you search, summarize, and analyze structured logs using short expressions like:

```text
count
last
last|dose
route=oral|count
ratio=route
sequence
sequence=combo
binges|largest|group_duration
```

Useful for personal journals, intake logs, habit tracking, experiments, and messy datasets.

---

# Why use it?

Instead of writing scripts every time you want answers:

```text
How many times this month?
What was my last dose?
Which route do I use most?
What usually comes after X?
```

Use one-line queries:

```text
month|count
last|dose
ratio=route
sequence=after:alprazolam
```

---

# Install

```bash
pip install .
```

Requires Python 3.9+.

---

# Quick Start

```bash
# Count all entries
freakquery logs.json count

# Last recorded dose
freakquery logs.json "last|dose"

# Route breakdown
freakquery logs.json "ratio=route"

# Interactive shell
freakquery shell logs.json
```

---

# Input Formats

## Standard logs

```json
[
  {
    "time": 1728855908000,
    "substance": "Alprazolam",
    "dose": 0.5,
    "unit": "mg",
    "route": "oral"
  }
]
```

## Journal exports

Supported automatically. Ingestions are extracted from exported experiences.

---

# Query Reference

## Filters

Reduce rows by time window or field value.

| Filter | Description |
|--------|-------------|
| `today` | Rows from today |
| `week` | Rows from this ISO week |
| `month` | Rows from this month |
| `year` | Rows from this year |
| `substance=X` | Rows where substance matches X |
| `route=X` | Rows where route matches X |
| `site=X` | Rows where site matches X |
| `unit=X` | Rows where unit matches X |

Filters can be combined: `month|route=oral|count`

## Selectors

Pick one row or group.

| Selector | Description |
|----------|-------------|
| `first` | Earliest row by time |
| `last` | Most recent row by time |
| `random` | One random row |
| `largest` | Group with highest total dose |
| `longest` | Group with longest duration |

## Groups

Group rows into clusters.

| Group | Description |
|-------|-------------|
| `binges` | Rows within a configurable gap (default 8h) |
| `streaks` | Consecutive calendar-day entries |

## Metrics

Produce a result from rows.

| Metric | Description |
|--------|-------------|
| `count` | Total row count |
| `dose` | Dose text of the last row |
| `substance` | Substance name of the last row |
| `since` | Time since the last entry |
| `sum_dose` | Total dose in mg (mass only) |
| `top_substances` | Substances ranked by count |
| `top_routes` | Routes ranked by count |
| `sites` | Sites ranked by count |
| `substance_totals` | Substances ranked by total dose |
| `avg_gap` | Average time gap between rows |
| `substances_count` | Number of distinct substances |
| `timeline` | Rows in time order |
| `sequence` | Substance sequence |
| `trend_month` | Row counts by month |
| `trend_year` | Row counts by year |
| `group_sum` | Total dose in a group |
| `group_duration` | Duration of a group |
| `group_count` | Row count in a group |
| `main_substance` | Most common substance in a group |

## Dynamic Metrics

| Syntax | Description |
|--------|-------------|
| `ratio=FIELD` | Breakdown by field with percentages |
| `sequence=dose` | Sequence with dose text |
| `sequence=time` | Sequence with time gaps |
| `sequence=patterns` | Adjacent transition counts |
| `sequence=combo` | Same-time combination counts |
| `sequence=escalation` | Dose escalation counts |
| `sequence=after:X` | What follows substance X |
| `sequence=before:X` | What precedes substance X |

## Parameters

| Parameter | Description |
|-----------|-------------|
| `limit=N` or `top=N` | Limit list results |
| `reverse` | Reverse result order |
| `field=NAME` | Extract a single field value |
| `json` | Output as JSON |

## Render Flags

| Flag | Description |
|------|-------------|
| `dose=true/false` | Show/hide dose |
| `unit=true/false` | Show/hide unit |
| `route=true` | Show route |
| `site=true` | Show site |
| `time=iso` | ISO timestamp |
| `time=date` | Date only |
| `time` | Clock time |
| `parens=true/false` | Wrap details in parentheses |
| `labels=true/false` | Show/hide labels |
| `count=true` | Show raw counts |
| `percent=true/false` | Show/hide percentages |
| `compact=true` | Compact output |

---

# Shell Commands

```text
.help          show help
.reload        reload data from file
.clear         clear the screen
.version       show version
.rows          show row count
.path          show loaded file path
.pwd           show current directory
.cd [dir]      change directory
.history       show command history
.stats         show quick stats overview
.last          re-run last query
.time <query>  run query with timing
.watch <query> run query repeatedly
.source        show file info
.quit / .exit   exit shell
```

---

# Config

Customize aliases, defaults, rendering, and behavior in `config.toml`.

See `docs/TAGS.md` for the tag creation guide.

See `docs/USEFUL_TAG_COMBINATIONS.md` for a complete list of working queries.
