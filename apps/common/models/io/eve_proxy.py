from apps.common.models.io.base_proxy import BaseProxy
from eve.utils import ParsedRequest


class EveProxy(BaseProxy):
    '''
    Data layer implementation used to connect the models to the Eve data layer.
    Transforms the model data layer API into Eve data layer calls.
    '''
    def __init__(self, data_layer):
        self.data_layer = data_layer

    def find(self, resource, filter, projection, **options):
        req = ParsedRequest()
        req.args = {}
        req.projection = projection
        return self.data_layer.get(resource, req, filter)
