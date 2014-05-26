
import flask
import superdesk
from .utc import utcnow


def archive_assets(data, doc):
    """Archive all related assets for given doc."""
    for group in doc.get('groups', []):
        for ref in group.get('refs', []):
            if 'residRef' in ref:
                item = data.find_one('ingest', _id=ref['residRef'])
                if item:
                    data.insert('archive', [item])


def on_create_item(data, docs):
    """Set guid as doc _id."""
    for doc in docs:
        if 'guid' in doc:
            doc.setdefault('_id', doc['guid'])


def on_create_archive(data, docs):
    """Set user and archived properties."""
    for doc in docs:
        if doc.get('guid'):
            # set archived on ingest item
            doc['archived'] = utcnow()
            ingest_doc = data.find_one('ingest', _id=doc.get('guid'))
            if ingest_doc:
                data.update('ingest', ingest_doc.get('_id'), {
                    'archived': doc['archived']
                })

            archive_assets(data, doc)

        # set who created the item
        doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))

superdesk.connect('create:ingest', on_create_item)
superdesk.connect('create:archive', on_create_item)
superdesk.connect('create:archive', on_create_archive)

base_schema = {
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
        'type': 'string',
        'required': True
    },
    'mimetype': {
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
    'usageterms': {
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
        'type': 'string',
        'nullable': True
    },
    'firstcreated': {
        'type': 'datetime'
    },
    'filemeta': {
        'type': 'dict'
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

ingest_schema = {
    'archived': {
        'type': 'datetime'
    }
}

archive_schema = {}

ingest_schema.update(base_schema)
archive_schema.update(base_schema)

item_url = 'regex("[\w][\w,.:-]+")'

extra_response_fields = ['guid', 'headline', 'firstcreated', 'versioncreated', 'archived']

facets = {
    'type': {'terms': {'field': 'type'}},
    'provider': {'terms': {'field': 'provider'}},
    'urgency': {'terms': {'field': 'urgency'}},
    'subject': {'terms': {'field': 'subject.name'}},
    'place': {'terms': {'field': 'place.name'}},
    'versioncreated': {'date_histogram': {'field': 'versioncreated', 'interval': 'hour'}},
}

superdesk.domain('ingest', {
    'schema': ingest_schema,
    'extra_response_fields': extra_response_fields,
    'item_url': item_url,
    'datasource': {
        'backend': 'elastic',
        'facets': facets
    }
})

superdesk.domain('archive', {
    'schema': archive_schema,
    'extra_response_fields': extra_response_fields,
    'item_url': item_url,
    'datasource': {
        'backend': 'elastic',
        'facets': facets
    }
})
