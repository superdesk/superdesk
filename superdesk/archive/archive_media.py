import superdesk
from superdesk.utc import utcnow
from superdesk.upload import url_for_media
from flask import abort, current_app as app
from superdesk.media_operations import resize_image, process_file_from_stream, decode_metadata
from werkzeug.datastructures import FileStorage
from PIL import Image
from superdesk.base_model import BaseModel
from .common import base_schema, item_url, update_dates_for, generate_guid, GUID_TAG, ARCHIVE_MEDIA, set_user
from .common import on_create_media_archive, on_update_media_archive, on_delete_media_archive
from eve.utils import config
from bson.objectid import ObjectId
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
                doc['type'] = self.type_av.get(file_type)
                doc['version'] = 1
                doc['versioncreated'] = utcnow()
                doc['renditions'] = self.generate_renditions(file, doc['media'], inserted, file_type, content_type)
                doc['mimetype'] = content_type
                doc['filemeta'] = metadata
                doc['creator'] = set_user(doc)
            except Exception as io:
                superdesk.logger.exception(io)
                for file_id in inserted:
                    self.delete_file_on_error(doc, file_id)
                abort(500)
        on_create_media_archive()

    def get_file_from_document(self, doc):
        file = doc.get('media_fetched')
        if file:
            del doc['media_fetched']
        else:
            content = doc['media']
            res = process_file_from_stream(content, filename=content.filename, content_type=content.mimetype)
            file_name, out, content_type, metadata = res
            logger.debug('Going to save media file with %s ' % file_name)
            id = app.media.put(out, filename=file_name, content_type=content_type, metadata=metadata)
            doc['media'] = id
            return out, content_type, decode_metadata(metadata)
        return file, file.content_type, file.metadata

    def delete_file_on_error(self, doc, file_id):
        # Don't delete the file if we are on the import from storage flow
        if doc['_import']:
            return
        app.media.delete(file_id)

    def generate_renditions(self, original, media_id, inserted, file_type, content_type):
        """Generate system renditions for given media file id."""
        rend = {'href': url_for_media(media_id), 'media': media_id, 'mimetype': content_type}
        renditions = {'original': rend}

        if file_type != 'image':
            return renditions

        original.seek(0)
        img = Image.open(original)
        width, height = img.size
        rend.update({'width': width})
        rend.update({'height': height})

        ext = content_type.split('/')[1].lower()
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


class AuthorItemModel(BaseModel):
    endpoint_name = 'user_items'
    url = 'users/<regex("[a-f0-9]{24}"):user_id>/archive'
    schema = base_schema
    datasource = {'source': 'archive'}
    resource_methods = ['GET']

    def get(self, req, lookup):
        if lookup.get('user_id'):
            lookup["author.user"] = ObjectId(lookup['user_id'])
            del lookup['user_id']
        return super().get(req, lookup)
