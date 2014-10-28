from apps.common.components.base_component import BaseComponent
from apps.legal_archive.tasks import archive_item, update_item
from apps.archive.archive_ingest import update_status
from celery import states


class LegalArchiveProxy(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'legal_archive_proxy'

    def create(self, items):
        for item in items:
            task = archive_item.delay(item)
            if task.state not in ('PROGRESS', states.SUCCESS, states.FAILURE) and not task.result:
                update_status(task.id, 0, 0)
        return [item.get('guid') for item in items]

    def update(self, item_id, updates):
        task = update_item.delay(item_id, updates)
        if task.state not in ('PROGRESS', states.SUCCESS, states.FAILURE) and not task.result:
            update_status(task.id, 0, 0)
