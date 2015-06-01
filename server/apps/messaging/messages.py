from superdesk import Resource, Service
from superdesk.errors import SuperdeskApiError


class MessageResource(Resource):
    schema = {
        'msg': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 500,
            'required': True,
        },
        'sender': Resource.rel('users', required=True),
        'chat_session': Resource.rel('chat_sessions', required=True)
    }

    resource_methods = ['GET', 'POST']
    datasource = {'default_sort': [('_created', -1)]}


class MessageService(Service):
    notification_key = '*/new_message'

    def on_create(self, docs):
        for doc in docs:
            sent_user = doc.get('sender', None)
            user = g.user
            if sent_user and sent_user != str(user.get('_id')):
                message = 'Sending a message on behalf of someone else is prohibited.'
                raise SuperdeskApiError.forbiddenError(message)
            doc['sender'] = str(user.get('_id'))

    def on_created(self, docs):
        for doc in docs:
            push_notification(self.notification_key, item=str(doc.get('item')))

    def on_updated(self, updates, original):
        push_notification(self.notification_key, updated=1)

    def on_deleted(self, doc):
        push_notification(self.notification_key, deleted=1)
