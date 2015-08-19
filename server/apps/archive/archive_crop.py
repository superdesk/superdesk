# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from flask import request
from superdesk import get_resource_service
from superdesk.resource import Resource
from .common import item_url
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from superdesk.media.media_operations import crop_image, process_file_from_stream
from superdesk.upload import UploadService, url_for_media
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE
from apps.archive.archive import SOURCE as ARCHIVE


class ArchiveCropResource(Resource):
    endpoint_name = 'archive_crop'
    url = 'archive/<{0}:item_id>/crop/<{0}:crop_name>'.format(item_url)
    schema = {
        'CropLeft': {'type': 'integer'},
        'CropRight': {'type': 'integer'},
        'CropTop': {'type': 'integer'},
        'CropBottom': {'type': 'integer'}
    }
    datasource = {'source': 'archive'}
    item_methods = []
    resource_methods = ['GET', 'POST', 'DELETE']
    resource_title = endpoint_name
    privileges = {'POST': 'archive', 'DELETE': 'archive'}


class ArchiveCropService(BaseService):

    def create(self, docs, **kwargs):
        item_id = request.view_args['item_id']
        crop_name = request.view_args['crop_name'].lower()
        archive_service = get_resource_service(ARCHIVE)
        original = archive_service.find_one(req=None, _id=item_id)
        self._validate_crop(original, crop_name, docs[0])
        self._add_crop(original, crop_name, docs[0])
        return [original]

    def delete(self, lookup):
        item_id = request.view_args['item_id']
        crop_name = request.view_args['crop_name'].lower()
        archive_service = get_resource_service(ARCHIVE)
        original = archive_service.find_one(req=None, _id=item_id)
        self._delete_crop(original, crop_name)

    def _validate_crop(self, original, crop_name, doc):
        # Check if type is picture
        if original[ITEM_TYPE] != CONTENT_TYPE.PICTURE:
            raise SuperdeskApiError.badRequestError(message='Only images can be cropped!')

        # Check if the renditions exists
        if not original.get('renditions'):
            raise SuperdeskApiError.badRequestError(message='Missing renditions!')

        # Check if the original rendition exists
        if not original.get('renditions').get('original'):
            raise SuperdeskApiError.badRequestError(message='Missing original rendition!')

        # Check if the crop name is valid
        crops = get_resource_service('vocabularies').find_one(req=None, _id='crop_sizes').get('items')
        if not crops:
            raise SuperdeskApiError.badRequestError(message='Crops couldn\'t be loaded!')

        crop = self._get_crop_by_name(crops, crop_name)
        if not crop:
            raise SuperdeskApiError.badRequestError(message='Unknown crop name!')

        self._validate_aspect_ratio(crop, doc)

    def _validate_aspect_ratio(self, crop, doc):
        """
        Checks if the aspect ratio is consistent with one in defined in spec
        :param crop: Spec parameters
        :param doc: Posted parameters
        :raises SuperdeskApiError.badRequestError:
        """
        width = doc['CropRight'] - doc['CropLeft']
        height = doc['CropBottom'] - doc['CropTop']

        if width < crop['width'] or height < crop['height']:
            raise SuperdeskApiError.badRequestError(
                message='Wrong crop size. Minimum crop size is {}x{}.'.format(crop['width'], crop['height']))

        doc_ratio = round(width / height, 1)
        spec_ratio = round(crop['width'] / crop['height'], 1)
        if doc_ratio != spec_ratio:
            raise SuperdeskApiError.badRequestError(message='Wrong aspect ratio!')

    def _get_crop_by_name(self, crops, crop_name):
        """
        Finds the crop in the list of crops by name
        :param crops: List of crops
        :param crop_name: Crop name
        :return: Matching crop or None
        """
        return next((c for c in crops if c.get('name', '').lower() == crop_name.lower()), None)

    def _delete_crop(self, original, crop_name):
        """ Deletes an existing crop with the given name """
        renditions = original.get('renditions')
        renditions.pop(crop_name, None)
        get_resource_service(ARCHIVE).patch(original['_id'], {'renditions': renditions})

    def _add_crop(self, original, crop_name, doc):
        """
        Updates the crop with the same name if exists,
        otherwise creates a new crop with the given parameters
        :param original: Article to add the crop
        :param crop_name: Name of the crop
        :param doc: Crop details
        :raises SuperdeskApiError.badRequestError
        """
        renditions = original.get('renditions')
        crop_data = UploadService().get_cropping_data(doc)
        original_image = original.get('renditions').get('original')
        original_file = superdesk.app.media.get(original_image.get('media'), 'upload')
        if not original_file:
            raise SuperdeskApiError.badRequestError('Original file couldn\'t be found')

        try:
            cropped, out = crop_image(original_file, original_file.filename, crop_data)
            if cropped:
                renditions[crop_name] = self._save_cropped_image(out, original_file, doc)
                get_resource_service(ARCHIVE).patch(original['_id'], {'renditions': renditions})
            else:
                raise SuperdeskApiError.badRequestError('Saving crop failed: {}'.format(str(out)))
        except SuperdeskApiError:
            raise
        except Exception as ex:
            raise SuperdeskApiError.badRequestError('Generating crop failed: {}'.format(str(ex)))

    def _save_cropped_image(self, file_stream, file, doc):
        """
        Saves the cropped image and returns the crop dictionary
        :param file_stream: cropped image stream
        :param file: original image file
        :param doc: crop data
        :return dict: Crop values
        :raises SuperdeskApiError.internalError
        """
        crop = {}
        try:
            file_name, content_type, metadata = process_file_from_stream(file_stream, content_type=file.content_type)
            file_stream.seek(0)
            file_id = superdesk.app.media.put(file_stream, filename=file_name,
                                              content_type=content_type,
                                              resource=self.datasource,
                                              metadata=metadata)
            crop['media'] = file_id
            crop['mime_type'] = content_type
            crop['href'] = url_for_media(file_id)
            crop['CropTop'] = doc.get('CropTop', None)
            crop['CropLeft'] = doc.get('CropLeft', None)
            crop['CropRight'] = doc.get('CropRight', None)
            crop['CropBottom'] = doc.get('CropBottom', None)
            return crop
        except Exception as ex:
            try:
                superdesk.app.media.delete(file_id)
            except:
                pass
            raise SuperdeskApiError.internalError('Generating crop failed: {}'.format(str(ex)))
