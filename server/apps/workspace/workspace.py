
import superdesk
from flask import request


class WorkspaceResource(superdesk.Resource):

    schema = {
        'name': {'type': 'string', 'unique_to_user': True},
        'widgets': {'type': 'list'},
        'desk': superdesk.Resource.rel('desks'),
        'user': superdesk.Resource.rel('users'),
    }


class WorkspaceService(superdesk.Service):

    def is_authorized(self, **kwargs):
        if kwargs.get('_id'):
            data = self.find_one(req=None, _id=kwargs.get('_id')) or request.get_json()
        else:
            data = request.get_json()
        # TODO(petr): use privileges to test who can save desk/role dashboard
        return 'user' not in data or str(data['user']) == str(kwargs['user_id'])
