import logging

from flask import abort, current_app as app
from eve.utils import config
from apps.archive import ArchiveVersionsResource

from superdesk.media.media_operations import process_file_from_stream, decode_metadata
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.resource import Resource
from superdesk.upload import url_for_media
from superdesk.utc import utcnow
from .common import item_url, update_dates_for, generate_guid, GUID_TAG, ARCHIVE_MEDIA, set_original_creator, \
    generate_unique_id_and_name
from .common import on_create_media_archive, on_update_media_archive, on_delete_media_archive
from superdesk.activity import add_activity
from apps.content import metadata_schema
from superdesk.services import BaseService
from .archive import SOURCE as ARCHIVE


logger = logging.getLogger(__name__)


class ArchiveMediaVersionsResource(ArchiveVersionsResource):
    """
    Resource class for versions of archive_media
    """

    datasource = {'source': ARCHIVE + '_versions'}


class ArchiveMediaResource(Resource):
    endpoint_name = ARCHIVE_MEDIA
    schema = {
        'upload_id': {'type': 'string'},
        'task': {'type': 'dict'},
    }

    schema.update(metadata_schema)

    datasource = {'source': ARCHIVE}

    resource_methods = ['POST']
    item_methods = ['PATCH', 'GET', 'DELETE']
    item_url = item_url
    versioning = True
    privileges = {'POST': 'archive', 'PATCH': 'archive', 'DELETE': 'archive'}


class ArchiveMediaService(BaseService):

    type_av = {'image': 'picture', 'audio': 'audio', 'video': 'video'}

    def on_update(self, updates, original):
        on_update_media_archive()

    def on_delete(self, doc):
        on_delete_media_archive()

    def on_create(self, docs):
        """ Create corresponding item on file upload """

        for doc in docs:
            if 'media' not in doc or doc['media'] is None:
                abort(400, description="No media found")

            file, content_type, metadata = self.get_file_from_document(doc)
            inserted = [doc['media']]
            file_type = content_type.split('/')[0]

            try:
                update_dates_for(doc)
                generate_unique_id_and_name(doc)
                doc['guid'] = generate_guid(type=GUID_TAG)
                doc.setdefault('_id', doc['guid'])

                doc['type'] = self.type_av.get(file_type)
                doc[config.VERSION] = 1
                doc['versioncreated'] = utcnow()

                rendition_spec = config.RENDITIONS['picture']
                renditions = generate_renditions(file, doc['media'], inserted, file_type,
                                                 content_type, rendition_spec, url_for_media)
                doc['renditions'] = renditions
                doc['mimetype'] = content_type
                doc['filemeta'] = metadata

                if not doc.get('_import', None):
                    set_original_creator(doc)

                add_activity('upload', 'uploaded media {{ name }}', item=doc,
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
            doc['media'] = app.media.put(content, filename=file_name, content_type=content_type, metadata=metadata)
            return content, content_type, decode_metadata(metadata)

        return file, file.content_type, file.metadata
