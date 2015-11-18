# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging

from flask import abort, current_app as app
from eve.utils import config
from apps.archive.common import copy_metadata_from_user_preferences
from settings import DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES
from superdesk.media.media_operations import process_file_from_stream, decode_metadata
from superdesk.media.renditions import generate_renditions, delete_file_on_error
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE, ITEM_TYPE, CONTENT_TYPE
from superdesk.upload import url_for_media
from .common import update_dates_for, generate_guid, GUID_TAG, set_original_creator, \
    generate_unique_id_and_name, set_item_expiry
from superdesk.activity import add_activity


logger = logging.getLogger(__name__)


class ArchiveMediaService():

    type_av = {'image': CONTENT_TYPE.PICTURE, 'audio': CONTENT_TYPE.AUDIO, 'video': CONTENT_TYPE.VIDEO}

    def on_create(self, docs):
        """ Create corresponding item on file upload """

        for doc in docs:
            if 'media' not in doc or doc['media'] is None:
                abort(400, description="No media found")

            file, content_type, metadata = self.get_file_from_document(doc)
            inserted = [doc['media']]
            file_type = content_type.split('/')[0]

            self._set_metadata(doc)

            try:
                doc[ITEM_TYPE] = self.type_av.get(file_type)

                rendition_spec = config.RENDITIONS['picture']
                renditions = generate_renditions(file, doc['media'], inserted, file_type,
                                                 content_type, rendition_spec, url_for_media)
                doc['renditions'] = renditions
                doc['mimetype'] = content_type
                doc['filemeta'] = metadata

                add_activity('upload', 'uploaded media {{ name }}',
                             'archive', item=doc,
                             name=doc.get('headline', doc.get('mimetype')),
                             renditions=doc.get('renditions'))
            except Exception as io:
                logger.exception(io)
                for file_id in inserted:
                    delete_file_on_error(doc, file_id)
                abort(500)

    def _set_metadata(self, doc):
        """
        Adds metadata to doc.
        """

        update_dates_for(doc)
        generate_unique_id_and_name(doc)
        doc['guid'] = generate_guid(type=GUID_TAG)
        doc.setdefault(config.ID_FIELD, doc['guid'])
        doc[config.VERSION] = 1
        set_item_expiry({}, doc)

        if not doc.get('_import', None):
            set_original_creator(doc)

        doc.setdefault(ITEM_STATE, CONTENT_STATE.DRAFT)

        if not doc.get('ingest_provider'):
            doc['source'] = DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES

        copy_metadata_from_user_preferences(doc)

    def get_file_from_document(self, doc):
        file = doc.get('media_fetched')
        if file:
            del doc['media_fetched']
        else:
            content = doc['media']
            res = process_file_from_stream(content, content_type=content.mimetype)
            file_name, content_type, metadata = res
            logger.debug('Going to save media file with %s ' % file_name)
            content.seek(0)
            doc['media'] = app.media.put(content, filename=file_name, content_type=content_type, metadata=metadata)
            return content, content_type, decode_metadata(metadata)

        return file, file.content_type, file.metadata
