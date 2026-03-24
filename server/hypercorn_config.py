import os

bind = "0.0.0.0:%s" % os.environ.get("PORT", "5000")
_web_concurrency = os.environ.get("WEB_CONCURRENCY")
if _web_concurrency is not None:
    workers = int(_web_concurrency)
else:
    workers = 1

accesslog = "-"
access_log_format = "%(m)s %(U)s status=%(s)s time=%(T)ss size=%(B)sb"

use_reload = "SUPERDESK_RELOAD" in os.environ
read_timeout = int(os.environ.get("WEB_TIMEOUT", 30))
