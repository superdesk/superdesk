from apps.common.models.base_model import BaseModel, Validator


class ErrorsValidator(Validator):
    def validate(self, doc):
        return True


class ErrorsModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'errors', data_layer, {}, ErrorsValidator())

    @classmethod
    def name(cls):
        return 'errors'
