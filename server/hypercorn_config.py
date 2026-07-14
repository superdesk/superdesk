import os
import multiprocessing

DEFAULT_MAX_WORKERS = 8

bind = "0.0.0.0:%s" % os.environ.get("PORT", "5000")
default_workers = min(multiprocessing.cpu_count() + 1, DEFAULT_MAX_WORKERS)
workers = int(os.environ.get("WEB_CONCURRENCY", default_workers))
read_timeout = int(os.environ.get("WEB_TIMEOUT", 30))

accesslog = "-"
access_log_format = "%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"

use_reloader = "SUPERDESK_RELOAD" in os.environ
