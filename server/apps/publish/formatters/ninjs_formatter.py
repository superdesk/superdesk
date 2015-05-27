# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json

from apps.publish.formatters import Formatter
import superdesk
from superdesk.errors import FormatterError
from bson import json_util


class NINJSFormatter(Formatter):
    """
    NINJS Formatter
    """
    direct_copy_properties = ['versioncreated', 'usageterms', 'subject', 'language', 'headline',
                              'urgency', 'pubstatus', 'mimetype', 'renditions', 'place', 'located']

    def format(self, article, destination):
        try:
            pub_seq_num = superdesk.get_resource_service('output_channels').generate_sequence_number(destination)

            ninjs = {}
            ninjs['_id'] = article['_id']
            ninjs['version'] = str(article['version'])
            ninjs['type'] = self._get_type(article)
            try:
                ninjs['byline'] = self._get_byline(article)
            except Exception:
                pass
            for property in self.direct_copy_properties:
                if property in article:
                    ninjs[property] = article[property]
            if article['type'] == 'composite':
                article['associations'] = self._get_associations(article)

            return pub_seq_num, json.dumps(ninjs, default=json_util.default)
        except Exception as ex:
            raise FormatterError.ninjsFormatterError(ex, destination)

    def can_format(self, format_type):
        return format_type == 'ninjs'

    def _get_byline(self, article):
        if 'byline' in article:
            return article['byline']
        user = superdesk.get_resource_service('users').find_one(article['original_creator'])
        if user:
            return user['display_name']
        raise Exception('User not found')

    def _get_type(self, article):
        if article['type'] == 'preformatted':
            return 'text'
        return article['type']

    def _get_associations(self, article):
        associations = set()
        for group in article['groups']:
            for ref in group['refs']:
                if 'guid' in ref:
                    associations.add(ref['guid'])
