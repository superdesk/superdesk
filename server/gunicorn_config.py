
import os
import multiprocessing

bind = '0.0.0.0:%s' % os.environ.get('PORT', '5000')
workers = multiprocessing.cpu_count()

accesslog = '-'
access_log_format = '%(r)s\nstatus=%(s)s time=%(T)ss bytes=%(b)s pid=%(p)s remote=%(h)s referer=%(f)s'

if 'TRAVIS' in os.environ:
    # a bit more constraint setup to make errors popup
    workers = 3
    timeout = 10

reload = 'SUPERDESK_RELOAD' in os.environ
