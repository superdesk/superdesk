
import blinker


def connect(signal, subscriber):
    """Connect to signal"""
    blinker.signal(signal).connect(subscriber)


def send(signal, sender, **kwargs):
    """Send signal"""
    return blinker.signal(signal).send(sender, **kwargs)


def proxy_resource_signal(action, app):
    def handle(resource, documents):
        docs = documents
        if '_items' in documents:
            docs = documents['_items']
        send(action, app.data, docs=docs)
        send('%s:%s' % (action, resource), app.data, docs=docs)
    return handle


def proxy_item_signal(action, app):
    def handle(resource, document):
        send(action, app.data, resource=resource, docs=[document])
        send('%s:%s' % (action, resource), app.data, docs=[document])
    return handle
