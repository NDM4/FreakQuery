# Guide to Creating FreakQuery Tags

This guide explains how FreakQuery tags work and how to create new ones without having to reverse-engineer the whole project.

A tag is one part of a query. Queries are written as `|`-separated pipelines:

```text
month|route=oral|last|dose
binges|largest|group_duration
ratio=substance|limit=5
```

Tags can also be used inside templates:

```text
Last entry: {{last}}
Last dose: {{last|dose}}
```

## System Map

These are the files that matter when working with tags:

| File | Purpose |
| --- | --- |
| `freakquery/engine.py` | Accepts standalone tags or `{{...}}` templates and calls the executor. |
| `freakquery/query/parser.py` | Splits a query by `|`. |
| `freakquery/query/precedence.py` | Reorders query parts into a stable order: filters, params, group, selector, metrics, format. |
| `freakquery/query/planner.py` | Converts query parts into a `QueryPlan`. |
| `freakquery/query/validator.py` | Checks whether tag combinations make sense according to declared input/output types. |
| `freakquery/tag_registry.py` | Declares known tags, their pipeline stage, and their input/output types. |
| `freakquery/ops/filters.py` | Implements filters like `today`, `month`, and `route=oral`. |
| `freakquery/ops/grouping.py` | Implements grouping tags like `binges` and `streaks`. |
| `freakquery/ops/selectors.py` | Implements selectors like `last`, `first`, and `largest`. |
| `freakquery/ops/metrics.py` | Implements metrics like `count`, `dose`, `ratio=...`, and `sequence=...`. |
| `freakquery/ops/transforms.py` | Applies final transforms like `reverse` and `limit`. |
| `freakquery/outputs/text.py` | Renders results as text. |
| `freakquery/outputs/json.py` | Renders results as JSON. |
| `config.toml` | Configures aliases, equivalent field names, limits, and rendering defaults. |

## Query Flow

For a query like:

```text
month|route=oral|last|dose
```

FreakQuery does this:

1. `parse_tag()` turns it into parts:

```python
["month", "route=oral", "last", "dose"]
```

2. `normalize_parts()` sorts the query by precedence. The user may write `last|month|dose`, but the system tries to execute filters first, then selectors, then metrics.

3. `validate_parts()` checks that every registered tag accepts the current data type.

4. `build_plan()` creates a `QueryPlan`:

```python
filters = ["month", "route=oral"]
selector = "last"
metrics = ["dose"]
```

5. `execute_tag()` runs the pipeline:

```text
initial rows
-> apply_filters()
-> apply_grouping()
-> apply_selectors()
-> apply_metrics()
-> apply_transforms()
-> render_text() or render_json()
```

## Data Types

Types are defined in `freakquery/fq_types.py`.

| Type | Meaning |
| --- | --- |
| `LOG_ROWS` | A normal list of log entries. Each entry is usually a `dict`. |
| `GROUP_ROWS` | A list of groups. Each group is a list of log entries. |
| `TEXT_ROWS` | Rows already shaped for text output. |
| `TOTAL_ROWS` | Total rows, usually grouped by substance or another entity. |
| `TREND_ROWS` | Rows representing time trends. |
| `SCALAR` | A single value: number, string, duration, etc. |
| `ANY` | Any type. |
| `EMPTY` | No useful result. |

These are not Python classes. They are strings used to validate the tag chain.

## Tag Families

FreakQuery has four main tag families.

## 1. Filters

Filters reduce `LOG_ROWS` and return `LOG_ROWS`.

Current examples:

```text
today
week
month
year
route=oral
substance=alprazolam
site=left nostril
```

Generic `key=value` filters are resolved through aliases and equivalent field names from `config.toml`.

For example, if `config.toml` says that `route`, `roa`, and `administrationRoute` are equivalent fields, then `route=oral` can work even when the actual row uses a different compatible key.

## 2. Groups

Groups turn `LOG_ROWS` into `GROUP_ROWS`.

Current examples:

```text
binges
streaks
```

Usage examples:

```text
binges|count
binges|largest|group_duration
streaks|longest|main_substance
```

## 3. Selectors

Selectors pick one row or one group.

Current examples:

```text
first
last
random
largest
longest
```

`first`, `last`, and `random` work on normal rows. `largest` and `longest` are meant for grouped rows.

Usage examples:

```text
last
last|dose
last|field=notes
binges|largest
binges|longest|group_duration
```

## 4. Metrics

Metrics turn rows or groups into a final result: a number, text, list, ranking, timeline, etc.

