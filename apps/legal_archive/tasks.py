from superdesk.celery_app import celery
from apps.common.components.utils import get_component
from apps.legal_archive.components.legal_archive import LegalArchive


@celery.task(bind=True, max_retries=3)
def archive_item(self, item, task_id=None):
    get_component(LegalArchive).create(item)


@celery.task(bind=True, max_retries=3)
def update_item(self, item_id, updates, task_id=None):
    get_component(LegalArchive).update(item_id, updates)
