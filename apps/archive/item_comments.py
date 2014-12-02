import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.comments import CommentsService, CommentsResource, comments_schema


comments_schema = dict(comments_schema)
comments_schema.update({'item': Resource.rel('archive', True, True, type='string')})


class ItemCommentsResource(CommentsResource):
    schema = comments_schema
    resource_methods = ['GET', 'POST', 'DELETE']
    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'archive', 'DELETE': 'archive'}


class ItemCommentsService(CommentsService):
    notification_key = 'item:comment'


class ItemCommentsSubResource(Resource):
    url = 'archive/<path:item>/comments'
    schema = comments_schema
    datasource = {'source': 'item_comments'}
    resource_methods = ['GET']


class ItemCommentsSubService(BaseService):

    def check_item_valid(self, item_id):
        item = superdesk.get_resource_service('archive').find_one(req=None, _id=item_id)
        if not item:
            msg = 'Invalid content item ID provided: %s' % item_id
            raise superdesk.SuperdeskError(payload=msg)

    def get(self, req, lookup):
        self.check_item_valid(lookup.get('item'))
        return super().get(req, lookup)
