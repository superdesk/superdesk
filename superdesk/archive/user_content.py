
from superdesk.base_model import BaseModel
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
