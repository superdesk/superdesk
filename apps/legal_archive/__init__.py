from apps.legal_archive.components.legal_archive import LegalArchive
from apps.common.components.utils import register_component
from apps.legal_archive.components.legal_archive_proxy import LegalArchiveProxy
from apps.common.models.utils import register_model
from apps.legal_archive.models.legal_archive import LegalArchiveModel
from apps.legal_archive.datalayer import LegalArchiveDataLayer
from apps.common.models.io.mongo_proxy import MongoProxy
from apps.legal_archive.resource import LegalArchiveService,\
    LegalArchiveResource, ErrorsResource
from apps.legal_archive.components.error import Error
from apps.legal_archive.models.errors import ErrorsModel
from superdesk.services import BaseService


def init_app(app):
    datalayer = LegalArchiveDataLayer(app)

    register_model(LegalArchiveModel(MongoProxy(datalayer)))
    register_component(LegalArchive(app))
    register_component(LegalArchiveProxy(app))

    endpoint_name = 'legal_archive'
    service = LegalArchiveService(endpoint_name, backend=None)
    LegalArchiveResource(endpoint_name, app=app, service=service)

    register_model(ErrorsModel(MongoProxy(datalayer)))
    register_component(Error(app))

    endpoint_name = 'errors'
    service = BaseService(endpoint_name, backend=None)
    ErrorsResource(endpoint_name, app=app, service=service)
