from apps.legal_archive.components.legal_archive import LegalArchive
from apps.common.components.utils import register_component
from apps.legal_archive.components.legal_archive_proxy import LegalArchiveProxy
from apps.common.models.utils import register_model
from apps.legal_archive.models.legal_archive import LegalArchiveModel
from apps.legal_archive.datalayer import LegalArchiveDataLayer
from apps.legal_archive.resource import LegalArchiveService,\
    LegalArchiveResource, ErrorsResource
from apps.legal_archive.components.error import Error
from apps.legal_archive.models.errors import ErrorsModel
from superdesk.services import BaseService
from apps.common.models.io.eve_proxy import EveProxy


def init_app(app):
    datalayer = LegalArchiveDataLayer(app)

    register_model(LegalArchiveModel(EveProxy(datalayer)))
    register_component(LegalArchive(app))
    register_component(LegalArchiveProxy(app))

    endpoint_name = 'legal_archive'
    service = LegalArchiveService(endpoint_name, backend=datalayer)
    LegalArchiveResource(endpoint_name, app=app, service=service)

    register_model(ErrorsModel(EveProxy(datalayer)))
    register_component(Error(app))

    endpoint_name = 'errors'
    service = BaseService(endpoint_name, backend=datalayer)
    ErrorsResource(endpoint_name, app=app, service=service)
