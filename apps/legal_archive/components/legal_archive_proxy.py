from apps.common.components.base_component import BaseComponent
from apps.legal_archive.tasks import archive_item, update_item


class LegalArchiveProxy(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'legal_archive_proxy'

    def create(self, items):
        return archive_item.delay(items)

    def update(self, original, updates):
        return update_item.delay(original, updates)
