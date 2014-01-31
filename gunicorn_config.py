
import os

port = int(os.environ.get('PORT', 5000))
bind = '%s:%d' % ('0.0.0.0', port)
workers = 5
timeout = 21

if port == 5000:
    debug = True
    accesslog = '-'
    access_log_format = '%(h)s %(l)s %(u)s %(t)s “%(r)s” %(s)s %(b)s “%(f)s” %(D)s'
