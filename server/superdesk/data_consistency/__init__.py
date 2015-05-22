# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import logging

from superdesk.data_consistency.consistency_record import ConsistencyRecordResource, \
    ConsistencyRecordService
from superdesk.data_consistency.compare_repositories import CompareRepositories  # noqa
from superdesk.celery_app import celery
from superdesk import get_backend
from settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_URL
from superdesk.celery_task_utils import is_task_running, mark_task_as_not_running

logger = logging.getLogger(__name__)


def init_app(app):

    endpoint_name = 'consistency'
    service = ConsistencyRecordService(endpoint_name, backend=get_backend())
    ConsistencyRecordResource(endpoint_name, app=app, service=service)


@celery.task
def compare_repos():

    kwargs_ingest = {'resource': 'ingest'}
    kwargs_archive = {'resource': 'archive'}
    kwargs_published = {'resource': 'published'}
    kwargs_text_archive = {'resource': 'text_archive'}

    compare_repo.apply_async(kwargs=kwargs_ingest)
    compare_repo.apply_async(kwargs=kwargs_archive)
    compare_repo.apply_async(kwargs=kwargs_published)
    compare_repo.apply_async(kwargs=kwargs_text_archive)


@celery.task(soft_time_limit=600)
def compare_repo(resource):
    if is_task_running(name=resource, id=1, update_schedule={'seconds': 600}):
        return

    try:
        CompareRepositories().run(resource, ELASTICSEARCH_URL, ELASTICSEARCH_INDEX)
    finally:
        mark_task_as_not_running(name=resource, id=1)

# must be imported for registration
import superdesk.data_consistency.compare_repositories  # NOQA
import superdesk.data_consistency.consistency_record  # NOQA
