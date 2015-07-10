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
    def _transmit(self, queue_item, subscriber):
        config = queue_item.get('destination', {}).get('config', {})

        try:
            if isinstance(queue_item['formatted_item'], bytes):
                self.copy_file(config, queue_item)
            elif isinstance(queue_item['formatted_item'], str):
                queue_item['formatted_item'] = queue_item['formatted_item'].encode('utf-8')
                self.copy_file(config, queue_item)
            else:
                raise Exception
        except Exception as ex:
            raise PublishFileError.fileSaveError(ex, config)

    def copy_file(self, config, queue_item):
        with open('{}/{}-{}-{}.{}'.format(config['file_path'],
                                          queue_item['item_id'].replace(':', '-'),
                                          str(queue_item.get('item_version', '')),
                                          str(queue_item.get('published_seq_num', '')),
                                          config.get('file_extension', 'txt')), 'wb') as f:
            f.write(queue_item['formatted_item'])


register_transmitter('File', FilePublishService(), errors)
