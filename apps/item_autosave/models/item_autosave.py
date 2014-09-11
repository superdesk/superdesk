from apps.common.models.base_model import BaseModel
from apps.item_lock.models.item import ItemValidator


class ItemAutosaveModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'archive_autosave', data_layer, {}, ItemValidator())

    @classmethod
    def name(cls):
        return 'item_autosave'
