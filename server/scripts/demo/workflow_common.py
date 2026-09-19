"""Shared pieces of the Briefdesk workflow export.

Holds the three CSV shapes, time handling, and the derivation of stage visits and
hourly review load from a flat list of workflow events. The live export and the
synthetic sample both feed events through the same functions, so both sets of CSVs
are produced by identical logic.

Standard library only: these scripts run from a laptop against a deployed instance,
where nothing from server/requirements.txt is installed.
"""

import csv
import datetime
import math
import os
from collections import OrderedDict
from zoneinfo import ZoneInfo


EVENT_COLUMNS = [
    "timestamp_utc",
    "timestamp_local",
    "item_id",
    "item_reference",
    "title",
    "report_type",
    "severity",
    "priority",
    "urgency",
    "operation",
    "team",
    "from_stage",
    "to_stage",
    "user",
    "version",
]

INTERVAL_COLUMNS = [
    "item_id",
    "item_reference",
    "title",
    "report_type",
    "severity",
    "team",
    "stage",
    "entered_at_utc",
    "entered_at_local",
    "entered_by",
    "entered_operation",
    "left_at_utc",
    "left_at_local",
    "left_by",
    "left_operation",
    "duration_minutes",
    "still_open",
]

HOUR_COLUMNS = [
    "hour_local",
    "entered_review",
    "queue_end_of_hour_avg",
    "queue_end_of_hour_max",
    "median_wait_minutes",
    "p90_wait_minutes",
    "distinct_reviewers",
    "days_observed",
]

# Operations after which the item is out of the production workflow. A later event
# (a restore, an amendment) opens a fresh stage visit.
TERMINAL_OPERATIONS = {"publish", "spike", "kill", "takedown"}

DEFAULT_TIMEZONE = "Europe/Prague"
DEFAULT_REVIEW_STAGE = "Review"


# -- time -----------------------------------------------------------------


def get_timezone(name):
    try:
        return ZoneInfo(name)
    except Exception as err:
        raise SystemExit("unknown timezone %r (%s)" % (name, err))


def parse_api_datetime(value):
    """Parse the `2026-09-18T14:58:40+0000` form Eve returns, as an aware UTC datetime."""
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    elif len(text) >= 5 and text[-5] in "+-" and text[-3] != ":":
        text = text[:-2] + ":" + text[-2:]
    parsed = datetime.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def parse_iso(value):
    """Parse a timestamp this tool wrote into a CSV."""
    if not value:
        return None
    return datetime.datetime.fromisoformat(value)


