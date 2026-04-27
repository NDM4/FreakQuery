## FreakQuery

## v3.2.0

- Added Journal log export support
- Added centralized alias system
- Added unit normalization
- Added JSON alias-aware output

## v3.1.0
- Added interactive shell
- Added new metrics (sequence, timeline...)
- Fixed bugs
- New config file (config.toml)

---

# FreakQuery

Query personal logs with a compact DSL.

FreakQuery lets you search, summarize, and analyze structured logs using short expressions like:

\`\`\`text
count
last
last|dose
route=oral|count
route=intranasal|ratio=substance
sequence
sequence=combo
binges|largest|group_duration
\`\`\`

Useful for personal journals, intake logs, habit tracking, experiments, and messy datasets.

---

# Why use it?

Instead of writing scripts every time you want answers:

\`\`\`text
How many times this month?
What was my last dose?
Which route do I use most?
What usually comes after X?
\`\`\`

Use one-line queries:

\`\`\`text
month|count
last|dose
ratio=route
sequence=after:alprazolam
\`\`\`

---

# Features

- Compact query language using \`|\`
- Filters, metrics, ratios, rankings, sequences
- Human-readable text output
- JSON output for scripts and automation
- Supports standard \`logs.json\`
- Supports Journal exports
- Handles messy aliases automatically
- CLI + interactive shell
- Configurable through \`config.toml\`

---

# Examples

## Count entries

\`\`\`text
count
\`\`\`

## Last recorded substance

\`\`\`text
last|substance
\`\`\`

## Last recorded dose

\`\`\`text
last|dose
\`\`\`

## Route breakdown

\`\`\`text
ratio=route
\`\`\`

## Most common substances

\`\`\`text
top_substances
\`\`\`

## Recent sequence

\`\`\`text
sequence
\`\`\`

## Combo patterns

\`\`\`text
sequence=combo
\`\`\`

## Escalation patterns

\`\`\`text
sequence=escalation
\`\`\`

---

# Input formats

## Standard logs

\`\`\`json
[
  {
    "time": 1728855908000,
    "substance": "Alprazolam",
    "dose": 0.5,
    "unit": "mg",
    "route": "oral"
  }
]
\`\`\`

## Journal exports

Supported automatically. Ingestions are extracted from exported experiences.

---

# Install

Go to the project file and use this command:
\`\`\`bash
pip install .
\`\`\`

---

# CLI

\`\`\`bash
freakquery logs.json count
freakquery logs.json route=oral|count
freakquery logs.json "{{last|dose}}"
\`\`\`

---

# Interactive shell

\`\`\`bash
freakquery shell logs.json
\`\`\`

Then run queries directly.

---

# Output modes

## Text

\`\`\`text
Alprazolam (0.5 mg)
\`\`\`

## JSON

\`\`\`text
last|json
\`\`\`

---

# Config

Customize aliases, defaults, rendering, and behavior in:

\`\`\`text
config.toml
\`\`\`

---
