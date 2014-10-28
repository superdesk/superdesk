from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.legal_archive.models.legal_archive import LegalArchiveModel
from apps.common.components.utils import get_component
from apps.legal_archive.components.error import Error


class LegalArchive(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'legal_archive'

    def create(self, items):
        try:
            return get_model(LegalArchiveModel).create(items)
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), items, str(e))

    def update(self, item_id, updates):
        try:
            return get_model(LegalArchiveModel).update({'_id': item_id}, updates)
        except Exception as e:
            get_component(Error).create(LegalArchiveModel.name(), [updates], str(e))
