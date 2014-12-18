from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.io import allowed_providers
from superdesk.activity import ACTIVITY_CREATE, ACTIVITY_EVENT, \
    ACTIVITY_DELETE, ACTIVITY_UPDATE, notify_and_add_activity
from superdesk import get_resource_service


DAYS_TO_KEEP = 2


class IngestProviderResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'type': {
            'type': 'string',
            'required': True,
            'allowed': allowed_providers
        },
        'days_to_keep': {
            'type': 'integer',
            'required': True,
            'default': DAYS_TO_KEEP
        },
        'config': {
            'type': 'dict'
        },
        'ingested_count': {
            'type': 'integer'
        },
        'accepted_count': {
            'type': 'integer'
        },
        'token': {
            'type': 'dict'
        },
        'source': {
            'type': 'string',
            'required': True,
        },
        'is_closed': {
            'type': 'boolean',
            'default': False
        },
        'update_schedule': {
            'type': 'dict',
            'schema': {
                'hours': {'type': 'integer'},
                'minutes': {'type': 'integer', 'default': 5},
                'seconds': {'type': 'integer'},
            }
        },
        'last_updated': {'type': 'datetime'},
        'rule_set': Resource.rel('rule_sets', nullable=True)
    }

    privileges = {'POST': 'ingest_providers', 'PATCH': 'ingest_providers', 'DELETE': 'ingest_providers'}


class IngestProviderService(BaseService):

    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource=datasource, backend=backend)
        self.user_service = get_resource_service('users')

    def on_created(self, docs):
        for doc in docs:
            notify_and_add_activity(ACTIVITY_CREATE, 'created Ingest Channel {{name}}', item=doc,
                                    user_list=self.user_service.get_users_by_user_type('administrator'),
                                    name=doc.get('name'))

    def on_updated(self, updates, original):
        if 'is_closed' not in updates:
            notify_and_add_activity(ACTIVITY_UPDATE, 'updated Ingest Channel {{name}}', item=original,
                                    user_list=self.user_service.get_users_by_user_type('administrator'),
                                    name=updates.get('name', original.get('name')))

        if updates.get('is_closed') and updates.get('is_closed') != original.get('is_closed'):
            notify_and_add_activity(ACTIVITY_EVENT, '{{status}} Ingest Channel {{name}}', item=original,
                                    user_list=self.user_service.get_users_by_user_type('administrator'),
                                    name=updates.get('name', original.get('name')),
                                    status='closed' if updates.get('is_closed') else 'opened')

    def on_deleted(self, doc):
        notify_and_add_activity(ACTIVITY_DELETE, 'deleted Ingest Channel {{name}}', item=doc,
                                user_list=self.user_service.get_users_by_user_type('administrator'),
                                name=doc.get('name'))
