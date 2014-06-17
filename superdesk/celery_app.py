'''
Created on May 29, 2014

@author: ioan
'''


from celery import Celery
from superdesk import settings
import redis


celery = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
TaskBase = celery.Task


class AppContextTask(TaskBase):
        abstract = True
        flask_app = None

        def __call__(self, *args, **kwargs):
            with self.flask_app.test_request_context():
                return super(AppContextTask, self).__call__(*args, **kwargs)

celery.Task = AppContextTask


def init_celery(app):
    celery.conf.update(app.config)
    celery.Task.flask_app = app
    app.celery = celery


def add_subtask_to_progress(task_id):
    return _update_subtask_progress(task_id, total=True)


def finish_subtask_from_progress(task_id):
    return _update_subtask_progress(task_id, current=True)


def finish_task_for_progress(task_id):
    return _update_subtask_progress(task_id, delete=True)


def _update_subtask_progress(task_id, current=None, total=None, delete=None):
    redis_db = redis.from_url(celery.conf['CELERY_RESULT_BACKEND'])

    current_key = 'current_%s' % task_id
    total_key = 'total_%s' % task_id

    if current:
        crt_current = redis_db.incr(current_key)
    else:
        crt_current = redis_db.get(current_key)

    if total:
        crt_total = redis_db.incr(total_key)
    else:
        crt_total = redis_db.get(total_key)

    if delete:
        redis_db.delete(current_key)
        redis_db.delete(crt_total)
        crt_current = crt_total

    return task_id, crt_current, crt_total
