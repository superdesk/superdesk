import flask
import superdesk
from .utc import utcnow
from .upload import get_media_url
from datetime import datetime
from settings import SERVER_DOMAIN
from uuid import uuid4
from eve.methods.post import post
from eve.methods.delete import deleteitem
from eve.utils import config
from flask import abort
from werkzeug.exceptions import NotFound


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
            ingest_doc = data.find_one('ingest', guid=doc.get('guid'))
            if ingest_doc:
                doc.update(ingest_doc)
                data.update('ingest', ingest_doc.get('_id'), {'archived': utcnow()})
                del doc['_id']  # use all data from ingest but id
            archive_assets(data, doc)

        # set who created the item
        doc.setdefault('user', str(getattr(flask.g, 'user', {}).get('_id')))


def on_delete_archive(data, lookup):
    '''Delete associated binary files.'''
    res = data.find_one('archive', res=None, **lookup)
    if res:
        try:
            deleteitem('upload', {'_id': str(res['media_file'])})
        except NotFound:
            pass


def generate_guid(hints):
    '''Generate a GUID based on given hints'''
    newsml_guid_format = 'urn:newsml:%(domain)s:%(timestamp)s:%(identifier)s'
    tag_guid_format = 'tag:%(domain)s:%(year)d:%(identifier)s'

    assert isinstance(hints, dict)
    t = datetime.today()
    if hints['type'].lower() == 'tag':
        return tag_guid_format % {'domain': SERVER_DOMAIN, 'year': t.year, 'identifier': hints['id']}
    elif hints['type'].lower() == 'newsml':
        return newsml_guid_format % {'domain': SERVER_DOMAIN, 'timestamp': t.isoformat(), 'identifier': hints['id']}
    return None


def on_upload_create(data, docs):
    ''' Create corresponding item on file upload '''
    for doc in docs:
        res, _u, _e, code = post('upload')
        if code != 201:
            abort(500)
        res = superdesk.app.data.find_one('upload', req=None, _id=str(res['_id']))
        if not res:
            abort(500)
        type = res['mime_type'].split('/')[0]
        if type != 'image':
            deleteitem('upload', {'_id': str(res['_id'])})
            abort(400, 'Invalid file type: %s' % type)

        doc['media_file'] = str(res['_id'])
        doc['guid'] = generate_guid({'type': 'tag', 'id': str(uuid4())})
        doc['type'] = 'picture'
        doc['version'] = 1
        doc['versioncreated'] = utcnow()
        doc['renditions'] = generate_renditions(doc['media'])


def generate_renditions(media_id):
    """Generate system renditions for given media file id.

    This is just a mock implementation for ui..
    """
    url = get_media_url(media_id)
    renditions = {}
    for rendition in config.RENDITIONS['picture']:
        renditions[rendition] = {'href': url}
    return renditions


def on_upload_update(data, docs):
    for doc in docs:
        doc['version'] += 1


superdesk.connect('create:ingest', on_create_item)
superdesk.connect('create:archive', on_create_item)
superdesk.connect('create:archive_ingest', on_create_archive)
superdesk.connect('create:archive', on_create_archive)
superdesk.connect('create:archive_media', on_upload_create)
superdesk.connect('delete:archive', on_delete_archive)

base_schema = {
    'uri': {
        'type': 'string',
        'required': True,
        'unique': True
    },
    'guid': {
        'type': 'string',
        'required': True,
        'unique': True
    },
    'provider': {
        'type': 'string'
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
    'media_file': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'upload',
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
    },
    'resource_methods': ['GET', 'POST', 'DELETE']
})

superdesk.domain('archive_media', {
    'schema': {
        'media': {
            'type': 'media',
            'required': True
        },
        'headline': base_schema['headline'],
        'byline': base_schema['byline'],
        'description_text': base_schema['description_text']
    },
    'datasource': {
        'source': 'archive'
    },
    'resource_methods': ['POST'],
    'item_methods': ['PATCH', 'GET', 'DELETE'],
    'item_url': item_url
})

superdesk.domain('archive_ingest', {
    'schema': {
        'guid': {'type': 'string', 'required': True}
    },
    'datasource': {
        'source': 'archive'
    },
    'resource_methods': ['POST'],
    'item_methods': []
})
