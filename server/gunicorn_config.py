
import os
import multiprocessing

bind = '0.0.0.0:%s' % os.environ.get('PORT', '5000')
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))

accesslog = '-'
access_log_format = '%(r)s\nstatus=%(s)s time=%(T)ss bytes=%(b)s pid=%(p)s remote=%(h)s referer=%(f)s'

reload = 'SUPERDESK_RELOAD' in os.environ

timeout = int(os.environ.get('WEB_TIMEOUT', 30))
