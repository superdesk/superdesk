'''
Created on May 29, 2014

@author: ioan
'''


import redis
from celery import Celery
from superdesk import settings


celery = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
TaskBase = celery.Task


class AppContextTask(TaskBase):
        abstract = True
        flask_app = None

        def __call__(self, *args, **kwargs):
            with self.flask_app.app_context():
                return super().__call__(*args, **kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            try:
                self.flask_app.sentry.captureException()
            except:
                pass


celery.Task = AppContextTask


def init_app(app):
    celery.conf.update(app.config)
    celery.Task.flask_app = app
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
