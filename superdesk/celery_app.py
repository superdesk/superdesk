'''
Created on May 29, 2014

@author: ioan
'''


import redis
import arrow
import superdesk
from bson import ObjectId
from celery import Celery
from kombu.serialization import register
from eve.io.mongo import MongoJSONEncoder
from eve.utils import str_to_date
from flask import json


celery = Celery(__name__)
TaskBase = celery.Task


def try_cast(v):
    try:
        str_to_date(v)  # try if it matches format
        return arrow.get(v).datetime  # return timezone aware time
    except:
        try:
            return ObjectId(v)
        except:
            return v


def cast_item(o):
    with superdesk.app.app_context():
        for k, v in o.items():
            if isinstance(v, dict):
                cast_item(v)
            else:
                o[k] = try_cast(v)


def loads(s):
    o = json.loads(s)

    if not o.get('args', None):
        o['args'] = []

    if not o.get('kwargs', None):
        o['kwargs'] = {}

    for v in o['args']:
        if isinstance(v, dict):
            cast_item(v)

    for k, v in o['kwargs'].items():
        cast_item(v)

    return o


def dumps(o):
    with superdesk.app.app_context():
        return MongoJSONEncoder().encode(o)


register('eve/json', dumps, loads, content_type='application/json')


class AppContextTask(TaskBase):
    abstract = True
    serializer = 'eve/json'

    def __call__(self, *args, **kwargs):
        with superdesk.app.app_context():
            return super().__call__(*args, **kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            superdesk.app.sentry.captureException()
        except:
            pass


celery.Task = AppContextTask


def init_celery(app):
    celery.conf.update(app.config)
    app.celery = celery


def add_subtask_to_progress(task_id):
    return _update_subtask_progress(task_id, total=True)


def finish_subtask_from_progress(task_id):
    return _update_subtask_progress(task_id, current=True)


def finish_task_for_progress(task_id):
    return _update_subtask_progress(task_id, done=True)


def update_key(redis_db, key, flag):
    if flag:
        crt_value = redis_db.incr(key)
    else:
        crt_value = redis_db.get(key)

    if crt_value:
        crt_value = int(crt_value)
    else:
        crt_value = 0

    return crt_value


def _update_subtask_progress(task_id, current=None, total=None, done=None):
    redis_db = redis.from_url(celery.conf['CELERY_RESULT_BACKEND'])

    current_key = 'current_%s' % task_id
    total_key = 'total_%s' % task_id
    done_key = 'done_%s' % task_id

    crt_current = update_key(redis_db, current_key, current)
    crt_total = update_key(redis_db, total_key, total)
    crt_done = update_key(redis_db, done_key, done)

    if crt_done and crt_current == crt_total:
        redis_db.delete(current_key)
        redis_db.delete(crt_total)
        redis_db.delete(done_key)

    return task_id, crt_current, crt_total
