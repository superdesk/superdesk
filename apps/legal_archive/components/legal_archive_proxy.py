from apps.common.components.base_component import BaseComponent
from apps.legal_archive.tasks import update_legal_archive


class LegalArchiveProxy(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'legal_archive_proxy'

    def create(self, items):
        return update_legal_archive.delay([item['_id'] for item in items])

    def update(self, original, updates):
        return update_legal_archive.delay([original['_id']])
