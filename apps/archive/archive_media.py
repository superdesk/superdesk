from flask import abort, current_app as app
from superdesk.media.media_operations import process_file_from_stream, decode_metadata
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.models import BaseModel
from superdesk.upload import url_for_media
from superdesk.utc import utcnow
from eve.utils import config
from .common import base_schema, item_url, update_dates_for, generate_guid, GUID_TAG, ARCHIVE_MEDIA, set_user
from .common import on_create_media_archive, on_update_media_archive, on_delete_media_archive
from apps.activity import add_activity
import logging

logger = logging.getLogger(__name__)


class ArchiveMediaModel(BaseModel):
    type_av = {'image': 'picture', 'audio': 'audio', 'video': 'video'}
    endpoint_name = ARCHIVE_MEDIA
    schema = {
        'media': {
            'type': 'file',
            'required': True
        },
        'upload_id': {'type': 'string'},
        'headline': base_schema['headline'],
        'byline': base_schema['byline'],
        'description_text': base_schema['description_text'],
        'creator': base_schema['creator']
    }
    datasource = {'source': 'archive'}
    resource_methods = ['POST']
    item_methods = ['PATCH', 'GET', 'DELETE']
    item_url = item_url

    def on_update(self, updates, original):
        on_update_media_archive()

    def on_delete(self, doc):
        on_delete_media_archive()

    def on_create(self, docs):
        ''' Create corresponding item on file upload '''
        for doc in docs:
            file, content_type, metadata = self.get_file_from_document(doc)
            inserted = [doc['media']]
            file_type = content_type.split('/')[0]

            try:
                update_dates_for(doc)
                doc['guid'] = generate_guid(type=GUID_TAG)
                doc.setdefault('_id', doc['guid'])
                doc['type'] = self.type_av.get(file_type)
                doc['version'] = 1
                doc['versioncreated'] = utcnow()
                rendition_spec = config.RENDITIONS['picture']
                renditions = generate_renditions(file, doc['media'], inserted, file_type,
                                                 content_type, rendition_spec, url_for_media)
                doc['renditions'] = renditions
                doc['mimetype'] = content_type
                doc['filemeta'] = metadata
                if not doc.get('_import', None):
                    doc['creator'] = set_user(doc)

                add_activity('uploaded media {{ name }}',
                             name=doc.get('headline', doc.get('mimetype')),
                             renditions=doc.get('renditions'))

            except Exception as io:
                logger.exception(io)
                for file_id in inserted:
                    delete_file_on_error(doc, file_id)
                abort(500)
        on_create_media_archive()

    def get_file_from_document(self, doc):
        file = doc.get('media_fetched')
        if file:
            del doc['media_fetched']
        else:
            content = doc['media']
            res = process_file_from_stream(content, filename=content.filename, content_type=content.mimetype)
            file_name, content_type, metadata = res
            logger.debug('Going to save media file with %s ' % file_name)
            content.seek(0)
            id = app.media.put(content, filename=file_name, content_type=content_type, metadata=metadata)
            doc['media'] = id
            return content, content_type, decode_metadata(metadata)
        return file, file.content_type, file.metadata
