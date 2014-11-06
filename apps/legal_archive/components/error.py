from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.legal_archive.models.errors import ErrorsModel


class Error(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'error'

    def create(self, resource, docs, error):
        error = {'resource': resource, 'docs': docs, 'error': error}
        get_model(ErrorsModel).create(error)
