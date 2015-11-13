from time import time
import logging

from yowsup.stacks import YowStack
from .layer import get_wrapped_collect_layer
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import YowCryptLayer, YowAuthenticationProtocolLayer, AuthError
from yowsup.layers.coder import YowCoderLayer
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_messages import YowMessagesProtocolLayer
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.stanzaregulator import YowStanzaRegulator
from yowsup.layers.protocol_receipts import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks import YowAckProtocolLayer
from yowsup.layers.logger import YowLoggerLayer
from yowsup.layers.protocol_iq import YowIqProtocolLayer
from yowsup.layers.protocol_calls import YowCallsProtocolLayer
from yowsup.common import YowConstants
from yowsup import env
from yowsup.layers.axolotl import YowAxolotlLayer


MAX_TIMEOUT = 10  # seconds
MAX_TASK_TIME = 120


logger = logging.getLogger(__name__)


class YowsupCollectStack(object):

    def __init__(self, credentials, results):
        """
        @tparam credentials tuple (phone, pass)
        @tparam results list []
        """

        self.results = results
        WrappedCollectLayer = get_wrapped_collect_layer(self.results)
        layers = (
            WrappedCollectLayer,
            (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer,
             YowAckProtocolLayer, YowMediaProtocolLayer, YowIqProtocolLayer, YowCallsProtocolLayer),
            YowAxolotlLayer,
            YowLoggerLayer,
            YowCoderLayer,
            YowCryptLayer,
            YowStanzaRegulator,
            YowNetworkLayer
        )
        self.stack = YowStack(layers)
        self.stack.setCredentials(credentials)

    def start(self):

        start_time = last_activity_time = time()
        previous_list_length = 0

        self.stack.broadcastEvent(YowLayerEvent(
            YowNetworkLayer.EVENT_STATE_CONNECT
        ))

        while (
            (time() - start_time) < MAX_TASK_TIME
        ) and (
            (time() - last_activity_time) < MAX_TIMEOUT
        ):
            previous_list_length = len(self.results)
            try:
                self.stack.loop(count=1, timeout=MAX_TIMEOUT)
            except AuthError as e:
                logger.critical("Authentication Error: %s" % e.message)
            if previous_list_length != len(self.results):
                last_activity_time = time()
