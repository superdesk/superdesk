from apps.common.models.io.base_proxy import BaseProxy


class MongoProxy(BaseProxy):
    '''
    Data layer implementation used to connect the models to the Mongo data layer.
    Transforms the model data layer API into Eve data layer calls.
    '''
    def __init__(self, data_layer):
        self.data_layer = data_layer

    def create(self, resource, docs):
        return self.data_layer.insert(resource, docs)
