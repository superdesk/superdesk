import logging

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity


logger = logging.getLogger(__name__)


class CollectLayer(YowInterfaceLayer):

    def __init__(self, *args, results, **kwargs):
        self.results = results
        super().__init__()

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        phone = messageProtocolEntity.getFrom(False)
        result = {
            'from': phone,
        }
        logger.info("Received from %s" % (phone))

        reply_message = "Thank you for submitting your report!"

        result['timestamp'] = messageProtocolEntity.getTimestamp()
        if messageProtocolEntity.getType() == 'text':
            result['type'] = 'text'
            result['body'] = messageProtocolEntity.getBody()
        elif messageProtocolEntity.getType() == 'media':
            if messageProtocolEntity.getMediaType() == "image":
                result['type'] = 'image'
                result['body'] = messageProtocolEntity.getCaption()
                result['url'] = messageProtocolEntity.url
            else:
                result['type'] = 'media'
            # elif messageProtocolEntity.getMediaType() == "location":
                # print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(
                # ), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))
            # elif messageProtocolEntity.getMediaType() == "vcard":
                # print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(
                # ), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))

        self.results.append(result)

        if '@' in phone:
            recipient = phone
        elif '-' in phone:
            recipient = "%s@g.us" % phone
        else:
            recipient = "%s@s.whatsapp.net" % phone
        messageEntity = TextMessageProtocolEntity(reply_message, to=recipient)

        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))
        self.toLower(messageEntity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())


def get_wrapped_collect_layer(results_list):

    class WrappedCollectLayer(CollectLayer):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, results=results_list, **kwargs)

    return WrappedCollectLayer
