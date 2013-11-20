
import blinker


def connect(signal, subscriber):
    """Connect to signal"""
    blinker.signal(signal).connect(subscriber)


def send(signal, sender, **kwargs):
    """Send signal"""
    blinker.signal(signal).send(sender, **kwargs)


def proxy_resource_signal(action, app):
    def handle(resource, documents):
        send(action, app.data, docs=documents)
        send('%s:%s' % (action, resource), app.data, docs=documents)
    return handle


def proxy_item_signal(action, app):
    def handle(resource, id, document):
        send(action, app.data, resource=resource, docs=[document])
        send('%s:%s' % (action, resource), app.data, docs=[document])
    return handle