Current examples:

```text
count
dose
substance
since
sum_dose
top_substances
top_routes
sites
substance_totals
timeline
sequence
group_sum
group_duration
group_count
main_substance
trend_month
trend_year
```

There are also dynamic metrics that use `=`.

```text
ratio=route
ratio=substance
sequence=dose
sequence=time
sequence=patterns
sequence=after:alprazolam
sequence=before:alprazolam
```

## Tag Registry Contract

Each registered tag in `freakquery/tag_registry.py` looks like this:

```python
"tag_name": {
    "accept": {LOG_ROWS},
    "returns": SCALAR,
    "stage": "metric",
    "fn": "function_name",
}
```

Fields:

| Field | Meaning |
| --- | --- |
| `accept` | Set of data types the tag can receive. |
| `returns` | Data type returned after the tag runs. |
| `stage` | Pipeline stage: `"group"`, `"selector"`, or `"metric"`. |
| `fn` | Descriptive function name. In the current code, this is not used for automatic dispatch. |

Important: in the current implementation, adding a tag to `REGISTRY` is not enough. The registry helps the planner and validator, but the actual behavior must be implemented in the matching `ops` file.

## Creating a Simple Metric

Example: create `avg_dose`, a metric that returns the average dose normalized to mg.

### Step 1: Register the tag

Edit `freakquery/tag_registry.py`:

```python
"avg_dose": {
    "accept": {LOG_ROWS},
    "returns": SCALAR,
    "stage": "metric",
    "fn": "avg_dose_value",
},
```

Place it in the metrics section.

### Step 2: Implement it in `ops/metrics.py`

Inside `apply_metrics()`, near the existing dose metrics:

```python
if metric == "avg_dose":
    if not rows:
        return 0

    total = 0.0
    count = 0

    for r in rows:
        total += to_mg(
            row_get(r, "dose"),
            row_get(r, "unit"),
        )
        count += 1

    avg = total / count

    if avg.is_integer():
        return int(avg)

    return round(avg, 2)
```

You can now use:

```text
avg_dose
month|avg_dose
substance=alprazolam|avg_dose
```

### Step 3: Add a default limit if needed

If your metric returns a list, you can add a default limit in `config.toml`:

```toml
[limits]
my_metric = 10
```

For scalar metrics like `avg_dose`, this is usually not needed.

## Creating a Metric That Returns Rows

Example: `large_doses`, a metric that returns entries with doses above a fixed threshold.

In `tag_registry.py`:

```python
"large_doses": {
    "accept": {LOG_ROWS},
    "returns": LOG_ROWS,
    "stage": "metric",
    "fn": "large_doses_rows",
},
```

In `ops/metrics.py`:

```python
if metric == "large_doses":
    return [
        r for r in rows
        if to_mg(row_get(r, "dose"), row_get(r, "unit")) >= 100
    ]
```

Usage:

```text
large_doses
large_doses|json
large_doses|limit=5
```

Note: `limit` and `reverse` are applied after `apply_metrics()` in `apply_transforms()`, but only if the final result is a list.

## Creating a Dynamic `name=value` Metric

Dynamic metrics are not registered one by one in `REGISTRY`, because the tag name includes a variable value. Two existing patterns are:

```text
ratio=route
sequence=after:alprazolam
```

To create a new dynamic metric, edit `freakquery/query/planner.py` and `freakquery/ops/metrics.py`.

Example: `exists=notes`, which counts how many rows have a non-empty field.

In `planner.py`, inside the `if "=" in part` block, before treating the part as a normal filter:

```python
if key_l == "exists":
    plan.metrics.append(
        f"exists={tag_norm(val)}"
    )
    continue
```

In `metrics.py`:

```python
if metric.startswith("exists="):
    field = metric.split("=", 1)[1]

    return sum(
        1 for r in rows
        if row_get(r, field) not in (None, "")
    )
```

Usage:

```text
exists=notes
month|exists=site
substance=ketamine|exists=notes
```

If the new dynamic metric uses `key=value`, also review `validator.py`. Currently `validate_parts()` has explicit rules for some keys such as `substance`, `route`, `limit`, `top`, and `ratio`.

## Creating a Selector

A selector receives rows or groups and returns a selection.

Example: `second_last`, which returns the second-to-last row by time.

In `tag_registry.py`:

```python
"second_last": {
    "accept": {LOG_ROWS},
    "returns": LOG_ROWS,
    "stage": "selector",
    "fn": "second_last_item",
},
```

In `query/precedence.py`, add the name to the selector list:

