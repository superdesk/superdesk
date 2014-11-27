from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.utc import utcnow
from flask import current_app as app
import logging


logger = logging.getLogger(__name__)


class VocabulariesResource(Resource):
    schema = {
        '_id': {
            'type': 'string',
            'required': True,
            'unique': True
        },
        'items': {
            'type': 'list',
            'required': True
        }
    }

    item_url = 'regex("[\w]+")'
    item_methods = ['GET']
    resource_methods = ['GET']


class VocabulariesService(BaseService):
    def on_replace(self, document, original):
        document[app.config['LAST_UPDATED']] = utcnow()
        document[app.config['DATE_CREATED']] = original[app.config['DATE_CREATED']] if original else utcnow()
        logger.info("updating vocabulary", document["_id"])
