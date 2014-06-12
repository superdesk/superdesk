'''
Created on May 29, 2014

@author: ioan
'''


from celery import Celery
from superdesk import settings


celery = Celery(__name__, broker=settings.CELERY_BROKER_URL)
TaskBase = celery.Task


def init_celery(app):
    celery.conf.update(app.config)

    class AppContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(AppContextTask, self).__call__(*args, **kwargs)

    celery.Task = AppContextTask
    app.celery = celery
