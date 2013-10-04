
import superdesk
import superdesk.tokens

def on_create_items(db, docs):
    """Make sure there is only single instance for any guid."""
    for doc in docs:
        old = db.find_one('items', guid=doc.get('guid'))
        if old:
            db.remove('items', old.get('_id'))

        if doc.get('firstCreated'):
            doc.setdefault('created', doc.get('firstCreated'))

        if doc.get('versionCreated'):
            doc.setdefault('updated', doc.get('versionCreated'))

def on_read_items(db, docs):
    for doc in docs:
        for content in doc.get('contents', []):
            if content.get('href'):
                content['href'] = '%s?auth_token=%s' % (content.get('href'), superdesk.tokens.get_token(db))

superdesk.connect('read:items', on_read_items)
superdesk.connect('create:items', on_create_items)

schema = {
    'guid': {
        'type': 'string'
    },
    'version': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'slugline': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    'copyrightHolder': {
        'type': 'string'
    },
    'description': {
        'type': 'string'
    },
    'firstCreated': {
        'type': 'datetime'
    },
    'versionCreated': {
        'type': 'datetime'
    },
    'itemClass': {
        'type': 'string'
    },
    'provider': {
        'type': 'string'
    },
    'urgency': {
        'type': 'int'
    },
    'contents': {
        'type': 'list'
    },
    'groups': {
        'type': 'list'
    }
}

superdesk.domain('items', {
    'item_title': 'newsItem',
    'additional_lookup': {
        'url': '[a-zA-Z0-9,.:-]+',
        'field': 'guid'
    },
    'schema': schema,
    'extra_response_fields': ['headline', 'guid']
})
