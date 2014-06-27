import superdesk
from .utc import utcnow
from .upload import url_for_media
from .media_operations import store_file_from_url
from datetime import datetime
from settings import SERVER_DOMAIN
from uuid import uuid4
from eve.utils import config
from flask import abort, request, Response
from werkzeug.exceptions import NotFound
from superdesk import SuperdeskError
from superdesk.media_operations import resize_image
from werkzeug.datastructures import FileStorage
from PIL import Image
from superdesk.notification import push_notification


bp = superdesk.Blueprint('archive_media', __name__)


GUID_TAG = 'tag'
GUID_NEWSML = 'newsml'


class InvalidFileType(SuperdeskError):
    """Exception raised when receiving a file type that is not supported."""

    def __init__(self, type=None):
        super().__init__('Invalid file type %s' % type, payload={})


def on_create_item(data, docs):
    """Make sure item has basic fields populated."""
    for doc in docs:
        update_dates_for(doc)

        if not doc.get('guid'):
            doc['guid'] = generate_guid(type=GUID_NEWSML)

        doc.setdefault('_id', doc['guid'])


def on_delete_archive(data, lookup):
    '''Delete associated binary files.'''
    res = data.find_one('archive', res=None, req=None, **lookup)
    if res and res.get('renditions'):
        for _name, ref in res['renditions'].items():
            try:
                superdesk.app.media.delete(ref['media'])
            except (KeyError, NotFound):
                pass


def generate_guid(**hints):
    '''Generate a GUID based on given hints'''
    newsml_guid_format = 'urn:newsml:%(domain)s:%(timestamp)s:%(identifier)s'
    tag_guid_format = 'tag:%(domain)s:%(year)d:%(identifier)s'

    if not hints.get('id'):
        hints['id'] = str(uuid4())

    t = datetime.today()

    if hints['type'].lower() == GUID_TAG:
        return tag_guid_format % {'domain': SERVER_DOMAIN, 'year': t.year, 'identifier': hints['id']}
    elif hints['type'].lower() == GUID_NEWSML:
        return newsml_guid_format % {'domain': SERVER_DOMAIN, 'timestamp': t.isoformat(), 'identifier': hints['id']}
    return None


@bp.route('/archive_media/import_media/', methods=['POST'])
def import_media_into_archive():
    archive_guid = request.form['media_archive_guid']
    media_url = request.form['href']

    if request.form.get('rendition_name'):
        rendition_name = request.form['rendition_name']
        rv = import_rendition(archive_guid, rendition_name, media_url)
    else:
        rv = import_media(archive_guid, media_url)
    return Response(rv)


def import_media(media_archive_guid, href):
    '''
    media_archive_guid: media_archive guid
    href: external file URL from which to download it
    Download from href and save file on app storage, process it and
    update "original" rendition for guid content item
    '''
    rv = import_rendition(media_archive_guid, 'baseImage', href)
    return rv


def import_rendition(media_archive_guid, rendition_name, href):
    '''
    media_archive_guid: media_archive guid
    rendition_name: rendition to update,
    href: external file URL from which to download it
    Download from href and save file on app storage, process it and
    update "rendition_name" rendition for guid content item
    '''
    archive = fetch_media_from_archive(media_archive_guid)
    if rendition_name not in archive['renditions']:
        payload = 'Invalid rendition name %s' % rendition_name
        raise superdesk.SuperdeskError(payload=payload)

    file_guid = store_file_from_url(href)
    updates = {}
    updates['renditions'] = {rendition_name: {'href': url_for_media(file_guid)}}
    rv = superdesk.app.data.update(ARCHIVE_MEDIA, id_=str(media_archive_guid), updates=updates)
    return rv


def fetch_media_from_archive(media_archive_guid):
    archive = superdesk.app.data.find_one(ARCHIVE_MEDIA, req=None, _id=str(media_archive_guid))
    if not archive:
        msg = 'No document found in the media archive with this ID: %s' % media_archive_guid
        raise superdesk.SuperdeskError(payload=msg)
    return archive


type_av = {'image': 'picture', 'audio': 'audio', 'video': 'video'}


