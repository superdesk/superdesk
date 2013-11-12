
import superdesk

def on_create_item(data, docs):
    for doc in docs:
        if 'guid' in doc:
            doc.setdefault('_id', doc['guid'])

superdesk.connect('create:ingest', on_create_item)
superdesk.connect('create:archive', on_create_item)

schema = {
    'guid': {
        'type': 'string'
    },
    'uri': {
        'type': 'string'
    },
    'version': {
        'type': 'integer'
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
    'description_text': {
        'type': 'string'
    },
    'firstcreated': {
        'type': 'datetime'
    },
    'versioncreated': {
        'type': 'datetime'
    },
    'type': {
        'type': 'string'
    },
    'provider': {
        'type': 'string'
    },
    'ingest_provider': {
        'type': 'string'
    },
    'urgency': {
        'type': 'integer'
    },
    'contents': {
        'type': 'list'
    },
    'groups': {
        'type': 'list'
    },
    'keywords': {
        'type': 'list'
    },
    'subject': {
        'type': 'list'
    },
    'body_html': {
        'type': 'string'
    },
    'renditions': {
        'type': 'dict'
    }
}

item_url = '[\w][\w,.:-]+'

extra_response_fields = ['guid', 'headline', 'firstcreated', 'versioncreated']

facets = {
    'provider': {'terms': {'field': 'provider'}},
    'urgency': {'terms': {'field': 'urgency'}},
    'subject': {'terms': {'field': 'subject.name'}},
    'versioncreated': {'date_histogram': {'field': 'versioncreated', 'interval': 'hour'}},
}

superdesk.domain('ingest', {
    'schema': schema,
    'extra_response_fields': extra_response_fields,
    'item_url': item_url,
    'datasource': {
        'backend': 'elastic',
        'facets': facets
    }
})

superdesk.domain('archive', {
    'schema': schema,
    'extra_response_fields': extra_response_fields,
    'item_url': item_url,
    'datasource': {
        'backend': 'elastic',
        'facets': facets
    }
})
