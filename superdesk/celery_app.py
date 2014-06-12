'''
Created on May 29, 2014

@author: ioan
'''


from celery import Celery
from flask import current_app as app  # noqa
from superdesk import settings


celery = Celery(__name__, broker=settings.CELERY_BROKER_URL)


def init_celery(app):
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.test_request_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
