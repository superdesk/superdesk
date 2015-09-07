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
import logging
from copy import deepcopy
from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.media.media_operations import crop_image, process_file_from_stream
from superdesk.upload import UploadService, url_for_media
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE


logger = logging.getLogger(__name__)


class ArchiveCropService():

    crop_sizes = []

    def validate_crop(self, original, crop_name, doc):
        """

        :param dict original: original item
        :param str crop_name: name of the crop
        :param dict doc: crop co-ordinates
        :raises SuperdeskApiError.badRequestError:
            For following conditions:
            1) if type != picture
            2) if renditions are missing in the original image
            3) if original rendition is missing
            4) Crop name is invalid
        """
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
        crop = self.get_crop_by_name(crop_name)
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

    def get_crop_by_name(self, crop_name):
        """
        Finds the crop in the list of crops by name
        :param crop_name: Crop name
        :return: Matching crop or None
        """
        if not self.crop_sizes:
            self.crop_sizes = get_resource_service('vocabularies').find_one(req=None, _id='crop_sizes').get('items')

        if not self.crop_sizes:
            raise SuperdeskApiError.badRequestError(message='Crops sizes couldn\'t be loaded!')

        return next((c for c in self.crop_sizes if c.get('name', '').lower() == crop_name.lower()), None)

    def create_crop(self, original, crop_name, doc):
        """
        Create a new crop based on the crop co-ordinates
        :param original: Article to add the crop
        :param crop_name: Name of the crop
        :param doc: Crop details
        :raises SuperdeskApiError.badRequestError
        :return dict: modified renditions
        """
        renditions = original.get('renditions', {})
        crop_data = UploadService().get_cropping_data(doc)
        original_crop = renditions.get(crop_name, {})
        fields = ('CropLeft', 'CropTop', 'CropRight', 'CropBottom')
        crop_created = False

        if any(crop_data[i] != original_crop.get(name) for i, name in enumerate(fields)):

            original_image = renditions.get('original', {})
            original_file = superdesk.app.media.get(original_image.get('media'), 'upload')
            if not original_file:
                raise SuperdeskApiError.badRequestError('Original file couldn\'t be found')

            try:
                cropped, out = crop_image(original_file, original_file.name, crop_data)

                if not cropped:
                    raise SuperdeskApiError.badRequestError('Saving crop failed: {}'.format(str(out)))

                renditions[crop_name] = self._save_cropped_image(out, original_file, doc)
                crop_created = True
            except SuperdeskApiError:
                raise
            except Exception as ex:
                raise SuperdeskApiError.badRequestError('Generating crop failed: {}'.format(str(ex)))

        return renditions, crop_created

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
                                              resource='upload',
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

    def _delete_crop_file(self, file_id):
        """
        Delete the crop file
        :param Object_id file_id: Object_Id of the file.
        """
        try:
            superdesk.app.media.delete(file_id)
        except:
            logger.exception("Crop File cannot be deleted. File_Id {}".format(file_id))

    def create_multiple_crops(self, updates, original):
        """
        Create multiple crops based on the renditions.
        :param dict updates: update item
        :param dict original: original of the updated item
        """
        update_renditions = updates.get('renditions', {})
        if original.get(ITEM_TYPE) == CONTENT_TYPE.PICTURE and update_renditions:
            renditions = original.get('renditions', {})
            original_copy = deepcopy(original)
            for key in update_renditions:
                if self.get_crop_by_name(key):
                    renditions, crop_created = self.create_crop(original_copy, key, update_renditions.get(key, {}))

            updates['renditions'] = renditions

    def validate_multiple_crops(self, updates, original):
        """
        Validate crops for the image
        :param dict updates: update item
        :param dict original: original of the updated item
        """
        renditions = updates.get('renditions', {})
        if renditions and original.get(ITEM_TYPE) == CONTENT_TYPE.PICTURE:
            for key in renditions:
                self.validate_crop(original, key, renditions.get(key, {}))

    def delete_replaced_crop_files(self, updates, original):
        """
        Delete the replaced crop files.
        :param dict updates: update item
        :param dict original: original of the updated item
        """
        update_renditions = updates.get('renditions', {})
        if original.get(ITEM_TYPE) == CONTENT_TYPE.PICTURE and update_renditions:
            renditions = original.get('renditions', {})
            for key in update_renditions:
                if self.get_crop_by_name(key) and \
                        update_renditions.get(key, {}).get('media') != \
                        renditions.get(key, {}).get('media'):
                    self._delete_crop_file(renditions.get(key, {}).get('media'))
