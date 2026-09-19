#!/usr/bin/env python3
"""Generate a synthetic month of Briefdesk workflow events in the export's CSV format.

The live demo instance was seeded in a single afternoon, so its real history has no
daily rhythm and cannot show what a month of production looks like. This script
simulates one for the invented firm Halden Risk Intelligence: a 24/7 Watch team,
alerts all day, daily briefs converging on review in the late afternoon, and fewer
reviewers on shift than analysts after 17:00. The review queue is a real first come
first served simulation against reviewer shifts, so the afternoon backlog is produced
by the model rather than written into it.

Nothing here touches any instance. Output is deterministic for a given seed.

  python3 workflow_sample.py --out ../../../workflow-export/sample --report
"""

import argparse
import datetime
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workflow_common as wc

DEFAULT_SEED = 20260918
DEFAULT_START = "2026-08-17"
DEFAULT_DAYS = 28

WATCH = "Watch"
REGIONS = ["Europe", "MENA", "Americas"]
PREFIX = {"Europe": "EU", "MENA": "ME", "Americas": "AM", WATCH: "WA"}

# Invented staff. The five named in CONTRACT.md plus colleagues in the same style, so a
# 24/7 rota and three regional teams have enough people to be believable.
ANALYSTS = {
    "Europe": [("Maja Lindqvist", (8, 0), (16, 30)), ("Sofia Bergman", (10, 0), (18, 30))],
    "MENA": [("Omar Nasser", (7, 0), (15, 30)), ("Nadia Haddad", (9, 0), (17, 30))],
    "Americas": [("Marco Ruiz", (12, 0), (20, 30))],
}
WATCH_OFFICERS = [
    ("Dana Reyes", (6, 0), (14, 0)),
    ("Ida Nystrom", (14, 0), (22, 0)),
    ("Jonas Weller", (22, 0), (6, 0)),
]
# Reviewer rotas. Two out of hours duty reviewers cover every team round the clock, and
# each team has its own reviewer during its working day. Tomas Havel is off at 17:00,
# which is exactly when the European briefs arrive, so between 17:00 and 18:00 Lucia
# Ferro covers three teams on her own.
ALL_DAYS = {0, 1, 2, 3, 4, 5, 6}
WEEKDAYS = {0, 1, 2, 3, 4}
DUTY = [
    ("Ana Reinholt", ALL_DAYS, (2, 0), (10, 0)),
    ("Rasmus Holt", ALL_DAYS, (18, 0), (2, 0)),
]
REVIEWERS = {
    "Europe": DUTY
    + [
        ("Tomas Havel", WEEKDAYS, (8, 30), (17, 0)),
        ("Lucia Ferro", WEEKDAYS, (10, 0), (18, 30)),
        ("Lucia Ferro", {5, 6}, (10, 0), (16, 0)),
    ],
    "MENA": DUTY
    + [
        ("Petr Kral", {6, 0, 1, 2, 3}, (7, 0), (15, 30)),
        ("Lucia Ferro", WEEKDAYS, (10, 0), (18, 30)),
        ("Lucia Ferro", {5, 6}, (10, 0), (16, 0)),
    ],
    "Americas": DUTY
    + [
        ("Elena Varga", WEEKDAYS, (13, 0), (21, 0)),
        ("Lucia Ferro", WEEKDAYS, (10, 0), (18, 30)),
    ],
}

REPORT_TYPES = ["Alert", "Daily Brief", "Country Assessment", "RFI Response"]
SERVICE_MINUTES = {
    "Alert": (6, 22),
    "Daily Brief": (18, 48),
    "Country Assessment": (35, 95),
    "RFI Response": (14, 40),
}
SEVERITIES = ["Critical", "High", "Medium", "Low", "Informational"]
SEVERITY_WEIGHTS = {
    "Alert": [4, 20, 38, 26, 12],
    "Daily Brief": [2, 14, 44, 30, 10],
    "Country Assessment": [1, 10, 40, 34, 15],
    "RFI Response": [1, 8, 36, 38, 17],
}
PRIORITY_OF = {"Critical": (1, 1), "High": (2, 2), "Medium": (3, 3), "Low": (4, 4), "Informational": (5, 5)}

# Alerts arrive round the clock but cluster on the European working day and again as
# the afternoon closes, which is what pushes the review queue into the evening.
ALERT_WEIGHT_BY_HOUR = [
    3, 2, 2, 2, 3, 5, 8, 12, 14, 13, 11, 10,
    10, 11, 14, 16, 17, 14, 10, 8, 7, 6, 5, 4,
]

