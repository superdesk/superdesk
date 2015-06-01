from superdesk import Resource, Service
from superdesk.errors import SuperdeskApiError
from flask import g


class ChatResource(Resource):
    schema = {
        'creator': Resource.rel('users', required=False),
        'users': {'type': 'list', 'schema': Resource.rel('users', required=True)},
        'desks': {'type': 'list', 'schema': Resource.rel('desks', required=True)},
        'groups': {'type': 'list', 'schema': Resource.rel('groups', required=True)}
    }
    resource_methods = ['GET', 'POST']
    datasource = {'default_sort': [('_created', -1)]}


class ChatService(Service):

    def on_create(self, docs):
        for doc in docs:
            sent_user = doc.get('creator', None)
            user = g.user
            if sent_user and sent_user != str(user.get('_id')):
                message = 'Creating a chat session on behalf of someone else is prohibited.'
                raise SuperdeskApiError.forbiddenError(message)
            creator = str(user.get('_id'))
            doc['creator'] = creator
