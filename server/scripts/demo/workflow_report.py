#!/usr/bin/env python3
"""Render the Briefdesk workflow report from the three exported CSVs.

One self contained HTML file: inline CSS, inline SVG charts, no external scripts or
fonts. The same code renders the live export and the synthetic sample; the sample is
labelled as such in the header and on every chart.

  python3 workflow_report.py --in ../../../workflow-export/live
  python3 workflow_report.py --in ../../../workflow-export/sample --sample
"""

import argparse
import collections
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workflow_common as wc

TITLE = "Workflow load, Halden Risk Intelligence"

CSS = """
:root{
  --navy:#10243E; --green:#1FB57A; --amber:#E8A317; --red:#B42318;
  --bg:#ffffff; --surface:#f5f8fa; --ink:#10243E; --muted:#5B7083;
  --line:#dde5ed; --track:#e7eef4; --bar1:#1FB57A; --bar2:#10243E; --chip:#eef3f8;
  --sev-critical:#B42318; --sev-high:#D9480F; --sev-medium:#B27407;
  --sev-low:#2E7D5B; --sev-info:#5B7083;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0A1726; --surface:#12263B; --ink:#E7EEF5; --muted:#9AAFC4;
    --line:#22384E; --track:#1B3148; --bar1:#1FB57A; --bar2:#7FA6CC; --chip:#1B3148;
    --sev-critical:#F16A5F; --sev-high:#F58A3C; --sev-medium:#E8A317;
    --sev-low:#4FC79B; --sev-info:#9AAFC4;
  }
}
:root[data-theme="dark"]{
  --bg:#0A1726; --surface:#12263B; --ink:#E7EEF5; --muted:#9AAFC4;
  --line:#22384E; --track:#1B3148; --bar1:#1FB57A; --bar2:#7FA6CC; --chip:#1B3148;
  --sev-critical:#F16A5F; --sev-high:#F58A3C; --sev-medium:#E8A317;
  --sev-low:#4FC79B; --sev-info:#9AAFC4;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:16px; line-height:1.55; overflow-wrap:break-word;
}
.wrap{max-width:900px; margin:0 auto; padding:32px 16px 64px}
header.top{border-bottom:3px solid var(--green); padding-bottom:18px; margin-bottom:26px}
.brand{display:flex; align-items:center; gap:10px; margin-bottom:14px}
.mark{width:22px; height:22px; flex:0 0 22px}
.brand span{font-weight:700; letter-spacing:.02em; font-size:15px}
h1{font-size:28px; line-height:1.2; margin:0 0 8px}
.sub{color:var(--muted); font-size:14px; margin:0}
.chips{display:flex; flex-wrap:wrap; gap:8px; margin-top:12px}
.chip{
  display:inline-block; background:var(--chip); color:var(--muted);
  border-radius:999px; padding:3px 11px; font-size:12px; font-weight:600; letter-spacing:.03em;
}
.chip-sample{background:var(--amber); color:#241a02}
.chip-real{background:var(--green); color:#04261a}
h2{font-size:19px; margin:38px 0 6px; padding-top:10px; border-top:1px solid var(--line)}
h2:first-of-type{border-top:none}
p{margin:10px 0}
.note{color:var(--muted); font-size:14px}
.callout{
  background:var(--surface); border-left:4px solid var(--green);
  padding:12px 14px; border-radius:0 8px 8px 0; margin:14px 0; font-size:15px;
}
.callout.warn{border-left-color:var(--amber)}
.tiles{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:18px 0 6px}
@media (max-width:620px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tile{background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:12px 14px}
.tile .v{font-size:23px; font-weight:700; line-height:1.15}
.tile .k{font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; margin-top:3px}
figure{margin:16px 0 4px}
figure svg{display:block; width:100%; max-width:640px; height:auto; margin:0 auto}
figcaption{color:var(--muted); font-size:13px; margin-top:8px; display:flex; flex-wrap:wrap; gap:8px; align-items:center}
table{width:100%; border-collapse:collapse; font-size:14px; margin:14px 0}
th,td{text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top}
th{font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); font-weight:700}
td.num,th.num{text-align:right; font-variant-numeric:tabular-nums}
.sev{font-weight:700}
.sev-Critical{color:var(--sev-critical)} .sev-High{color:var(--sev-high)}
.sev-Medium{color:var(--sev-medium)} .sev-Low{color:var(--sev-low)}
.sev-Informational{color:var(--sev-info)}
footer{margin-top:44px; padding-top:16px; border-top:1px solid var(--line); color:var(--muted); font-size:13px}
ul{padding-left:20px} li{margin:5px 0}
@media (max-width:620px){
  .wrap{padding:22px 16px 48px}
  h1{font-size:23px}
  table.stack thead{display:none}
  table.stack tr{display:block; border-bottom:1px solid var(--line); padding:10px 0}
  table.stack td{display:flex; justify-content:space-between; gap:14px; border:none; padding:3px 0}
  table.stack td::before{content:attr(data-k); color:var(--muted); font-size:12px;
    text-transform:uppercase; letter-spacing:.04em; font-weight:700; flex:0 0 auto}
  table.stack td.num{text-align:right}
}
@media print{
  :root{--bg:#fff; --surface:#f5f8fa; --ink:#10243E; --muted:#5B7083;
        --line:#dde5ed; --track:#e7eef4; --bar2:#10243E; --chip:#eef3f8;
        --sev-critical:#B42318; --sev-high:#D9480F; --sev-medium:#B27407;
        --sev-low:#2E7D5B; --sev-info:#5B7083}
  body{font-size:12px}
  .wrap{max-width:none; padding:0}
  figure,table,.callout{break-inside:avoid; page-break-inside:avoid}
  h2{break-after:avoid; page-break-after:avoid}
  *{-webkit-print-color-adjust:exact; print-color-adjust:exact}
}
"""