CITIES = {
    "Europe": [
        "Hamburg", "Gdansk", "Lyon", "Rotterdam", "Prague", "Milan", "Valencia", "Antwerp",
        "Leipzig", "Katowice", "Bologna", "Utrecht", "Malmo", "Bratislava",
    ],
    "MENA": [
        "Alexandria", "Casablanca", "Amman", "Dubai", "Tunis", "Jeddah", "Izmir",
        "Manama", "Muscat", "Beirut", "Sfax", "Aqaba",
    ],
    "Americas": [
        "Monterrey", "Veracruz", "Bogota", "Sao Paulo", "Guadalajara", "Panama City",
        "Santiago", "Rosario", "Callao", "Houston",
    ],
}
ALERT_TEMPLATES = [
    "Road blockade reported on the {city} ring corridor",
    "Warehouse staff at {city} announce a two day stoppage",
    "Protest march expected through central {city} on Friday",
    "Port congestion builds at {city} after a crane failure",
    "Rail freight through {city} suspended for signalling work",
    "Cargo theft ring active on the approach to {city}",
    "Power interruption affects the {city} industrial zone",
    "Customs slowdown reported at the {city} terminal",
    "Fuel supply disruption reported around {city}",
    "Severe weather warning issued for the {city} region",
    "Cyber intrusion attempt reported at a {city} logistics operator",
    "Checkpoint delays lengthen on the {city} approach roads",
    "Public transport strike called in {city} for next week",
    "Flooding closes two access roads south of {city}",
]
BRIEF_CLIENTS = ["Nordfreight Logistics", "Aurelia Pharma", "Castellan Energy", "all recipients"]
BRIEF_TEMPLATES = [
    "{region} daily brief for {client}, {date}",
    "{region} evening brief for {client}, {date}",
]
ASSESSMENT_TEMPLATES = [
    "{city} corridor risk assessment",
    "Country assessment update, {city} operations",
    "Supply route review, {city} to the coast",
]
RFI_TEMPLATES = [
    "RFI response, site security around {city}",
    "RFI response, travel risk for {city}",
    "RFI response, contractor vetting in {city}",
]


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="workflow-export/sample", help="output directory")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="RNG seed, same seed same output")
    parser.add_argument("--start", default=DEFAULT_START, help="first local day, YYYY-MM-DD")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="number of days to simulate")
    parser.add_argument("--timezone", default=wc.DEFAULT_TIMEZONE, help="local timezone the rhythm is built in")
    parser.add_argument("--alerts-per-day", type=float, default=26.0, help="average alerts the Watch team raises")
    parser.add_argument("--report", action="store_true", help="also render report.html into the output directory")
    return parser.parse_args(argv if argv is not None else sys.argv[1:])


# -- shift helpers --------------------------------------------------------


def _at(tz, day, hm):
    return datetime.datetime.combine(day, datetime.time(hm[0], hm[1]), tzinfo=tz)


def on_shift(moment, weekdays, start, end):
    if end <= start:  # a rota that crosses midnight
        minutes = moment.hour * 60 + moment.minute
        if minutes >= start[0] * 60 + start[1]:
            return moment.weekday() in weekdays
        previous = (moment - datetime.timedelta(days=1)).weekday()
        return previous in weekdays and minutes < end[0] * 60 + end[1]
    if moment.weekday() not in weekdays:
        return False
    minutes = moment.hour * 60 + moment.minute
    return start[0] * 60 + start[1] <= minutes < end[0] * 60 + end[1]


def next_on_shift(moment, weekdays, start, end, tz, limit_days=10):
    """First minute at or after `moment` when this rota is covered."""
    probe = moment.replace(second=0, microsecond=0)
    horizon = probe + datetime.timedelta(days=limit_days)
    while probe < horizon:
        if on_shift(probe, weekdays, start, end):
            return probe
        # jump to the next shift start rather than stepping minute by minute
        candidate = _at(tz, probe.date(), start)
        if candidate <= probe:
            candidate = _at(tz, probe.date() + datetime.timedelta(days=1), start)
        probe = candidate
    return None


