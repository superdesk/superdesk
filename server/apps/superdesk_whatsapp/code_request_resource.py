import logging
from yowsup.registration import WACodeRequest

from superdesk.celery_app import celery
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.notification import push_notification
from superdesk import get_resource_service


logger = logging.getLogger('superdesk')
logger.setLevel(logging.INFO)


class WhatsAppCodeRequestService(BaseService):

    def on_created(self, docs):
        for doc in docs:
            code_request.delay(doc)


class WhatsAppCodeRequestResource(Resource):
    schema = {
        'phone': {'type': 'string'},
        'cc': {'type': 'string'},
        'mcc': {'type': 'string'},
        'mnc': {'type': 'string'},
    }
    privileges = {
        'GET': 'archive',
        'POST': 'archive',
        'DELETE': 'archive',
    }


@celery.task(name='whatsapp_code_request')
def code_request(model):
    # codeReq = WACodeRequest(
        # model["cc"],
        # model["phone"],
        # model["mcc"],
        # model["mnc"],
        # model["mcc"],
        # model["mnc"],
        # "sms"
    # )
    # result = codeReq.send()

    result = {
        "length": 6,
        "retry_after": 10805,
        "status": b'sent',
        "method": b'sms',
    }

    push_notification(
        'whatsapp_code_request',
        id=str(model['_id']),
        result=result
    )

    get_resource_service('whatsapp_code_request').delete(
        lookup={'_id': model['_id']}
    )
