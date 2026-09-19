#!/usr/bin/env python3
"""Export Briefdesk workflow data from a live Superdesk instance.

Reads the read-only `archive_history` resource over the REST API, resolves ids to
team, stage and user names, joins item metadata from `archive` and `published`, and
writes three CSVs:

  events.csv               one row per workflow event
  stage_intervals.csv      one row per item per stage visit
  review_load_by_hour.csv  hour-of-day profile of the review queue

The script only issues GET requests apart from the login POST, so it can never change
the instance.

  SUPERDESK_URL=https://host SUPERDESK_USER=admin SUPERDESK_PASSWORD=admin \
      python3 workflow_export.py --out ../../../workflow-export/live --report
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import workflow_common as wc
from sdapi import ApiError, Superdesk, log

PAGE_SIZE = 200
# Elasticsearch refuses `from` beyond its index.max_result_window, 10000 by default.
DEEP_PAGING_LIMIT = 10000


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=os.environ.get("SUPERDESK_URL"), help="instance URL, or SUPERDESK_URL")
    parser.add_argument("--user", default=os.environ.get("SUPERDESK_USER"), help="username, or SUPERDESK_USER")
    parser.add_argument(
        "--password", default=os.environ.get("SUPERDESK_PASSWORD"), help="password, or SUPERDESK_PASSWORD"
    )
    parser.add_argument("--since", help="only events from this moment, YYYY-MM-DD or full ISO, local time")
    parser.add_argument("--until", help="only events before this moment, YYYY-MM-DD or full ISO, local time")
    parser.add_argument("--team", action="append", help="limit to this team name, repeatable")
    parser.add_argument("--out", default="workflow-export/live", help="output directory")
    parser.add_argument("--timezone", default=wc.DEFAULT_TIMEZONE, help="local timezone for the report and the hours")
    parser.add_argument(
        "--review-stage",
        action="append",
        help="stage name that counts as review, repeatable, default %s" % wc.DEFAULT_REVIEW_STAGE,
    )
    parser.add_argument("--exclude-locks", action="store_true", help="drop item_lock and item_unlock events")
    parser.add_argument("--report", action="store_true", help="also render report.html into the output directory")
    parser.add_argument("--insecure", action="store_true", help="skip TLS certificate verification")
    return parser.parse_args(argv)


# -- fetching -------------------------------------------------------------


def fetch_reference(sd):
    """Id to name maps for the things `archive_history` only stores as ids."""
    desks = {d["_id"]: d.get("name") or d["_id"] for d in sd.find_all("desks", max_results=PAGE_SIZE)}
    stages = {s["_id"]: s.get("name") or s["_id"] for s in sd.find_all("stages", max_results=PAGE_SIZE)}
    users = {}
    for user in sd.find_all("users", max_results=PAGE_SIZE):
        users[user["_id"]] = user.get("display_name") or user.get("username") or user["_id"]
    profiles = {c["_id"]: c.get("label") or c["_id"] for c in sd.find_all("content_types", max_results=PAGE_SIZE)}
    return {"desks": desks, "stages": stages, "users": users, "profiles": profiles}


def fetch_history(sd, since, until):
    """Every history record in the window, oldest first."""
    where = {}
    if since:
        where.setdefault("_created", {})["$gte"] = since.strftime("%Y-%m-%dT%H:%M:%S+0000")
    if until:
        where.setdefault("_created", {})["$lt"] = until.strftime("%Y-%m-%dT%H:%M:%S+0000")

    records = []
    page = 1
    while True:
        params = {"max_results": PAGE_SIZE, "page": page, "sort": '[("_created",1)]'}
        if where:
            params["where"] = json.dumps(where)
        batch = sd.get("archive_history", params).get("_items") or []
        records.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        page += 1
    # The server side filter is a convenience; the window is enforced here as well so a
    # backend that ignores it cannot widen the export.
    out = []
    for record in records:
        moment = wc.parse_api_datetime(record.get("_created"))
        if moment is None:
            continue
        if since and moment < since:
            continue
        if until and moment >= until:
            continue
        record["_moment"] = moment
        out.append(record)
    out.sort(key=lambda r: (r["_moment"], str(r.get("_id"))))
    return out


def fetch_items(sd, item_ids):
    """Metadata for every item that appears in the history, from archive then published."""
    wanted = set(item_ids)
    found = {}
    for resource in ("archive", "published"):
        for doc in _scan(sd, resource, wanted):
            key = doc.get("guid") or doc.get("_id")
            if key in wanted and key not in found:
                found[key] = doc
        if len(found) == len(wanted):
            break

    missing = sorted(wanted - set(found))
    for item_id in missing:
        for resource in ("archive", "published", "archived"):
            try:
                doc = sd.get_item(resource, item_id)
            except ApiError:
                doc = None
            if doc:
                found[item_id] = doc
                break
    return found


def _scan(sd, resource, wanted):
    """Page through an elastic backed resource until everything wanted has been seen."""
    start = 0
    while start < DEEP_PAGING_LIMIT:
        source = json.dumps({"query": {"match_all": {}}, "size": PAGE_SIZE, "from": start})
        try:
            batch = sd.get(resource, {"source": source}).get("_items") or []
        except ApiError as err:
            log("  could not read %s (%s), continuing without it" % (resource, err.status), 0)
            return
        for doc in batch:
            yield doc
        if len(batch) < PAGE_SIZE:
            return
        start += PAGE_SIZE


# -- shaping --------------------------------------------------------------


def severity_of(item):
    for entry in item.get("subject") or []:
        if entry.get("scheme") == "severity":
            return entry.get("name") or entry.get("qcode") or ""
    return ""


def item_facts(item, profiles):
    if not item:
        return {"item_reference": "", "title": "", "report_type": "", "severity": "", "priority": "", "urgency": ""}
    profile = item.get("profile") or item.get("type") or ""
    return {
        "item_reference": item.get("slugline") or "",
        "title": item.get("headline") or "",
        "report_type": profiles.get(profile, profile),
        "severity": severity_of(item),
        "priority": item.get("priority") if item.get("priority") is not None else "",
        "urgency": item.get("urgency") if item.get("urgency") is not None else "",
    }


def build_events(history, items, reference, exclude_locks):
    """Turn history records into workflow events with resolved names.

    `archive_history` stores a move as the whole updated item, so `update.task` carries
    the stage the item lands in but never the one it came from. The previous stage is
    therefore carried forward from the item's own earlier events, and events that do not
    touch `task` inherit the stage the item was already in.
    """
    desks, stages, users = reference["desks"], reference["stages"], reference["users"]
    profiles = reference["profiles"]
    last_seen = {}
    unknown_stage = 0
    events = []

    for record in history:
        operation = record.get("operation") or ""
        if exclude_locks and operation in ("item_lock", "item_unlock"):
            continue
        item_id = record.get("item_id") or ""
        facts = item_facts(items.get(item_id), profiles)
        update = record.get("update") or {}
        task = update.get("task") or {}

        previous = last_seen.get(item_id, {"team": "", "stage": ""})
        if task.get("desk") or task.get("stage"):
            team = desks.get(str(task.get("desk")), str(task.get("desk") or ""))
            stage = stages.get(str(task.get("stage")), str(task.get("stage") or ""))
        else:
            team, stage = previous["team"], previous["stage"]
        if not stage:
            unknown_stage += 1

        row = dict(facts)
        row.update(
            {
                "timestamp_utc": record["_moment"],
                "item_id": item_id,
                "operation": operation,
                "team": team,
                "from_stage": previous["stage"],
                "to_stage": stage,
                "user": users.get(str(record.get("user_id")), "") if record.get("user_id") else "",
                "version": record.get("version") or "",
            }
        )
        events.append(row)
        last_seen[item_id] = {"team": team, "stage": stage}

    return events, unknown_stage


def filter_teams(events, teams):
    wanted = {name.strip().lower() for name in teams}
    return [row for row in events if (row["team"] or "").strip().lower() in wanted]


# -- main -----------------------------------------------------------------


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if not args.url:
        raise SystemExit("no instance URL: pass --url or set SUPERDESK_URL")
    if not args.user or not args.password:
        raise SystemExit("no credentials: pass --user and --password or set SUPERDESK_USER and SUPERDESK_PASSWORD")

    tz = wc.get_timezone(args.timezone)
    since = wc.parse_boundary(args.since, tz)
    until = wc.parse_boundary(args.until, tz, end_of_day=True)
    review_names = {name.strip().lower() for name in (args.review_stage or [wc.DEFAULT_REVIEW_STAGE])}
    out_dir = os.path.abspath(args.out)

    sd = Superdesk(args.url, insecure=args.insecure)
    log("logging in to %s" % sd.base_url)
    try:
        sd.login(args.user, args.password)
    except ApiError as err:
        raise SystemExit("login failed: %s" % err)

    log("reading teams, stages, users and report types")
    reference = fetch_reference(sd)
    log("  %d teams, %d stages, %d users" % (len(reference["desks"]), len(reference["stages"]), len(reference["users"])))

    log("reading archive_history")
    history = fetch_history(sd, since, until)
    log("  %d history records" % len(history))
    if not history:
        raise SystemExit("no history in this window, nothing to export")

    item_ids = sorted({record.get("item_id") for record in history if record.get("item_id")})
    log("reading item metadata for %d items" % len(item_ids))
    items = fetch_items(sd, item_ids)
    if len(items) < len(item_ids):
        log("  %d items could not be resolved, their rows carry ids only" % (len(item_ids) - len(items)))

    events, unknown_stage = build_events(history, items, reference, args.exclude_locks)
    if args.team:
        events = filter_teams(events, args.team)
        log("  %d events after the team filter" % len(events))
    if not events:
        raise SystemExit("no events left after filtering, nothing to export")
    if unknown_stage:
        log("  %d events carry no stage, the item had none recorded earlier in the window" % unknown_stage)

    horizon = until or max(row["timestamp_utc"] for row in events)
    intervals, hours = wc.write_all(out_dir, events, tz, review_names, horizon)

    log("wrote %s" % out_dir)
    log("  events.csv               %d rows" % len(events), 1)
    log("  stage_intervals.csv      %d rows" % len(intervals), 1)
    log("  review_load_by_hour.csv  %d rows" % len(hours), 1)
    open_visits = sum(1 for v in intervals if v["still_open"])
    log("  %d stage visits still open at %s" % (open_visits, wc.local_iso(horizon, tz)), 1)

    if args.report:
        import workflow_report

        label = "Live export from %s, taken %s" % (
            sd.base_url.rsplit("/api", 1)[0],
            datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M %Z"),
        )
        path = workflow_report.render_directory(out_dir, tz_name=args.timezone, source_label=label, sample=False)
        log("  report.html              %s" % path, 1)


if __name__ == "__main__":
    main()