class ReviewDesk:
    """First come first served review queue for one team, against real rotas."""

    def __init__(self, team, tz):
        self.team = team
        self.tz = tz
        self.slots = []
        for name, weekdays, start, end in REVIEWERS[team]:
            self.slots.append({"name": name, "weekdays": weekdays, "start": start, "end": end, "free_at": None})

    def take(self, arrival):
        best = None
        for slot in self.slots:
            ready = arrival if slot["free_at"] is None else max(arrival, slot["free_at"])
            start = next_on_shift(ready, slot["weekdays"], slot["start"], slot["end"], self.tz)
            if start is None:
                continue
            # next_on_shift works in whole minutes, so a reviewer must never be given a
            # start earlier than the moment the item actually reached the queue.
            start = max(start, ready)
            if best is None or start < best[0]:
                best = (start, slot)
        if best is None:
            return None, None
        return best[0], best[1]

    def occupy(self, slot, until):
        slot["free_at"] = until


# -- item generation ------------------------------------------------------


class Builder:
    def __init__(self, rng, tz, start_day, days):
        self.rng = rng
        self.tz = tz
        self.start_day = start_day
        self.days = days
        self.counter = {key: 100 for key in PREFIX}
        self.raw = []

    def reference(self, team):
        self.counter[team] += 1
        return "BD-%s-%d" % (PREFIX[team], self.counter[team])

    def record(self, item, moment, operation, user, team, stage):
        self.raw.append(
            {
                "timestamp_utc": moment.astimezone(datetime.timezone.utc),
                "item_id": item["item_id"],
                "item_reference": item["reference"],
                "title": item["title"],
                "report_type": item["report_type"],
                "severity": item["severity"],
                "priority": item["priority"],
                "urgency": item["urgency"],
                "operation": operation,
                "team": team,
                "stage": stage,
                "user": user,
                "version": item["version"],
            }
        )
        item["version"] += 1

    def new_item(self, report_type, region, title):
        severity = self.rng.choices(SEVERITIES, weights=SEVERITY_WEIGHTS[report_type])[0]
        priority, urgency = PRIORITY_OF[severity]
        reference = self.reference(region if report_type != "Alert" else WATCH)
        return {
            "item_id": "urn:briefdesk:sample:%s" % reference,
            "reference": reference,
            "title": title,
            "report_type": report_type,
            "severity": severity,
            "priority": priority,
            "urgency": urgency,
            "version": 1,
        }

    def jitter(self, low, high):
        return datetime.timedelta(minutes=self.rng.uniform(low, high))

    def analyst_on(self, region, moment):
        """An analyst of this team, preferring one whose shift covers the moment."""
        roster = ANALYSTS[region]
        covering = [a for a in roster if on_shift(moment, {0, 1, 2, 3, 4, 5, 6}, a[1], a[2])]
        pick = self.rng.choice(covering or roster)
        return pick[0]

    def watch_officer_on(self, moment):
        for name, start, end in WATCH_OFFICERS:
            if on_shift(moment, {0, 1, 2, 3, 4, 5, 6}, start, end):
                return name
        return WATCH_OFFICERS[0][0]


def alert_arrivals(rng, tz, start_day, days, per_day):
    """Creation moments for the Watch team's alerts, shaped by the hour of the local day."""
    moments = []
    total = sum(ALERT_WEIGHT_BY_HOUR)
    for offset in range(days):
        day = start_day + datetime.timedelta(days=offset)
        count = max(2, int(round(rng.gauss(per_day * (0.55 if day.weekday() >= 5 else 1.0), 2.0))))
        for _ in range(count):
            hour = rng.choices(range(24), weights=ALERT_WEIGHT_BY_HOUR)[0]
            moments.append(
                datetime.datetime.combine(day, datetime.time(hour, rng.randrange(60)), tzinfo=tz)
                + datetime.timedelta(seconds=rng.randrange(60))
            )
    moments.sort()
    return moments, total