def parse_boundary(value, tz, end_of_day=False):
    """Parse a --since / --until argument. A bare date means local midnight."""
    if not value:
        return None
    text = value.strip()
    try:
        if len(text) == 10:
            day = datetime.date.fromisoformat(text)
            moment = datetime.datetime.combine(day, datetime.time(0, 0), tzinfo=tz)
            if end_of_day:
                moment += datetime.timedelta(days=1)
            return moment.astimezone(datetime.timezone.utc)
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        raise SystemExit("cannot read date %r, use YYYY-MM-DD or a full ISO timestamp" % value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed.astimezone(datetime.timezone.utc)


def utc_iso(moment):
    if moment is None:
        return ""
    return moment.astimezone(datetime.timezone.utc).isoformat()


def local_iso(moment, tz):
    if moment is None:
        return ""
    return moment.astimezone(tz).isoformat()


# -- small numerics -------------------------------------------------------


def percentile(values, pct):
    """Linear interpolation between the two closest ranks. None for an empty list."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct / 100.0
    low = int(math.floor(rank))
    high = int(math.ceil(rank))
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def round_or_blank(value, digits=1):
    if value is None:
        return ""
    return ("%%.%df" % digits) % value


# -- derivation -----------------------------------------------------------


def stage_key(row):
    return "%s\x1f%s" % (row.get("team", ""), row.get("to_stage", ""))


def build_intervals(events, horizon, tz):
    """One row per item per stage visit.

    `events` must already be ordered and carry `to_stage` as the stage the item sits
    in after the event. A visit that is still running at `horizon` is measured to it
    and flagged `still_open`.
    """
    by_item = OrderedDict()
    for row in events:
        by_item.setdefault(row["item_id"], []).append(row)

    intervals = []
    for item_id, rows in by_item.items():
        rows = sorted(rows, key=lambda r: (r["timestamp_utc"], r.get("version") or 0))
        current = None
        for row in rows:
            if row["operation"] in TERMINAL_OPERATIONS:
                if current is not None:
                    intervals.append(_close(current, row, tz))
                    current = None
                continue
            if not row.get("to_stage"):
                continue
            if current is None:
                current = _open(row)
            elif stage_key(row) != current["key"]:
                intervals.append(_close(current, row, tz))
                current = _open(row)
        if current is not None:
            intervals.append(_close(current, None, tz, horizon))
    return intervals


def _open(row):
    return {
        "key": stage_key(row),
        "item_id": row["item_id"],
        "item_reference": row["item_reference"],
        "title": row["title"],
        "report_type": row["report_type"],
        "severity": row["severity"],
        "team": row["team"],
        "stage": row["to_stage"],
        "entered_at": row["timestamp_utc"],
        "entered_by": row["user"],
        "entered_operation": row["operation"],
    }


def _close(visit, row, tz, horizon=None):
    left_at = row["timestamp_utc"] if row is not None else horizon
    duration = (left_at - visit["entered_at"]).total_seconds() / 60.0
    out = dict(visit)
    out["left_at"] = left_at
    out["left_by"] = row["user"] if row is not None else ""
    out["left_operation"] = row["operation"] if row is not None else ""
    out["duration_minutes"] = max(duration, 0.0)
    out["still_open"] = row is None
    out["entered_at_local"] = visit["entered_at"].astimezone(tz)
    out["left_at_local"] = left_at.astimezone(tz)
    return out


def is_review_stage(name, review_names):
    return (name or "").strip().lower() in review_names


def build_review_load(intervals, events, tz, review_names, horizon=None):
    """Hour-of-day profile of the review queue, aggregated over every day in range."""
    review_visits = [v for v in intervals if is_review_stage(v["stage"], review_names)]

    entered = [0] * 24
    waits = [[] for _ in range(24)]
    for visit in review_visits:
        hour = visit["entered_at_local"].hour
        entered[hour] += 1
        if not visit["still_open"]:
            waits[hour].append(visit["duration_minutes"])

    # Someone counts as a reviewer for an hour when they acted on an item that was
    # already in Review. The move that puts an item into Review is the analyst handing
    # it over, so it is read from `from_stage`, not `to_stage`.
    reviewers = [set() for _ in range(24)]
    for row in events:
        if not is_review_stage(row.get("from_stage"), review_names):
            continue
        user = (row.get("user") or "").strip()
        if user:
            reviewers[row["timestamp_utc"].astimezone(tz).hour].add(user)

    days = _observed_days(events, tz)
    queues = [[] for _ in range(24)]
    for day in days:
        for hour in range(24):
            edge = datetime.datetime.combine(day, datetime.time(hour), tzinfo=tz) + datetime.timedelta(hours=1)
            edge = edge.astimezone(datetime.timezone.utc)
            # An hour that had not ended when the export was taken was never observed. Counting it
            # as an empty queue would read as "everything had been dealt with" on the very hour the
            # work arrived, because every open visit is measured only up to the horizon.
            if horizon is not None and edge > horizon:
                continue
            queues[hour].append(sum(1 for v in review_visits if v["entered_at"] <= edge < v["left_at"]))

    rows = []
    for hour in range(24):
        sizes = queues[hour]
        rows.append(
            {
                "hour_local": "%02d" % hour,
                "entered_review": entered[hour],
                "queue_end_of_hour_avg": round_or_blank(sum(sizes) / len(sizes) if sizes else None, 2),
                "queue_end_of_hour_max": max(sizes) if sizes else "",
                "median_wait_minutes": round_or_blank(percentile(waits[hour], 50)),
                "p90_wait_minutes": round_or_blank(percentile(waits[hour], 90)),
                "distinct_reviewers": len(reviewers[hour]),
                "days_observed": len(days),
            }
        )
    return rows


def _observed_days(events, tz):
    if not events:
        return []
    local = [row["timestamp_utc"].astimezone(tz).date() for row in events]
    first, last = min(local), max(local)
    out = []
    day = first
    while day <= last:
        out.append(day)
        day += datetime.timedelta(days=1)
    return out


# -- output ---------------------------------------------------------------


def write_events_csv(path, events, tz):
    rows = []
    for row in events:
        out = {key: row.get(key, "") for key in EVENT_COLUMNS}
        out["timestamp_utc"] = utc_iso(row["timestamp_utc"])
        out["timestamp_local"] = local_iso(row["timestamp_utc"], tz)
        rows.append(out)
    _write(path, EVENT_COLUMNS, rows)


def write_intervals_csv(path, intervals, tz):
    rows = []
    for visit in intervals:
        rows.append(
            {
                "item_id": visit["item_id"],
                "item_reference": visit["item_reference"],
                "title": visit["title"],
                "report_type": visit["report_type"],
                "severity": visit["severity"],
                "team": visit["team"],
                "stage": visit["stage"],
                "entered_at_utc": utc_iso(visit["entered_at"]),
                "entered_at_local": local_iso(visit["entered_at"], tz),
                "entered_by": visit["entered_by"],
                "entered_operation": visit["entered_operation"],
                "left_at_utc": utc_iso(visit["left_at"]),
                "left_at_local": local_iso(visit["left_at"], tz),
                "left_by": visit["left_by"],
                "left_operation": visit["left_operation"],
                "duration_minutes": round_or_blank(visit["duration_minutes"]),
                "still_open": "yes" if visit["still_open"] else "no",
            }
        )
    rows.sort(key=lambda r: (r["entered_at_utc"], r["item_reference"]))
    _write(path, INTERVAL_COLUMNS, rows)


def write_hours_csv(path, rows):
    _write(path, HOUR_COLUMNS, rows)


def _write(path, columns, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_all(out_dir, events, tz, review_names, horizon):
    """Write the three CSVs and return the derived collections for reuse."""
    intervals = build_intervals(events, horizon, tz)
    hours = build_review_load(intervals, events, tz, review_names, horizon)
    write_events_csv(os.path.join(out_dir, "events.csv"), events, tz)
    write_intervals_csv(os.path.join(out_dir, "stage_intervals.csv"), intervals, tz)
    write_hours_csv(os.path.join(out_dir, "review_load_by_hour.csv"), hours)
    return intervals, hours
