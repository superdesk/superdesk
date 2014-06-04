'''
Created on May 29, 2014

@author: ioan
'''

from __future__ import absolute_import
from celery import Celery
import __main__

celery = Celery('Superdesk', inport=['superdesk.archive_ingest'])
celery.config_from_object('settings')


if 'celery' in __main__.__file__:
    from app import get_app
    app = get_app()
    celery.conf.update(app.config)
# TODO: fix this Celery initialization on Eve
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.test_app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
