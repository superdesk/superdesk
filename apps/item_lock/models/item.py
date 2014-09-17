from apps.common.models.base_model import Validator, BaseModel


class ItemValidator(Validator):
    def validate(self, doc):
        return True


class ItemModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'archive', data_layer, {}, ItemValidator())

    @classmethod
    def name(cls):
        return 'item_model'
