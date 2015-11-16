import logging
from yowsup.registration import WARegRequest

from superdesk.celery_app import celery
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.notification import push_notification
from superdesk import get_resource_service


logger = logging.getLogger('superdesk')
logger.setLevel(logging.INFO)


class WhatsAppRegistrationRequestService(BaseService):

    def on_created(self, docs):
        for doc in docs:
            registration_request.delay(doc)


class WhatsAppRegistrationRequestResource(Resource):
    schema = {
        'phone': {'type': 'integer'},
        'cc': {'type': 'integer'},
        'code': {'type': 'integer'},
    }
    privileges = {
        'GET': 'archive',
        'POST': 'archive',
        'DELETE': 'archive',
    }


@celery.task(name='whatsapp_registration_request')
def registration_request(model):
    code = model['code']
    code = code.replace('-', '')
    req = WARegRequest(model['cc'], model['phone'], code)
    result = req.send()

    push_notification(
        'whatsapp_registration_request',
        id=str(model['_id']),
        result=result
    )

    get_resource_service('whatsapp_registration_request').delete(
        lookup={'_id': model['_id']}
    )
