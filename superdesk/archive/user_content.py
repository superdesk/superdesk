
from superdesk.base_model import BaseModel

class UserContentModel(BaseModel):
    endpoint_name = 'user_content'
    url = 'users/<regex("[a-f0-9]{24}"):original_creator>/content'
    datasource = {'source': 'archive'}
    resource_methods = ['GET']
    item_methods = ['GET']
