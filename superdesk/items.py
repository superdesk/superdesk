
import flask
import superdesk
from .utc import utcnow


def on_create_item(data, docs):
    for doc in docs:
        if 'guid' in doc:
            doc.setdefault('_id', doc['guid'])


def on_create_archive(data, docs):
    for doc in docs:
        if doc.get('guid'):
            # set archived on ingest item
            doc['archived'] = utcnow()
            ingest_doc = data.find_one('ingest', _id=doc.get('guid'))
            if ingest_doc:
                data.update('ingest', ingest_doc.get('_id'), {
                    'archived': doc['archived']
                })

        # set who created the item
        doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))

superdesk.connect('create:ingest', on_create_item)
superdesk.connect('create:archive', on_create_item)
superdesk.connect('create:archive', on_create_archive)

schema = {
    'uri': {
        'type': 'string',
        'required': True
    },
    'provider': {
        'type': 'string'
    },
    'guid': {
        'type': 'string',
        'required': True
    },
    'type': {
        'type': 'string'
    },
    'version': {
        'type': 'string'
    },
    'versioncreated': {
        'type': 'datetime'
    },
    'pubstatus': {
        'type': 'string'
    },
    'copyrightholder': {
        'type': 'string'
    },
    'copyrightnotice': {
        'type': 'string'
    },
    'language': {
        'type': 'string'
    },
    'place': {
        'type': 'list'
    },
    'subject': {
        'type': 'list'
    },
    'byline': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'located': {
        'type': 'string'
    },
    'renditions': {
        'type': 'dict'
    },
    'slugline': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    'description_text': {
        'type': 'string'
    },
    'firstcreated': {
        'type': 'datetime'
    },
    'ingest_provider': {
        'type': 'string'
    },
    'urgency': {
        'type': 'integer'
    },
    'groups': {
        'type': 'list'
    },
    'keywords': {
        'type': 'list'
    },
    'body_html': {
        'type': 'string'
    },
    'archived': {
        'type': 'datetime'
    },
    'user': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'users',
            'field': '_id',
            'embeddable': True
        }
    },
    'contents': {
        'type': 'list'
    },
}

item_url = 'regex("[\w][\w,.:-]+")'

extra_response_fields = ['guid', 'headline', 'firstcreated', 'versioncreated', 'archived']

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
