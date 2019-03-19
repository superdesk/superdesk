import re


def handle_item_update(sender, item, **kwargs):
    headline = item.get('headline')
    if headline:
        version = item.get('rewrite_sequence', 1) + 1
        headline = re.sub(r' \([0-9]+\)$', '', headline)
        headline = '{} ({})'.format(headline, version)
        item['headline'] = headline
        if item.get('fields_meta', {}).get('headline'):
            item['fields_meta']['headline'] = None


def init_app(app):
    try:
        from superdesk.signals import item_rewrite
        item_rewrite.connect(handle_item_update)
    except ImportError:
        pass  # old core version