MARK = (
    '<svg class="mark" viewBox="0 0 32 32" aria-hidden="true">'
    '<rect width="32" height="32" rx="7" fill="#10243E"/>'
    '<g transform="translate(3.2 3.2) scale(0.8)">'
    '<rect x="4" y="2" width="24" height="4" rx="2" fill="#FFFFFF"/>'
    '<rect x="4" y="10" width="4" height="4" rx="1" fill="#1FB57A"/>'
    '<rect x="12" y="10" width="16" height="4" rx="2" fill="#1FB57A"/>'
    '<rect x="4" y="18" width="24" height="4" rx="2" fill="#FFFFFF"/>'
    '<rect x="4" y="26" width="16" height="4" rx="2" fill="#FFFFFF"/>'
    '</g></svg>'
)


def esc(value):
    return html.escape("" if value is None else str(value))


def num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def minutes_words(value):
    if value is None or value == "":
        return "n/a"
    total = int(round(num(value)))
    if total < 60:
        return "%d min" % total
    hours, rest = divmod(total, 60)
    if hours < 48:
        return "%dh %02dm" % (hours, rest)
    return "%dd %dh" % divmod(hours, 24)


def hour_words(hour):
    return "%02d:00 to %02d:00" % (hour, (hour + 1) % 24)


# -- charts ---------------------------------------------------------------

W = 640
FONT_TICK = 19
FONT_LABEL = 20


def _sample_stamp(sample, x, y):
    if not sample:
        return ""
    return (
        '<text x="%d" y="%d" text-anchor="end" font-size="17" font-weight="700" '
        'letter-spacing="1.5" fill="var(--amber)">SAMPLE DATA</text>' % (x, y)
    )


