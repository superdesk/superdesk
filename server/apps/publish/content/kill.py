# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.versioning import resolve_document_version
from .common import BasePublishService, BasePublishResource, ITEM_KILL
from eve.utils import config
from superdesk.metadata.item import CONTENT_STATE, ITEM_STATE, GUID_FIELD, PUB_STATUS
from superdesk.metadata.packages import PACKAGE_TYPE
from superdesk import get_resource_service
from superdesk.utc import utcnow
import logging
from copy import copy
from superdesk.emails import send_article_killed_email
from superdesk.errors import SuperdeskApiError
from apps.archive.common import ITEM_OPERATION, ARCHIVE, insert_into_versions
from apps.templates.content_templates import render_content_template

logger = logging.getLogger(__name__)


class KillPublishResource(BasePublishResource):
    def __init__(self, endpoint_name, app, service):
        super().__init__(endpoint_name, app, service, 'kill')


class KillPublishService(BasePublishService):
    publish_type = 'kill'
    published_state = 'killed'

    def __init__(self, datasource=None, backend=None):
        super().__init__(datasource=datasource, backend=backend)

    def on_update(self, updates, original):
        # check if we are trying to kill and item that is contained in normal non takes package
        # and the package itself is not killed.

        packages = self.package_service.get_packages(original[config.ID_FIELD])
        if packages and packages.count() > 0:
            for package in packages:
                if package[ITEM_STATE] != CONTENT_STATE.KILLED and package.get(PACKAGE_TYPE, '') == '':
                    raise SuperdeskApiError.badRequestError(message='This item is in a package. '
                                                                    'It needs to be removed '
                                                                    'before the item can be killed')

        updates['pubstatus'] = PUB_STATUS.CANCELED
        super().on_update(updates, original)
        updates[ITEM_OPERATION] = ITEM_KILL
        self.takes_package_service.process_killed_takes_package(original)
        get_resource_service('archive_broadcast').spike_item(original)

    def update(self, id, updates, original):
        """
        Kill will broadcast kill email notice to all subscriber in the system and then kill the item.
        If item is a take then all the takes are killed as well.
        """
        self.broadcast_kill_email(original)
        super().update(id, updates, original)
        self._publish_kill_for_takes(updates, original)
        get_resource_service('archive_broadcast').kill_broadcast(updates, original)

    def broadcast_kill_email(self, original):
        """
        Sends the broadcast email to all subscribers (including in-active subscribers)
        :param original: Document to kill
        """
        # Get all subscribers
        subscribers = list(get_resource_service('subscribers').get(req=None, lookup=None))
        recipients = [s.get('email') for s in subscribers if s.get('email')]
        # send kill email.
        send_article_killed_email(original, recipients, utcnow())

    def _publish_kill_for_takes(self, updates, original):
        """
        Kill all the takes in a takes package.
        :param updates: Updates of the original document
        :param original: Document to kill
        """
        package = self.takes_package_service.get_take_package(original)
        last_updated = updates.get(config.LAST_UPDATED, utcnow())
        if package:
            for ref in[ref for group in package.get('groups', []) if group['id'] == 'main'
                       for ref in group.get('refs')]:
                if ref[GUID_FIELD] != original[config.ID_FIELD]:
                    original_data = super().find_one(req=None, _id=ref[GUID_FIELD])
                    updates_data = copy(updates)
                    '''
                    Popping out the config.VERSION as Take referenced by original and Take referenced by original_data
                    might have different and if not popped out then it might jump the versions.
                    '''
                    updates_data.pop(config.VERSION, None)
                    self._set_updates(original_data, updates_data, last_updated)
                    self._update_archive(original=original_data, updates=updates_data,
                                         should_insert_into_versions=True)
                    self.update_published_collection(published_item_id=original_data['_id'])

    def kill_item(self, item):
        """
        Kill the item after applying the template.
        :param dict item: Item
        """
        # get the kill template
        template = get_resource_service('content_templates').get_template_by_name('kill')
        if not template:
            SuperdeskApiError.badRequestError(message="Kill Template missing.")

        # apply the kill template
        updates = render_content_template(item, template)
        # resolve the document version
        resolve_document_version(document=updates, resource=ARCHIVE, method='PATCH', latest_doc=item)
        # kill the item
        self.patch(item.get(config.ID_FIELD), updates)
        # insert into versions
        insert_into_versions(id_=item[config.ID_FIELD])
