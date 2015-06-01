from .chat_session import ChatResource, ChatService
from .messages import MessageResource, MessageService
from superdesk import get_backend, intrinsic_privilege
import logging


logger = logging.getLogger(__name__)


def init_app(app):
    endpoint_name = 'chat_session'
    service = ChatService(endpoint_name, backend=get_backend())
    ChatResource(endpoint_name, app=app, service=service)

    endpoint_name = 'chat_message'
    service = MessageService(endpoint_name, backend=get_backend())
    MessageResource(endpoint_name, app=app, service=service)

    intrinsic_privilege('chat_session', method=['POST', 'PATCH'])
    intrinsic_privilege('chat_message', method=['POST', 'PATCH', 'DELETE'])
