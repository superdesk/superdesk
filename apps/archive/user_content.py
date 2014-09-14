
from superdesk.models import BaseModel, build_custom_hateoas
from superdesk.services import BaseService
from .archive import ArchiveModel


class UserContentModel(BaseModel):
    endpoint_name = 'user_content'
    item_url = ArchiveModel.item_url
    url = 'users/<regex("[a-f0-9]{24}"):original_creator>/content'
    schema = ArchiveModel.schema
    datasource = {'source': 'archive'}
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE']
    resource_title = endpoint_name


class UserContentService(BaseService):
    custom_hateoas = {'self': {'title': 'Archive', 'href': '/archive/{_id}'}}

    def get(self, req, lookup):
        docs = super().get(req, lookup)
        for doc in docs:
            build_custom_hateoas(self.custom_hateoas, doc)
        return docs
