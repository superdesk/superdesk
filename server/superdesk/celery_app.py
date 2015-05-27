# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

'''
Created on May 29, 2014

@author: ioan
'''


import redis
import arrow
import logging
import werkzeug
import superdesk
from bson import ObjectId
from celery import Celery
from kombu.serialization import register
from eve.io.mongo import MongoJSONEncoder
from eve.utils import str_to_date
from flask import json, current_app as app


logger = logging.getLogger(__name__)
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
            elif isinstance(v, bool):
                pass
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

    kwargs = o['kwargs']
    if isinstance(kwargs, str):
        o['kwargs'] = json.loads(kwargs)
        kwargs = o['kwargs']
    for k, v in kwargs.items():
        if isinstance(v, str):
            kwargs[k] = try_cast(v)

        if isinstance(v, list):
            kwargs[k] = [try_cast(val) for val in v]

        if isinstance(v, dict):
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
            try:
                return super().__call__(*args, **kwargs)
            except werkzeug.exceptions.InternalServerError as e:
                superdesk.app.sentry.captureException()
                logger.exception(e)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            superdesk.app.sentry.captureException()
        except:
            pass


celery.Task = AppContextTask


def init_celery(app):
    celery.conf.update(app.config)
    app.celery = celery
    app.redis = __get_redis(app)


def add_subtask_to_progress(task_id):
    return _update_subtask_progress(task_id, total=True)


def finish_subtask_from_progress(task_id):
    return _update_subtask_progress(task_id, current=True)


def finish_task_for_progress(task_id):
    return _update_subtask_progress(task_id, done=True)


def __get_redis(app_ctx):
    """
    Constructs Redis Client object.
    :return: Redis Client object
    """

    return redis.from_url(app_ctx.config['REDIS_URL'])


def update_key(key, flag=False, db=None):

    if db is None:
        db = app.redis

    if flag:
        crt_value = db.incr(key)
    else:
        crt_value = db.get(key)

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

    crt_current = update_key(current_key, current, redis_db)
    crt_total = update_key(total_key, total, redis_db)
    crt_done = update_key(done_key, done, redis_db)

    if crt_done and crt_current == crt_total:
        redis_db.delete(current_key)
        redis_db.delete(crt_total)
        redis_db.delete(done_key)

    return task_id, crt_current, crt_total


def set_key(key, value=0, db=None):
    """
    Sets the value of a key in Redis
    :param key: Name of the Key
    :param value: Value to be set
    :param db: if None the Redis db object is constructed again
    """

    if db is None:
        db = app.redis

    db.set(key, value)