```python
if low in (
    "last",
    "first",
    "random",
    "largest",
    "longest",
    "second_last",
):
    selector = low
    continue
```

In `ops/selectors.py`, inside `apply_selectors()`:

```python
if mode == "second_last":
    ordered = sorted(rows, key=row_time)

    if len(ordered) < 2:
        return []

    return [ordered[-2]]
```

Usage:

```text
second_last
second_last|dose
second_last|field=notes
```

If you want it to appear in shell autocomplete, add `second_last` to the `words` list in `freakquery/shell.py`.

## Creating a Group

A group receives `LOG_ROWS` and returns `GROUP_ROWS`: a list of lists.

Conceptual example: `sessions`, which groups rows separated by less than 90 minutes.

In `tag_registry.py`:

```python
"sessions": {
    "accept": {LOG_ROWS},
    "returns": GROUP_ROWS,
    "stage": "group",
    "fn": "make_sessions",
},
```

In `query/precedence.py`, add `sessions` to the group list:

```python
if low in ("binges", "streaks", "sessions"):
    group = low
    continue
```

In `ops/grouping.py`, create the function:

```python
def build_sessions(rows):
    if not rows:
        return []

    rows = sorted(rows, key=lambda r: r["time"])
    max_gap = 90 * 60 * 1000

    groups = []
    cur = [rows[0]]

    for row in rows[1:]:
        if row["time"] - cur[-1]["time"] <= max_gap:
            cur.append(row)
        else:
            groups.append(cur)
            cur = [row]

    groups.append(cur)
    return groups
```

Then connect it in `apply_grouping()`:

```python
if mode == "sessions":
    return build_sessions(rows)
```

Usage:

```text
sessions|count
sessions|largest|group_count
sessions|longest|group_duration
```

## Creating a Simple Filter

Generic `key=value` filters already work. If your data has a new field, you often do not need new code:

```text
mood=good|count
source=journal|last
```

If you want the filter to support alternate field names, add the field to `[fields]` in `config.toml`:

```toml
[fields]
mood = ["mood", "feeling", "state"]
```

If you want aliases for values:

```toml
[aliases.mood]
good = "good"
great = "good"
ok = "good"
bad = "bad"
```

Now these queries can point to the same canonical value:

```text
mood=great|count
mood=good|count
```

## `field=`: Universal Extractor

`field=` is special. It runs after filters, groups, and selectors, but before metrics.

Examples:

```text
last|field=notes
last|field=substance
last|field=administrationRoute
```

Use it to read fields that do not have their own metric. If you extract a field often, consider turning it into a metric. If you only need it occasionally, `field=` is enough.

## Rendering and Result Shape

The shape your tag returns affects how it is printed.

| Return value | Rendered as |
| --- | --- |
| `str`, `int`, `float` | Direct text. |
| `dict` | One row. |
| `list[dict]` with `substance` and `count` | Substance ranking. |
| `list[dict]` with `value` and `count` | Generic ranking. |
| `list[dict]` with `value`, `count`, and `label` | Ratio/percentage rows. |
| Normal `list[dict]` | Normal rows with substance, dose, unit, route, site, and time depending on render flags. |
| `json` in the query | Pretty JSON with `ensure_ascii=False`. |

Examples:

```text
top_substances
top_substances|json
ratio=route|count=true
last|route|site|time=iso
```

## Universal Parameters

These parameters already exist:

| Parameter | Use |
| --- | --- |
| `limit=5` or `top=5` | Limits results if the final result is a list. |
| `reverse` or `reverse=true` | Reverses lists at the end. |
| `reverse=false` | Prevents reversing. |
| `json` | Renders as JSON. |

Render flags:

```text
dose
unit
route
site
time
time=iso
time=date
labels=false
percent=false
count=true
compact=true
parens=false
sep=" / "
```

These flags do not filter data. They only change how the output is displayed.

## New Tag Checklist

Before writing code, decide:

- What type it receives: `LOG_ROWS`, `GROUP_ROWS`, `TEXT_ROWS`, etc.
- What type it returns: `SCALAR`, `LOG_ROWS`, `TEXT_ROWS`, etc.
- Which stage it belongs to: filter, group, selector, or metric.
- Whether it returns a list or a single value.
- Whether it needs field aliases or value aliases.
- Whether it needs a default limit in `config.toml`.
- Whether it should work with `json`.
- Whether it should appear in the interactive shell.

Then implement:

