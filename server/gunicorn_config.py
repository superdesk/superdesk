
import os
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:%s' % os.environ.get('PORT', 5000)

accesslog = '-'
access_log_format = '%(r)s\nstatus=%(s)s time=%(T)ss bytes=%(b)s pid=%(p)s remote=%(h)s referer=%(f)s'
