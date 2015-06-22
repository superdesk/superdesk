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
            if isinstance(formatted_item['formatted_item'], bytes):
                self.copy_file(config, formatted_item)
            elif isinstance(formatted_item['formatted_item'], str):
                formatted_item['formatted_item'] = formatted_item['formatted_item'].encode('utf-8')
                self.copy_file(config, formatted_item)
            else:
                raise Exception
        except Exception as ex:
            raise PublishFileError.fileSaveError(ex, output_channel)

    def copy_file(self, config, formatted_item):
        with open('{}/{}-{}.{}'.format(config['file_path'],
                                       formatted_item['item_id'].replace(':', '-'),
                                       str(formatted_item.get('item_version', '')),
                                       config.get('file_extension', 'txt')), 'wb') as f:
            f.write(formatted_item['formatted_item'])

register_transmitter('File', FilePublishService(), errors)