1. Register it in `freakquery/tag_registry.py`, unless it is a dynamic `name=value` metric.
2. Add the actual behavior in `freakquery/ops/metrics.py`, `ops/grouping.py`, `ops/selectors.py`, or `ops/filters.py`.
3. Update precedence in `freakquery/query/precedence.py` if it is a new group or selector.
4. Update parsing/planning in `freakquery/query/planner.py` if it uses special `=` syntax.
5. Update validation in `freakquery/query/validator.py` if the new syntax has type restrictions.
6. Add autocomplete in `freakquery/shell.py` if you want it in the shell.
7. Add limits/configuration in `config.toml` if it returns lists or needs global settings.
8. Add examples to the README or docs.

## Common Mistakes

### Registering the tag but not implementing it

`tag_registry.py` does not execute the function named in `fn`. If you add the registry entry but do not add an `if metric == "my_tag"` or equivalent in `ops`, the tag will not have real behavior.

### Returning the wrong type

If you declare:

```python
"returns": GROUP_ROWS
```

return a list of groups:

```python
[
    [row1, row2],
    [row3, row4],
]
```

Do not return a flat list of rows if you promised `GROUP_ROWS`.

### Breaking the type chain

This query makes sense:

```text
binges|largest|group_duration
```

Because the type chain is:

```text
LOG_ROWS -> GROUP_ROWS -> LOG_ROWS -> SCALAR
```

This can fail if the tag expects groups but receives rows:

```text
last|largest
```

### Forgetting `row_get()`

Do not always read `row["substance"]` or `row["route"]` directly if you want field alias compatibility. Use `row_get(row, "substance")` when working in `metrics.py` or `filters.py`.

### Forgetting to normalize values

For substances, routes, units, and sites, use:

```python
canonical_value("substance", value)
canonical_value("route", value)
canonical_value("unit", value)
canonical_value("site", value)
```

To compare values with aliases:

```python
same_value("substance", a, b)
```

## Recommended Conventions

- Use short lowercase names: `avg_dose`, `top_routes`, `group_count`.
- Use `snake_case`.
- If the tag returns a final number or string, use `SCALAR`.
- If it returns original rows, use `LOG_ROWS`.
- If it returns a ranking, use a list of dicts with `value/count` or `substance/count`.
- If it returns percentages, use `value/count/label`.
- Avoid doing final text rendering inside metrics when you can return structured data.
- Use `to_mg()` when summing or comparing mass doses.
- Use `human_since()` when returning readable durations.
- Keep dynamic metrics in the `name=value` format.

## Complete Example: `unique_substances`

Goal:

```text
unique_substances
month|unique_substances
unique_substances|json
```

It should return a list of unique substances.

In `tag_registry.py`:

```python
"unique_substances": {
    "accept": {LOG_ROWS},
    "returns": TEXT_ROWS,
    "stage": "metric",
    "fn": "unique_substances_rows",
},
```

In `metrics.py`:

```python
if metric == "unique_substances":
    values = sorted(
        set(
            row_substance(r)
            for r in rows
            if row_substance(r)
        )
    )

    return [
        {"value": v, "count": 1}
        for v in values
    ]
```

Text output:

```text
Alprazolam (1)
Ketamine (1)
Psilocin (1)
```

JSON output:

```json
[
  {
    "value": "Alprazolam",
    "count": 1
  }
]
```

If you do not want `(1)` in text output, return strings instead:

```python
return values
```

In that case, `unique_substances|json` returns a simple list of strings.

## Testing a Tag

Create or reuse a small JSON file:

```json
[
  {
    "time": 1728855908000,
    "substance": "Alprazolam",
    "dose": 0.5,
    "unit": "mg",
    "route": "oral"
  },
  {
    "time": 1728860000000,
    "substance": "Ketamine",
    "dose": 40,
    "unit": "mg",
    "route": "intranasal"
  }
]
```

Test from the CLI:

```bash
freakquery logs.json count
freakquery logs.json last
freakquery logs.json "last|dose"
freakquery logs.json "ratio=route|json"
```

Test from Python:

```python
from freakquery.engine import repl

rows = [
    {
        "time": 1728855908000,
        "substance": "Alprazolam",
        "dose": 0.5,
        "unit": "mg",
        "route": "oral",
    }
]

print(repl("last|dose", rows))
```

## Final Mental Model

Think of every tag as a small function inside a pipeline:

```text
data -> filter -> group -> selector -> metric -> transform -> render
```

A good tag clearly declares what it accepts, returns a predictable shape, respects aliases, and leaves final rendering to FreakQuery whenever possible.
