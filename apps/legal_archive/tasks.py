from superdesk.celery_app import celery
from apps.common.components.utils import get_component
from apps.legal_archive.components.legal_archive import LegalArchive


@celery.task(bind=True, max_retries=3)
def archive_item(self, items, task_id=None):
    return get_component(LegalArchive).create(items)


@celery.task(bind=True, max_retries=3)
def update_item(self, original, updates, task_id=None):
    return get_component(LegalArchive).update(original, updates)