def update_dates_for(doc):
    for item in ['firstcreated', 'versioncreated']:
        doc.setdefault(item, utcnow())


def on_upload_create(data, docs):
    ''' Create corresponding item on file upload '''
    for doc in docs:
        file = get_file_from_document(doc)
        inserted = [doc['media']]
        file_type = file.content_type.split('/')[0]

        try:
            update_dates_for(doc)
            doc['guid'] = generate_guid(type=GUID_TAG)
            doc['type'] = type_av.get(file_type)
            doc['version'] = 1
            doc['renditions'] = generate_renditions(file, doc['media'], inserted, file_type)
            doc['mimetype'] = file.content_type
            doc['filemeta'] = file.metadata
        except Exception as io:
            superdesk.logger.exception(io)
            for file_id in inserted:
                delete_file_on_error(doc, file_id)
            abort(500)


def get_file_from_document(doc):
    file = doc.get('media_fetched')
    if not file:
        file = superdesk.app.media.get(doc['media'])
    else:
        del doc['media_fetched']
    return file


def delete_file_on_error(doc, file_id):
    # Don't delete the file if we are on the import from storage flow
    if doc['_import']:
        return
    superdesk.app.media.delete(file_id)


def generate_renditions(original, media_id, inserted, file_type):
    """Generate system renditions for given media file id."""
    rend = {'href': url_for_media(media_id), 'media': media_id, 'mimetype': original.content_type}
    renditions = {'original': rend}

    if file_type != 'image':
        return renditions

    img = Image.open(original)
    width, height = img.size
    rend.update({'width': width})
    rend.update({'height': height})

    ext = original.content_type.split('/')[1].lower()
    ext = ext if ext in ('jpeg', 'gif', 'tiff', 'png') else 'png'
    for rendition, rsize in config.RENDITIONS['picture'].items():
        size = (rsize['width'], rsize['height'])
        original.seek(0)
        resized, width, height = resize_image(original, ext, size)
        resized = FileStorage(stream=resized, content_type='image/%s' % ext)
        id = superdesk.app.media.put(resized)
        inserted.append(id)
        renditions[rendition] = {'href': url_for_media(id), 'media': id,
                                 'mimetype': 'image/%s' % ext, 'width': width, 'height': height}
    return renditions


def on_upload_update(data, docs):
    for doc in docs:
        doc['version'] += 1


superdesk.connect('create:ingest', on_create_item)
superdesk.connect('create:archive', on_create_item)
superdesk.connect('create:archive_media', on_upload_create)
superdesk.connect('delete:archive', on_delete_archive)
superdesk.blueprint(bp)

base_schema = {
    'guid': {
        'type': 'string',
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
        'type': 'string'
    },
    'contents': {
        'type': 'list'
    },
    'media': {'type': 'media'}
}

ingest_schema = {
    'archived': {
        'type': 'datetime'
    }
}

archive_schema = {}

ingest_schema.update(base_schema)
archive_schema.update(base_schema)

item_url = 'regex("[\w,.:-]+")'

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

ARCHIVE_MEDIA = 'archive_media'
superdesk.domain(ARCHIVE_MEDIA, {
    'schema': {
        'media': {
            'type': 'media',
            'required': True
        },
        'upload_id': {'type': 'string'},
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

def on_create_media_archive(resource, docs):
    push_notification('media_archive', created=1)

superdesk.connect('create:ingest', on_create_media_archive)
superdesk.connect('create:archive', on_create_media_archive)
superdesk.connect('create:archive_media', on_create_media_archive)

def on_update_media_archive(resource, id, updates):
    push_notification('media_archive', updated=1)

superdesk.connect('update:ingest', on_update_media_archive)
superdesk.connect('update:archive', on_update_media_archive)
superdesk.connect('update:archive_media', on_update_media_archive)

def on_delete_media_archive(resource, lookup):
    push_notification('media_archive', deleted=1)

superdesk.connect('delete:ingest', on_delete_media_archive)
superdesk.connect('delete:archive', on_delete_media_archive)
superdesk.connect('delete:archive_media', on_delete_media_archive)
