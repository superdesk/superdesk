import logging
import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from superdesk import SuperdeskError


logger = logging.getLogger(__name__)


class RuleSetsResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
            'minlength': 1
        },
        'rules': {
            'type': 'list'
        }
    }

    datasource = {
        'default_sort': [('name', 1)]
    }
    privileges = {'POST': 'rule_sets', 'DELETE': 'rule_sets', 'PATCH': 'rule_sets'}


class RuleSetsService(BaseService):

    def update(self, id, updates):
        """
        Overriding to set the value of "new" attribute of rules to empty string if it's None.
        """

        for rule in updates.get('rules', {}):
            if rule['new'] is None:
                rule['new'] = ''

        return super().update(id, updates)

    def on_delete(self, doc):
        if self.backend.find_one('ingest_providers', req=None, rule_set=doc['_id']):
            raise SuperdeskError('rule set is in use')


def init_app(app):
    endpoint_name = 'rule_sets'
    service = RuleSetsService(endpoint_name, backend=get_backend())
    RuleSetsResource(endpoint_name, app=app, service=service)


superdesk.privilege(name='rule_sets',
                    label='Transformation Rules Management',
                    description='User can setup transformation rules for ingest content.')
