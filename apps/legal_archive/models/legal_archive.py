from apps.common.models.base_model import BaseModel
from apps.item_lock.models.item import ItemValidator


class LegalArchiveModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'legal_archive', data_layer, {}, ItemValidator())

    @classmethod
    def name(cls):
        return 'legal_archive'