def _nice_top(value):
    if value <= 0:
        return 1
    step = 1
    while value / step > 5:
        step *= 2 if str(step)[0] == "1" else (2.5 if str(step)[0] == "2" else 2)
        step = int(round(step)) or 1
    return int(step * -(-value // step))


def _line_run(points):
    """One unbroken stretch of the line series. A single point would be invisible as a polyline."""
    if not points:
        return ""
    if len(points) == 1:
        return '<circle cx="%.1f" cy="%.1f" r="3" fill="var(--bar2)"/>' % points[0]
    return (
        '<polyline points="%s" fill="none" stroke="var(--bar2)" stroke-width="2.5" '
        'stroke-linejoin="round"/>' % " ".join("%.1f,%.1f" % point for point in points)
    )


def hour_chart(values, line_values=None, line_label=None, bar_label="items", sample=False, height=300,
               highlight=True):
    """24 bars across the hours of the local day, with an optional second series as a line."""
    left, right, top, bottom = 46, 46 if line_values else 16, 46, 40
    plot_w = W - left - right
    plot_h = height - top - bottom
    slot = plot_w / 24.0
    bar_w = max(8.0, slot * 0.62)

    top_value = _nice_top(max(values) if values else 1)
    peak = max(range(24), key=lambda h: values[h]) if any(values) else None
    mean = (sum(values) / 24.0) if values else 0

    parts = ['<svg viewBox="0 0 %d %d" role="img" font-family="inherit">' % (W, height)]
    parts.append(_sample_stamp(sample, W - 4, 16))

    for tick in range(0, 5):
        value = top_value * tick / 4.0
        y = top + plot_h - plot_h * tick / 4.0
        parts.append(
            '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line)" stroke-width="1"/>'
            % (left, y, W - right, y)
        )
        parts.append(
            '<text x="%d" y="%.1f" text-anchor="end" font-size="%d" fill="var(--muted)">%s</text>'
            % (left - 7, y + 6, FONT_TICK, _fmt_tick(value))
        )

    for hour in range(24):
        value = values[hour]
        bar_h = plot_h * (value / top_value) if top_value else 0
        x = left + slot * hour + (slot - bar_w) / 2.0
        y = top + plot_h - bar_h
        colour = "var(--bar1)"
        if highlight and peak is not None and hour == peak and value > 0:
            colour = "var(--red)"
        elif highlight and mean > 0 and value >= mean * 1.5:
            colour = "var(--amber)"
        parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
            % (x, y, bar_w, max(bar_h, 0.8), colour)
        )

    if line_values:
        # A None hour was never observed, which is not the same as a queue of zero, so the line
        # breaks there rather than being drawn down to the axis.
        known = [value for value in line_values if value is not None]
        line_top = (_nice_top(max(known)) if known else 1) or 1
        run = []
        for hour in list(range(24)) + [None]:
            value = line_values[hour] if hour is not None else None
            if value is None:
                parts.append(_line_run(run))
                run = []
                continue
            x = left + slot * hour + slot / 2.0
            y = top + plot_h - plot_h * (value / line_top)
            run.append((x, y))
        for tick in (0, 2, 4):
            value = line_top * tick / 4.0
            y = top + plot_h - plot_h * tick / 4.0
            parts.append(
                '<text x="%d" y="%.1f" text-anchor="start" font-size="%d" fill="var(--bar2)">%s</text>'
                % (W - right + 7, y + 6, FONT_TICK, _fmt_tick(value))
            )

    for hour in range(0, 24, 3):
        x = left + slot * hour + slot / 2.0
        parts.append(
            '<text x="%.1f" y="%d" text-anchor="middle" font-size="%d" fill="var(--muted)">%02d</text>'
            % (x, height - 16, FONT_TICK, hour)
        )
    parts.append(
        '<text x="%d" y="%d" text-anchor="middle" font-size="%d" fill="var(--muted)">hour of the local day</text>'
        % (W / 2, height - 1, FONT_TICK - 2, )
    )

    parts.append('<rect x="%d" y="14" width="13" height="13" rx="2" fill="var(--bar1)"/>' % left)
    parts.append(
        '<text x="%d" y="25" font-size="%d" fill="var(--muted)">%s</text>'
        % (left + 19, FONT_LABEL, esc(bar_label))
    )
    if line_values:
        offset = left + 19 + len(bar_label) * 10 + 22
        parts.append(
            '<line x1="%d" y1="20" x2="%d" y2="20" stroke="var(--bar2)" stroke-width="2.5"/>'
            % (offset, offset + 20)
        )
        parts.append(
            '<text x="%d" y="25" font-size="%d" fill="var(--muted)">%s</text>'
            % (offset + 26, FONT_LABEL, esc(line_label))
        )
    parts.append("</svg>")
    return "".join(parts)


def _fmt_tick(value):
    if value >= 10 or value == int(value):
        return "%d" % round(value)
    return "%.1f" % value


def paired_bar_chart(rows, sample=False, series=("median", "p90"), unit="minutes", shared_scale=True):
    """One block per label: the label on its own line, then two bars below it.

    Keeping the label on its own line is what lets long team and stage names stay
    readable at phone width without a horizontal scroll. `shared_scale` is for two
    series in the same unit; counts of different things get a scale each, so a small
    series is not flattened by a large one.
    """
    if not rows:
        return ""
    row_h = 62
    height = 34 + row_h * len(rows) + 6
    if shared_scale:
        top_a = top_b = max([max(r["a"], r["b"]) for r in rows] + [1])
    else:
        top_a = max([r["a"] for r in rows] + [1])
        top_b = max([r["b"] for r in rows] + [1])
    bar_left = 4
    bar_max = W - 150

    parts = ['<svg viewBox="0 0 %d %d" role="img" font-family="inherit">' % (W, height)]
    parts.append(_sample_stamp(sample, W - 4, 14))
    parts.append('<rect x="%d" y="22" width="13" height="13" rx="2" fill="var(--bar1)"/>' % bar_left)
    parts.append(
        '<text x="%d" y="33" font-size="%d" fill="var(--muted)">%s</text>'
        % (bar_left + 19, FONT_LABEL, esc(series[0]))
    )
    offset = bar_left + 19 + len(series[0]) * 10 + 24
    parts.append('<rect x="%d" y="22" width="13" height="13" rx="2" fill="var(--bar2)"/>' % offset)
    parts.append(
        '<text x="%d" y="33" font-size="%d" fill="var(--muted)">%s</text>'
        % (offset + 19, FONT_LABEL, esc(series[1]))
    )

    for index, row in enumerate(rows):
        base = 34 + row_h * index
        parts.append(
            '<text x="%d" y="%d" font-size="%d" font-weight="600" fill="var(--ink)">%s</text>'
            % (bar_left, base + 20, FONT_LABEL, esc(row["label"]))
        )
        for offset_y, value, top, colour in (
            (26, row["a"], top_a, "var(--bar1)"),
            (42, row["b"], top_b, "var(--bar2)"),
        ):
            width = bar_max * (value / top) if top else 0
            parts.append(
                '<rect x="%d" y="%d" width="%.1f" height="11" rx="3" fill="var(--track)"/>'
                % (bar_left, base + offset_y, bar_max)
            )
            parts.append(
                '<rect x="%d" y="%d" width="%.1f" height="11" rx="3" fill="%s"/>'
                % (bar_left, base + offset_y, max(width, 1.5), colour)
            )
            parts.append(
                '<text x="%d" y="%d" font-size="%d" fill="var(--muted)">%s</text>'
                % (bar_max + 12, base + offset_y + 10, FONT_TICK, esc(_fmt_unit(value, unit)))
            )
    parts.append("</svg>")
    return "".join(parts)


def _fmt_unit(value, unit):
    if unit == "minutes":
        return minutes_words(value)
    if value == int(value):
        return "%d" % value
    return "%.1f" % value


# -- report ---------------------------------------------------------------


def load(directory):
    data = {}
    for name in ("events", "stage_intervals", "review_load_by_hour"):
        path = os.path.join(directory, name + ".csv")
        if not os.path.exists(path):
            raise SystemExit("missing %s, run the export first" % path)
        data[name] = wc.read_csv(path)
    return data


def summarise(data, tz, review_names):
    events = data["events"]
    intervals = data["stage_intervals"]
    hours = data["review_load_by_hour"]

    local_days = sorted({row["timestamp_local"][:10] for row in events if row["timestamp_local"]})
    review_visits = [v for v in intervals if wc.is_review_stage(v["stage"], review_names)]
    closed_review = [v for v in review_visits if v["still_open"] == "no"]

    entered = [int(num(h["entered_review"])) for h in hours]
    queue_avg = [num(h["queue_end_of_hour_avg"]) for h in hours]
    # An hour the export horizon fell inside or before has no queue measurement at all. It is kept
    # apart from a measured zero so the chart can break the line rather than draw it to the axis.
    queue_seen = [h["queue_end_of_hour_avg"] != "" for h in hours]
    reviewers = [int(num(h["distinct_reviewers"])) for h in hours]

    return {
        "events": events,
        "intervals": intervals,
        "hours": hours,
        "days": local_days,
        "items": sorted({row["item_id"] for row in events}),
        "review_visits": review_visits,
        "closed_review": closed_review,
        "entered": entered,
        "queue_avg": queue_avg,
        "queue_seen": queue_seen,
        "reviewers": reviewers,
        "peak_hour": max(range(24), key=lambda h: entered[h]) if any(entered) else None,
        "operations": collections.Counter(row["operation"] for row in events),
        # Too few review arrivals, or too few days, for an hour of day pattern to mean
        # anything. The report then reports the shortage instead of a peak.
        "thin": len(local_days) < 3 or sum(entered) < 20,
    }


def stage_rows(intervals):
    by_stage = collections.OrderedDict()
    for visit in intervals:
        if visit["still_open"] != "no":
            continue
        key = "%s / %s" % (visit["team"], visit["stage"])
        by_stage.setdefault(key, []).append(num(visit["duration_minutes"]))
    rows = []
    for label, values in by_stage.items():
        rows.append(
            {
                "label": label,
                "a": wc.percentile(values, 50) or 0,
                "b": wc.percentile(values, 90) or 0,
                "count": len(values),
            }
        )
    rows.sort(key=lambda r: r["b"], reverse=True)
    return rows


def team_rows(events, intervals, review_names):
    teams = collections.OrderedDict()
    for row in events:
        team = row["team"] or "(no team)"
        entry = teams.setdefault(team, {"events": 0, "items": set(), "review": [], "visits": 0})
        entry["events"] += 1
        entry["items"].add(row["item_id"])
    for visit in intervals:
        team = visit["team"] or "(no team)"
        entry = teams.setdefault(team, {"events": 0, "items": set(), "review": [], "visits": 0})
        entry["visits"] += 1
        if wc.is_review_stage(visit["stage"], review_names) and visit["still_open"] == "no":
            entry["review"].append(num(visit["duration_minutes"]))
    rows = []
    for team, entry in teams.items():
        rows.append(
            {
                "label": team,
                "items": len(entry["items"]),
                "events": entry["events"],
                "visits": entry["visits"],
                "review_count": len(entry["review"]),
                "review_median": wc.percentile(entry["review"], 50),
                "review_p90": wc.percentile(entry["review"], 90),
            }
        )
    rows.sort(key=lambda r: r["items"], reverse=True)
    return rows


def longest_waits(intervals, review_names, limit=12):
    closed = [v for v in intervals if v["still_open"] == "no"]
    review = [v for v in closed if wc.is_review_stage(v["stage"], review_names)]
    pool = review or closed
    pool = sorted(pool, key=lambda v: num(v["duration_minutes"]), reverse=True)
    return pool[:limit], bool(review)


def render(data, tz_name, source_label, sample, review_names):
    tz = wc.get_timezone(tz_name)
    s = summarise(data, tz, review_names)
    out = []
    add = out.append

    flag = (
        '<span class="chip chip-sample">Sample data</span>'
        if sample
        else '<span class="chip chip-real">Live instance data</span>'
    )
    period = "%s to %s" % (s["days"][0], s["days"][-1]) if s["days"] else "no events"

    add("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">")
    add('<meta name="viewport" content="width=device-width, initial-scale=1">')
    add("<title>%s</title>" % esc(TITLE + (" (sample data)" if sample else "")))
    add('<meta name="color-scheme" content="light dark">')
    add("<style>%s</style></head><body><div class=\"wrap\">" % CSS)

    add('<header class="top"><div class="brand">%s<span>Briefdesk</span></div>' % MARK)
    add("<h1>%s</h1>" % esc(TITLE))
    add('<p class="sub">%s</p>' % esc(source_label))
    add('<div class="chips">%s<span class="chip">%s</span><span class="chip">%s local time</span>'
        '<span class="chip">%d %s</span></div></header>'
        % (flag, esc(period), esc(tz_name), len(s["days"]), "day" if len(s["days"]) == 1 else "days"))

    if sample:
        add(
            '<div class="callout warn"><strong>This report is rendered from generated sample data.</strong> '
            "Nothing here was measured on a running system. It shows the shape of the answer the export gives "
            "once a month of real traffic has gone through the workflow, for the invented firm Halden Risk "
            "Intelligence and its invented staff.</div>"
        )
    else:
        add(
            '<div class="callout"><strong>This report is rendered from a real export.</strong> '
            "Every number below comes from the <code>archive_history</code> resource of the live demo "
            "instance over the REST API. Nothing was invented, and nothing was written to the instance.</div>"
        )
        if s["thin"]:
            add(
                '<div class="callout warn"><strong>The demo instance holds a single session of seeded work, '
                "not a month of production.</strong> Ten of its reports were walked through Analysis, "
                "Review, Held and release by the named staff, so the completed stage visits and the reviewer "
                "activity below are operations the product recorded as they happened. That walk ran inside "
                "half an hour of one day, so the waits are minutes rather than hours, there is no daily "
                "rhythm here to find and no pressure point worth naming. Everything else on the instance was "
                "created straight into the stage it sits in, which is why so many visits are still open. "
                "Read this part as proof that the export works against a real instance, and the companion "
                "sample report for the shape of a month of traffic.</div>"
            )

    add('<div class="tiles">')
    for key, value in (
        ("Items", len(s["items"])),
        ("Workflow events", len(s["events"])),
        ("Stage visits", len(s["intervals"])),
        ("Review visits", len(s["review_visits"])),
    ):
        add('<div class="tile"><div class="v">%s</div><div class="k">%s</div></div>' % (value, esc(key)))
    waits = [num(v["duration_minutes"]) for v in s["closed_review"]]
    add(
        '<div class="tile"><div class="v">%s</div><div class="k">Median wait in review</div></div>'
        % esc(minutes_words(wc.percentile(waits, 50)) if waits else "n/a")
    )
    add(
        '<div class="tile"><div class="v">%s</div><div class="k">Peak review hour</div></div>'
        % esc(hour_words(s["peak_hour"]) if s["peak_hour"] is not None and not s["thin"] else "n/a")
    )
    add("</div>")

    add(_section_review_queue(s, tz_name, sample))
    add(_section_stages(s, sample))
    add(_section_teams(s, review_names, sample))
    add(_section_reviewers(s, sample))
    add(_section_longest(s, review_names, sample))

    add("<h2>How this was produced</h2>")
    add(
        "<p>Superdesk records every operation on an item in the read only <code>archive_history</code> "
        "resource. <code>workflow_export.py</code> reads it over the REST API, resolves team, stage, user "
        "and report type ids to names, joins item metadata from <code>archive</code> and <code>published</code>, "
        "and writes <code>events.csv</code>, <code>stage_intervals.csv</code> and "
        "<code>review_load_by_hour.csv</code>. This page is rendered from those three files by "
        "<code>workflow_report.py</code>. The export issues GET requests only.</p>"
    )
    add("<h2>What this data cannot tell you</h2><ul>")
    add(
        "<li>A stage move records the stage the item lands in, never the one it came from, so the "
        "<em>from stage</em> column is derived from the item's own earlier events.</li>"
    )
    add(
        "<li>Release does not record a stage change of its own, so a visit that ends in a release is "
        "measured up to the release, not up to a move into a released stage.</li>"
    )
    add(
        "<li>Time in a stage is wall clock time. It does not distinguish an item being worked on from an "
        "item waiting, unless you read the lock and unlock events alongside it.</li>"
    )
    add(
        "<li>Reviewer availability is inferred from who acted, not from a roster. The export can say who "
        "touched items in an hour, not who was on shift.</li>"
    )
    add("</ul>")

    add("<footer>Halden Risk Intelligence is an invented firm and every person named here is invented. ")
    add("Briefdesk is a working name for Superdesk configured for security and risk intelligence work.</footer>")
    add("</div></body></html>")
    return "".join(out)


def _section_review_queue(s, tz_name, sample):
    out = ["<h2>Review queue by hour of day</h2>"]
    if not any(s["entered"]):
        out.append(
            '<p class="note">No item entered a stage named Review anywhere in this export, so there is no '
            "queue to plot. Either nothing passed through review in this window, or the review stage is "
            "called something other than Review here and <code>--review-stage</code> has to say so.</p>"
        )
        return "".join(out)

    peak = s["peak_hour"]
    total = sum(s["entered"])
    mean = total / 24.0
    if s["thin"]:
        out.append(
            '<div class="callout warn"><strong>There is not enough traffic here to read an hour of day '
            "pattern.</strong> Only %d %s entered a Review stage, across %d %s. The chart is drawn from what "
            "is there, and it is shown so the shape of the answer is visible, not because the peak it marks "
            "means anything.</div>"
            % (total, "item" if total == 1 else "items", len(s["days"]), "day" if len(s["days"]) == 1 else "days")
        )
    else:
        out.append(
            '<div class="callout%s"><strong>%s local time is the pressure point.</strong> %d of the %d review '
            "arrivals in this export land in that hour, %s the average hour, and the review queue ends it at %s "
            "items on average against %s across the day.</div>"
            % (
                " warn" if s["entered"][peak] >= mean * 1.5 else "",
                hour_words(peak),
                s["entered"][peak],
                total,
                ("%.1f times" % (s["entered"][peak] / mean)) if mean else "well above",
                _fmt_tick(s["queue_avg"][peak]),
                _fmt_tick(sum(s["queue_avg"]) / 24.0),
            )
        )
    out.append("<figure>")
    out.append(
        hour_chart(
            s["entered"],
            line_values=[value if seen else None for value, seen in zip(s["queue_avg"], s["queue_seen"])],
            line_label="queue at end of hour",
            bar_label="entered review",
            sample=sample,
            highlight=not s["thin"],
        )
    )
    out.append(
        "<figcaption>Bars: items entering a Review stage, summed over %d %s. Line: average number of items "
        "still in Review at the end of that hour. Hours are %s.%s</figcaption></figure>"
        % (
            len(s["days"]),
            "day" if len(s["days"]) == 1 else "days",
            esc(tz_name),
            ' <span class="chip chip-sample">Sample data</span>' if sample else "",
        )
    )

    rows = [h for h in s["hours"] if int(num(h["entered_review"])) or num(h["queue_end_of_hour_avg"])]
    if rows:
        out.append('<table class="stack"><thead><tr><th>Hour</th><th class="num">Entered</th>')
        out.append('<th class="num">Queue avg</th><th class="num">Queue max</th>')
        out.append('<th class="num">Median wait</th><th class="num">p90 wait</th>')
        out.append('<th class="num">Reviewers</th></tr></thead><tbody>')
        for row in rows:
            out.append(
                "<tr><td data-k=\"Hour\">%s</td>"
                '<td class="num" data-k="Entered">%s</td>'
                '<td class="num" data-k="Queue avg">%s</td>'
                '<td class="num" data-k="Queue max">%s</td>'
                '<td class="num" data-k="Median wait">%s</td>'
                '<td class="num" data-k="p90 wait">%s</td>'
                '<td class="num" data-k="Reviewers">%s</td></tr>'
                % (
                    esc(hour_words(int(row["hour_local"]))),
                    esc(row["entered_review"]),
                    esc(row["queue_end_of_hour_avg"] or "n/a"),
                    esc(row["queue_end_of_hour_max"] or "n/a"),
                    esc(minutes_words(row["median_wait_minutes"]) if row["median_wait_minutes"] else "n/a"),
                    esc(minutes_words(row["p90_wait_minutes"]) if row["p90_wait_minutes"] else "n/a"),
                    esc(row["distinct_reviewers"]),
                )
            )
        out.append("</tbody></table>")
    return "".join(out)


def _section_stages(s, sample):
    rows = stage_rows(s["intervals"])
    out = ["<h2>Time in each stage</h2>"]
    if not rows:
        out.append('<p class="note">No stage visit in this export has finished, so no duration can be measured.</p>')
        return "".join(out)
    out.append(
        "<p>Median and 90th percentile time an item spends in a stage before it moves on or is released. "
        "Only completed visits count; %d visits were still open when the export was taken.</p>"
        % sum(1 for v in s["intervals"] if v["still_open"] == "yes")
    )
    out.append("<figure>")
    out.append(paired_bar_chart(rows[:10], sample=sample, series=("median", "p90")))
    out.append(
        '<figcaption>Longest ninetieth percentile first. %d completed visits in total.%s</figcaption></figure>'
        % (sum(r["count"] for r in rows), ' <span class="chip chip-sample">Sample data</span>' if sample else "")
    )
    return "".join(out)


def _section_teams(s, review_names, sample):
    rows = team_rows(s["events"], s["intervals"], review_names)
    out = ["<h2>Load per team</h2>"]
    if not rows:
        return "".join(out + ['<p class="note">No team could be resolved for these events.</p>'])
    chart_rows = [{"label": r["label"], "a": r["items"], "b": r["events"]} for r in rows]
    out.append("<figure>")
    out.append(
        paired_bar_chart(chart_rows, sample=sample, series=("items", "events"), unit="count", shared_scale=False)
    )
    out.append(
        "<figcaption>Items each team touched and the number of workflow events recorded against them. "
        "The two series count different things, so each bar is drawn against the largest value in its own "
        "series.%s</figcaption></figure>" % (' <span class="chip chip-sample">Sample data</span>' if sample else "")
    )
    out.append('<table class="stack"><thead><tr><th>Team</th><th class="num">Items</th>')
    out.append('<th class="num">Events</th><th class="num">Stage visits</th>')
    out.append('<th class="num">Review visits</th><th class="num">Median review wait</th>')
    out.append('<th class="num">p90 review wait</th></tr></thead><tbody>')
    for row in rows:
        out.append(
            '<tr><td data-k="Team">%s</td><td class="num" data-k="Items">%d</td>'
            '<td class="num" data-k="Events">%d</td><td class="num" data-k="Stage visits">%d</td>'
            '<td class="num" data-k="Review visits">%d</td>'
            '<td class="num" data-k="Median review wait">%s</td>'
            '<td class="num" data-k="p90 review wait">%s</td></tr>'
            % (
                esc(row["label"]),
                row["items"],
                row["events"],
                row["visits"],
                row["review_count"],
                esc(minutes_words(row["review_median"]) if row["review_median"] is not None else "n/a"),
                esc(minutes_words(row["review_p90"]) if row["review_p90"] is not None else "n/a"),
            )
        )
    out.append("</tbody></table>")
    return "".join(out)


def _section_reviewers(s, sample):
    out = ["<h2>Reviewer activity by hour</h2>"]
    if not any(s["reviewers"]):
        out.append(
            '<p class="note">No event was recorded against an item sitting in a Review stage, so there is '
            "no reviewer activity to plot.</p>"
        )
        return "".join(out)
    busiest = max(range(24), key=lambda h: s["reviewers"][h])
    # Naming an arrival peak here would contradict the header tile, which withholds one whenever
    # there is too little traffic for an hour of day pattern to mean anything.
    arrivals = (
        "there is not enough traffic here to say when arrivals peak"
        if s["thin"] or s["peak_hour"] is None
        else "arrivals peak at %s" % hour_words(s["peak_hour"])
    )
    out.append(
        "<p>Distinct people who acted on an item while it sat in Review, counted per hour of the day. "
        "Compare it with the arrivals above: the gap between the two is what a capacity plan has to close. "
        "The widest cover is at %s with %d people; %s.</p>"
        % (hour_words(busiest), s["reviewers"][busiest], arrivals)
    )
    out.append("<figure>")
    out.append(
        hour_chart(s["reviewers"], bar_label="distinct reviewers", sample=sample, height=250, highlight=False)
    )
    out.append(
        '<figcaption>A person is counted once per hour however many items they touched.%s</figcaption></figure>'
        % (' <span class="chip chip-sample">Sample data</span>' if sample else "")
    )
    return "".join(out)


def _section_longest(s, review_names, sample):
    rows, is_review = longest_waits(s["intervals"], review_names)
    out = ["<h2>Longest waits</h2>"]
    if not rows:
        out.append('<p class="note">No completed stage visit to rank.</p>')
        return "".join(out)
    out.append(
        "<p>The %d longest completed %s. This is the list a team lead would work through first.</p>"
        % (len(rows), "waits in Review" if is_review else "stage visits, no Review visit has completed yet")
    )
    out.append('<table class="stack"><thead><tr><th>Reference</th><th>Title</th><th>Team and stage</th>')
    out.append('<th>Severity</th><th>Entered</th><th class="num">Wait</th><th>Moved in by</th>')
    out.append("<th>Moved on by</th></tr></thead><tbody>")
    for row in rows:
        out.append(
            '<tr><td data-k="Reference">%s</td><td data-k="Title">%s</td>'
            '<td data-k="Team and stage">%s</td>'
            '<td data-k="Severity"><span class="sev sev-%s">%s</span></td>'
            '<td data-k="Entered">%s</td><td class="num" data-k="Wait">%s</td>'
            '<td data-k="Moved in by">%s</td><td data-k="Moved on by">%s</td></tr>'
            % (
                esc(row["item_reference"] or row["item_id"]),
                esc(row["title"]),
                esc("%s / %s" % (row["team"], row["stage"])),
                esc((row["severity"] or "none").replace(" ", "")),
                esc(row["severity"] or "not set"),
                esc(row["entered_at_local"][:16].replace("T", " ")),
                esc(minutes_words(row["duration_minutes"])),
                esc(row["entered_by"] or "system"),
                esc(row["left_by"] or "system"),
            )
        )
    out.append("</tbody></table>")
    if sample:
        out.append('<p class="note"><span class="chip chip-sample">Sample data</span> Invented people and items.</p>')
    return "".join(out)


def render_directory(directory, tz_name=wc.DEFAULT_TIMEZONE, source_label="", sample=False, review_names=None,
                     out_path=None):
    data = load(directory)
    names = review_names or {wc.DEFAULT_REVIEW_STAGE.lower()}
    page = render(data, tz_name, source_label, sample, names)
    target = out_path or os.path.join(directory, "report.html")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(page)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="source", required=True, help="directory holding the three CSVs")
    parser.add_argument("--out", help="output file, default report.html next to the CSVs")
    parser.add_argument("--timezone", default=wc.DEFAULT_TIMEZONE, help="timezone the local columns were written in")
    parser.add_argument("--sample", action="store_true", help="label the page and every chart as sample data")
    parser.add_argument("--source-label", default="", help="provenance line under the title")
    parser.add_argument("--review-stage", action="append", help="stage name that counts as review")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    names = {n.strip().lower() for n in (args.review_stage or [wc.DEFAULT_REVIEW_STAGE])}
    label = args.source_label or (
        "Generated sample month" if args.sample else "Exported from a live Superdesk instance"
    )
    path = render_directory(args.source, args.timezone, label, args.sample, names, args.out)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