def build_lifecycles(builder, per_day):
    """Everything up to the moment an item enters Review. Returns the review arrivals."""
    rng = builder.rng
    tz = builder.tz
    arrivals = []

    moments, _ = alert_arrivals(rng, tz, builder.start_day, builder.days, per_day)
    for moment in moments:
        region = rng.choices(REGIONS, weights=[52, 30, 18])[0]
        city = rng.choice(CITIES[region])
        item = builder.new_item("Alert", region, rng.choice(ALERT_TEMPLATES).format(city=city))
        officer = builder.watch_officer_on(moment)
        builder.record(item, moment, "create", officer, WATCH, "Incoming")
        triaged = moment + builder.jitter(1, 8)
        builder.record(item, triaged, "move", officer, WATCH, "Triage")
        if rng.random() < 0.18:
            builder.record(item, triaged + builder.jitter(2, 25), "spike", officer, WATCH, "Triage")
            continue
        sent = triaged + builder.jitter(2, 20)
        builder.record(item, sent, "move", officer, region, "Incoming")
        picked = sent + builder.jitter(5, 70)
        analyst = builder.analyst_on(region, picked)
        builder.record(item, picked, "move", analyst, region, "Analysis")
        drafted = picked + builder.jitter(1, 4)
        builder.record(item, drafted, "item_lock", analyst, region, "Analysis")
        written = drafted + builder.jitter(12, 75)
        builder.record(item, written, "update", analyst, region, "Analysis")
        builder.record(item, written + builder.jitter(0, 2), "item_unlock", analyst, region, "Analysis")
        submitted = written + builder.jitter(2, 12)
        builder.record(item, submitted, "move", analyst, region, "Review")
        arrivals.append((submitted, item, region, analyst))

    for offset in range(builder.days):
        day = builder.start_day + datetime.timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        for region in REGIONS:
            arrivals.extend(_daily_briefs(builder, day, region))
        if offset >= 2 and offset % 7 in (1, 4):
            region = REGIONS[offset % 3]
            arrivals.extend(_assessment(builder, day, region))
        if offset % 5 == 2:
            region = REGIONS[(offset + 1) % 3]
            arrivals.extend(_rfi(builder, day, region))

    arrivals.sort(key=lambda entry: entry[0])
    return arrivals


def _daily_briefs(builder, day, region):
    """The client briefs a team ships each weekday, all handed to review around 17:00."""
    rng, tz = builder.rng, builder.tz
    out = []
    for index in range(rng.randrange(4, 7)):
        title = rng.choice(BRIEF_TEMPLATES).format(
            region=region, client=BRIEF_CLIENTS[index % len(BRIEF_CLIENTS)], date=day.isoformat()
        )
        item = builder.new_item("Daily Brief", region, title)
        started = _at(tz, day, (8, 30)) + builder.jitter(0, 140)
        # The convergence the customer complains about: briefs are handed over around 17:00.
        submitted = _at(tz, day, (17, 15)) + datetime.timedelta(minutes=rng.gauss(0, 18))
        analyst = builder.analyst_on(region, started)
        builder.record(item, started, "create", analyst, region, "Analysis")
        builder.record(item, started + builder.jitter(1, 6), "item_lock", analyst, region, "Analysis")
        for _ in range(rng.randrange(2, 5)):
            builder.record(item, _between(rng, started, submitted, 10, 8), "update", analyst, region, "Analysis")
        builder.record(item, submitted - builder.jitter(1, 4), "item_unlock", analyst, region, "Analysis")
        builder.record(item, submitted, "move", analyst, region, "Review")
        out.append((submitted, item, region, analyst))
    return out


def _between(rng, start, end, after_minutes, before_minutes):
    """A moment inside a drafting window, so an edit never lands after the handover."""
    low = start + datetime.timedelta(minutes=after_minutes)
    high = end - datetime.timedelta(minutes=before_minutes)
    if high <= low:
        return low
    span = (high - low).total_seconds()
    return low + datetime.timedelta(seconds=rng.uniform(0, span))


def _assessment(builder, day, region):
    rng, tz = builder.rng, builder.tz
    city = rng.choice(CITIES[region])
    item = builder.new_item("Country Assessment", region, rng.choice(ASSESSMENT_TEMPLATES).format(city=city))
    started = _at(tz, day - datetime.timedelta(days=2), (10, 0)) + builder.jitter(0, 180)
    analyst = builder.analyst_on(region, started)
    builder.record(item, started, "create", analyst, region, "Analysis")
    builder.record(item, started + builder.jitter(30, 300), "update", analyst, region, "Analysis")
    submitted = _at(tz, day, (14, 0)) + builder.jitter(0, 180)
    builder.record(item, submitted, "move", analyst, region, "Review")
    return [(submitted, item, region, analyst)]


def _rfi(builder, day, region):
    rng, tz = builder.rng, builder.tz
    city = rng.choice(CITIES[region])
    item = builder.new_item("RFI Response", region, rng.choice(RFI_TEMPLATES).format(city=city))
    started = _at(tz, day, (9, 0)) + builder.jitter(0, 240)
    submitted = started + builder.jitter(90, 330)
    analyst = builder.analyst_on(region, started)
    builder.record(item, started, "create", analyst, region, "Analysis")
    builder.record(item, _between(rng, started, submitted, 20, 10), "update", analyst, region, "Analysis")
    builder.record(item, submitted, "move", analyst, region, "Review")
    return [(submitted, item, region, analyst)]


