import logging
import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend


logger = logging.getLogger(__name__)


class RuleSetsResource(Resource):
    schema = {
        'name': {
            'type': 'string',
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
    pass


def init_app(app):
    endpoint_name = 'rule_sets'
    service = RuleSetsService(endpoint_name, backend=get_backend())
    RuleSetsResource(endpoint_name, app=app, service=service)


superdesk.privilege(name='rule_sets',
                    label='String Replace Rule Management',
                    description='User can setup string replace rules for ingest content.')