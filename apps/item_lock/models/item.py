from .base_model import BaseModel, Validator


class ItemValidator(Validator):
    def validate(self, doc):
        return True


class ItemModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'archive', data_layer, {}, ItemValidator())
