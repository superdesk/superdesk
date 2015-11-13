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
        'phone': {'type': 'string'},
        'cc': {'type': 'string'},
        'code': {'type': 'string'},
    }
    privileges = {
        'GET': 'archive',
        'POST': 'archive',
        'DELETE': 'archive',
    }


@celery.task(name='whatsapp_registration_request')
def registration_request(model):
    # code = model['code']
    # code = code.replace('-', '')
    # req = WARegRequest(model['cc'], model['phone'], code)
    # result = req.send()

    result = {
        "login": b'491771781387',
        "currency": b'EUR',
        "price_expiration": 1449174519,
        "price": b'0,89 \xe2\x82\xac',
        "type": b'new',
        "status": b'ok',
        "kind": b'free',
        "pw": b'm52HvXhrwyuNllcCUjRDyZDuVIw=',
        "expiration": 1477675534,
        "cost": b'0.89',
    }

    push_notification(
        'whatsapp_registration_request',
        id=str(model['_id']),
        result=result
    )

    get_resource_service('whatsapp_registration_request').delete(
        lookup={'_id': model['_id']}
    )
