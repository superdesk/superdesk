# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish.publish_service import PublishService
from superdesk.publish import register_transmitter
from superdesk.errors import PublishFileError

errors = [PublishFileError.fileSaveError().get_error_description()]


class FilePublishService(PublishService):
    def _transmit(self, formatted_item, subscriber, output_channel):
        config = output_channel.get('config', {})

        try:
            item = formatted_item['formatted_item']
            if isinstance(item, bytes):
                with open('{}/{}-{}.{}'.format(config['file_path'], formatted_item['item_id'].replace(':', '-'),
                                               str(formatted_item.get('item_version', '')),
                                               'txt'), 'wb') as f:
                    f.write(item)
            else:
                raise Exception
        except Exception as ex:
            raise PublishFileError.fileSaveError(ex, output_channel)


register_transmitter('File', FilePublishService(), errors)
