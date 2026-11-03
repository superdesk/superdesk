#!/usr/bin/env python3
"""Snapshot and marker helpers for run_seed.sh (documentation screenshot instance, SDESK-8055).

Run it from the server folder. superdesk-core resolves dump/full/<name> and dump/records/<name>.json.bz2
against the working directory of the `rest` process (superdesk/commands/data_manipulation.py), and this
script writes to the same relative paths.

Commands:
    prepare-base <e2e dump dir> <name>   copy a client-core e2e full dump, rename its database folders
                                         to this instance's database names and write a record for it
    record <name>                        write dump/records/<name>.json.bz2 for dump/full/<name>
    has <name>...                        exit 0 when every named snapshot is on disk
    marker-check <version>               exit 0 when the seed marker for <version> exists
    marker-write <version> <docs ref> <docs sha>
    archive <version> <name>...          store the named snapshots in Mongo (GridFS)
    extract <version>                    put the archived snapshots of <version> back on disk

Exit status 1 means "no" (no marker, snapshot or archive) and 2 means an error, so that run_seed.sh never
mistakes an unreachable database for a missing marker and wipes a seeded instance.
"""

import bz2
import datetime
import io
import json
import shutil
import sys
import tarfile
import time
from pathlib import Path
from urllib.parse import urlparse

DUMP_DIR = Path("dump/full")
RECORD_DIR = Path("dump/records")


def fail(message):
    print("snapshots.py: " + message, file=sys.stderr)
    sys.exit(2)


def db_name(uri):
    return urlparse(uri).path.lstrip("/").split("?")[0]


def instance_db_names():
    from superdesk import default_settings as ds

    return {
        "main": db_name(ds.MONGO_URI),
        "archived": db_name(ds.ARCHIVED_URI),
        "legal_archive": db_name(ds.LEGAL_ARCHIVE_URI),
        "contentapi": db_name(ds.CONTENTAPI_MONGO_URI),
    }


def state_db():
    """Database that holds the marker and the archived snapshots.

    It sits next to the instance databases on purpose: snapshot restores and the prepopulate endpoint only
    drop the four Superdesk databases, so it survives them, while Fireq's "reset db" drops every database
    whose name starts with the instance name, so a reset also forgets the seed and snapshots.
    """
    from pymongo import MongoClient
    from superdesk import default_settings as ds

    client = MongoClient(ds.MONGO_URI, serverSelectionTimeoutMS=10000)
    return client[db_name(ds.MONGO_URI) + "_autodocs"]


def e2e_db_kind(folder_name):
    if folder_name.startswith("contentapi"):
        return "contentapi"
    if folder_name.endswith("_legal_archive"):
        return "legal_archive"
    if folder_name.endswith("_archived"):
        return "archived"
    return "main"


def write_record(name):
    if not (DUMP_DIR / name).is_dir():
        fail("no dump at {}".format(DUMP_DIR / name))
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "metadata": {
            "started": time.time(),
            "applied_updates": [],
            "base_dump": str(DUMP_DIR / name),
            "description": "documentation screenshot instance snapshot {}".format(name),
        },
        "events": [],
    }
    tmp = RECORD_DIR / "{}.json.bz2.tmp".format(name)
    with bz2.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(record, f)
    tmp.replace(RECORD_DIR / "{}.json.bz2".format(name))


def replace_dir(tmp, dest):
    if dest.exists():
        shutil.rmtree(dest)
    tmp.rename(dest)


def prepare_base(src, name):
    src = Path(src)
    if not src.is_dir():
        fail("no e2e dump at {}".format(src))
    names = instance_db_names()
    folders = {}
    for folder in sorted(p for p in src.iterdir() if p.is_dir()):
        kind = e2e_db_kind(folder.name)
        if kind in folders:
            fail(
                "{} and {} both look like the {} database".format(
                    folders[kind].name, folder.name, kind
                )
            )
        folders[kind] = folder
    if "main" not in folders:
        fail("no main database folder in {}".format(src))

    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DUMP_DIR / "{}.tmp".format(name)
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    for kind, folder in folders.items():
        shutil.copytree(folder, tmp / names[kind])
        print("{} -> {}".format(folder.name, names[kind]))
    replace_dir(tmp, DUMP_DIR / name)
    write_record(name)


def has(names):
    for name in names:
        if (
            not (DUMP_DIR / name).is_dir()
            or not (RECORD_DIR / "{}.json.bz2".format(name)).is_file()
        ):
            sys.exit(1)


def marker_check(version):
    sys.exit(0 if state_db()["marker"].find_one({"_id": version}) else 1)


def marker_write(version, docs_ref, docs_sha):
    state_db()["marker"].replace_one(
        {"_id": version},
        {
            "_id": version,
            "seeded_at": datetime.datetime.now(datetime.timezone.utc),
            "docs_ref": docs_ref,
            "docs_sha": docs_sha,
        },
        upsert=True,
    )


def archive_filename(version):
    return "snapshots-{}.tar.gz".format(version)


def archive(version, names):
    import gridfs

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name in names:
            tar.add(str(DUMP_DIR / name))
            tar.add(str(RECORD_DIR / "{}.json.bz2".format(name)))
    fs = gridfs.GridFS(state_db(), collection="snapshots")
    for old in fs.find():
        fs.delete(old._id)
    fs.put(buf.getvalue(), filename=archive_filename(version), names=names)
    print("archived {} ({} kB)".format(", ".join(names), len(buf.getvalue()) // 1024))


def extract(version):
    import gridfs

    fs = gridfs.GridFS(state_db(), collection="snapshots")
    stored = fs.find_one({"filename": archive_filename(version)})
    if stored is None:
        sys.exit(1)
    with tarfile.open(fileobj=io.BytesIO(stored.read()), mode="r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or path.parts[0] != "dump":
                fail("unexpected path {} in the archive".format(member.name))
            if not (member.isfile() or member.isdir()):
                fail("unexpected entry type for {} in the archive".format(member.name))
        for name in stored.names:
            if (DUMP_DIR / name).exists():
                shutil.rmtree(DUMP_DIR / name)
        if hasattr(tarfile, "data_filter"):
            tar.extractall(".", members=members, filter="data")
        else:
            tar.extractall(".", members=members)
    print("restored {} from the archive".format(", ".join(stored.names)))


def main(argv):
    if not argv:
        fail("missing command, see the docstring")
    command, args = argv[0], argv[1:]
    if command == "prepare-base" and len(args) == 2:
        prepare_base(*args)
    elif command == "record" and len(args) == 1:
        write_record(args[0])
    elif command == "has" and args:
        has(args)
    elif command == "marker-check" and len(args) == 1:
        marker_check(args[0])
    elif command == "marker-write" and len(args) == 3:
        marker_write(*args)
    elif command == "archive" and len(args) >= 2:
        archive(args[0], args[1:])
    elif command == "extract" and len(args) == 1:
        extract(args[0])
    else:
        fail("bad arguments: {}".format(" ".join(argv)))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except SystemExit:
        raise
    except Exception as err:
        fail("{}: {}".format(type(err).__name__, err))
