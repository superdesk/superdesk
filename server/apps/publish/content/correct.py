# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk import get_resource_service
from superdesk.media.crop import CropService
from superdesk.metadata.item import ITEM_STATE, CONTENT_STATE
from superdesk.metadata.packages import PACKAGE_TYPE

from eve.utils import config

from apps.archive.common import set_sign_off, ITEM_OPERATION, insert_into_versions

from .common import BasePublishService, BasePublishResource, ITEM_CORRECT


logger = logging.getLogger(__name__)


class CorrectPublishResource(BasePublishResource):

    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'correct')


class CorrectPublishService(BasePublishService):
    publish_type = 'correct'
    published_state = 'corrected'

    def on_update(self, updates, original):
        CropService().validate_multiple_crops(updates, original)
        super().on_update(updates, original)
        updates[ITEM_OPERATION] = ITEM_CORRECT
        set_sign_off(updates, original)

    def on_updated(self, updates, original):
        """
        Locates the published or corrected non-take packages containing the corrected item
        and corrects them
        :param updates: correction
        :param original: original story
        """
        original_updates = dict()
        original_updates['operation'] = updates['operation']
        original_updates[ITEM_STATE] = updates[ITEM_STATE]
        super().on_updated(updates, original)
        CropService().delete_replaced_crop_files(updates, original)
        packages = self.package_service.get_packages(original[config.ID_FIELD])
        if packages and packages.count() > 0:
            archive_correct = get_resource_service('archive_correct')
            processed_packages = []
            for package in packages:
                if package[ITEM_STATE] in [CONTENT_STATE.PUBLISHED, CONTENT_STATE.CORRECTED] and \
                        package.get(PACKAGE_TYPE, '') == '' and \
                        str(package[config.ID_FIELD]) not in processed_packages:
                    original_updates['groups'] = package['groups']

                    if updates.get('headline'):
                        self.package_service.update_field_in_package(original_updates, original[config.ID_FIELD],
                                                                     'headline', updates.get('headline'))

                    if updates.get('slugline'):
                        self.package_service.update_field_in_package(original_updates, original[config.ID_FIELD],
                                                                     'slugline', updates.get('slugline'))

                    archive_correct.patch(id=package[config.ID_FIELD], updates=original_updates)
                    insert_into_versions(id_=package[config.ID_FIELD])
                    processed_packages.append(package[config.ID_FIELD])

    def update(self, id, updates, original):
        CropService().create_multiple_crops(updates, original)
        super().update(id, updates, original)