def run_review(builder, arrivals):
    """Serve the review queue per team, which is what produces the afternoon backlog."""
    rng = builder.rng
    desks = {region: ReviewDesk(region, builder.tz) for region in REGIONS}
    pending = list(arrivals)
    guard = 0
    while pending and guard < 100000:
        guard += 1
        pending.sort(key=lambda entry: entry[0])
        arrival, item, region, analyst = pending.pop(0)
        desk = desks[region]
        start, slot = desk.take(arrival)
        if start is None:
            continue
        low, high = SERVICE_MINUTES[item["report_type"]]
        service = datetime.timedelta(minutes=rng.uniform(low, high))
        finish = start + service
        desk.occupy(slot, finish)
        reviewer = slot["name"]
        builder.record(item, start, "item_lock", reviewer, region, "Review")
        if rng.random() < 0.12:
            builder.record(item, finish, "item_unlock", reviewer, region, "Review")
            builder.record(item, finish, "move", reviewer, region, "Analysis")
            redo = finish + builder.jitter(25, 200)
            builder.record(item, redo, "update", analyst, region, "Analysis")
            again = redo + builder.jitter(5, 45)
            builder.record(item, again, "move", analyst, region, "Review")
            pending.append((again, item, region, analyst))
            continue
        builder.record(item, finish - builder.jitter(0, 2), "update", reviewer, region, "Review")
        builder.record(item, finish, "item_unlock", reviewer, region, "Review")
        builder.record(item, finish + datetime.timedelta(seconds=rng.randrange(20, 240)), "publish", reviewer,
                       region, "Review")


def finalise(raw):
    """Order the raw records and fill from_stage and to_stage the way the export does."""
    rows = sorted(raw, key=lambda r: (r["timestamp_utc"], r["item_reference"], r["version"]))
    last = {}
    events = []
    for row in rows:
        previous = last.get(row["item_id"], "")
        event = {key: row[key] for key in ("item_id", "item_reference", "title", "report_type", "severity",
                                           "priority", "urgency", "operation", "team", "user", "version")}
        event["timestamp_utc"] = row["timestamp_utc"]
        event["from_stage"] = previous
        event["to_stage"] = row["stage"]
        events.append(event)
        last[row["item_id"]] = row["stage"]
    return events


def main(argv=None):
    args = parse_args(argv)
    tz = wc.get_timezone(args.timezone)
    try:
        start_day = datetime.date.fromisoformat(args.start)
    except ValueError:
        raise SystemExit("--start must be YYYY-MM-DD")
    if args.days < 1:
        raise SystemExit("--days must be at least 1")

    rng = random.Random(args.seed)
    builder = Builder(rng, tz, start_day, args.days)
    arrivals = build_lifecycles(builder, args.alerts_per_day)
    run_review(builder, arrivals)
    events = finalise(builder.raw)

    end = datetime.datetime.combine(
        start_day + datetime.timedelta(days=args.days), datetime.time(0, 0), tzinfo=tz
    ).astimezone(datetime.timezone.utc)
    horizon = max(end, max(row["timestamp_utc"] for row in events))
    out_dir = os.path.abspath(args.out)
    intervals, hours = wc.write_all(out_dir, events, tz, {wc.DEFAULT_REVIEW_STAGE.lower()}, horizon)

    wc_log = print
    wc_log("wrote %s" % out_dir)
    wc_log("  events.csv               %d rows" % len(events))
    wc_log("  stage_intervals.csv      %d rows" % len(intervals))
    wc_log("  review_load_by_hour.csv  %d rows" % len(hours))
    wc_log("  %d items over %d days, seed %d" % (len({r["item_id"] for r in events}), args.days, args.seed))

    if args.report:
        import workflow_report

        label = "Generated sample: %d days of new items from %s, seed %d, Halden Risk Intelligence (invented)" % (
            args.days,
            start_day.isoformat(),
            args.seed,
        )
        path = workflow_report.render_directory(out_dir, tz_name=args.timezone, source_label=label, sample=True)
        wc_log("  report.html              %s" % path)


if __name__ == "__main__":
    main()
