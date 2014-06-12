'''
Created on May 29, 2014

@author: ioan
'''


from celery import Celery
from superdesk import settings


celery = Celery(__name__, broker=settings.CELERY_BROKER_URL)
TaskBase = celery.Task


class AppContextTask(TaskBase):
        abstract = True
        flask_app = None

        def __call__(self, *args, **kwargs):
            with self.flask_app.app_context():
                return super(AppContextTask, self).__call__(*args, **kwargs)

celery.Task = AppContextTask


def init_celery(app):
    celery.conf.update(app.config)
    celery.Task.flask_app = app
    app.celery = celery
