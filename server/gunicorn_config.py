
import os
import multiprocessing
from urllib.parse import urlparse

workers = multiprocessing.cpu_count() * 2 + 1

if os.environ.get('SUPERDESK_URL'):
    url = urlparse(os.environ.get('SUPERDESK_URL'))
    bind = url.netloc
else:
    bind = ':%s' % os.environ.get('PORT', 5000)

accesslog = '-'
access_log_format = '%(r)s\nstatus=%(s)s time=%(T)ss bytes=%(b)s pid=%(p)s remote=%(h)s referer=%(f)s'
