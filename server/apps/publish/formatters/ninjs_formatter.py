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
from superdesk.utils import json_serialize_datetime_objectId


class NINJSFormatter(Formatter):
    """
    NINJS Formatter
    """
    direct_copy_properties = ['versioncreated', 'usageterms', 'subject', 'language', 'headline',
                              'urgency', 'pubstatus', 'mimetype', 'renditions', 'place',
                              '_created', '_updated', 'body_text', 'body_html']

    def format(self, article, subscriber):
        try:
            pub_seq_num = superdesk.get_resource_service('subscribers').generate_sequence_number(subscriber)

            ninjs = {
                '_id': article['_id'],
                'version': str(article['_current_version']),
                'type': self._get_type(article)
            }
            try:
                ninjs['byline'] = self._get_byline(article)
            except:
                pass

            located = article.get('dateline', {}).get('located', {}).get('city')
            if located:
                ninjs['located'] = article.get('dateline', {}).get('located', {}).get('city', '')

            for copy_property in self.direct_copy_properties:
                if copy_property in article:
                    ninjs[copy_property] = article[copy_property]

            if 'description' in article:
                ninjs['description_text'] = article['description']

            if article['type'] == 'composite':
                ninjs['associations'] = self._get_associations(article)

            return [(pub_seq_num, json.dumps(ninjs, default=json_serialize_datetime_objectId))]
        except Exception as ex:
            raise FormatterError.ninjsFormatterError(ex, subscriber)

    def can_format(self, format_type, article):
        return format_type == 'ninjs'

    def _get_byline(self, article):
        if 'byline' in article:
            return article['byline']
        user = superdesk.get_resource_service('users').find_one(req=None, _id=article['original_creator'])
        if user:
            return user['display_name']
        raise Exception('User not found')

    def _get_type(self, article):
        if article['type'] == 'preformatted':
            return 'text'
        return article['type']

    def _get_associations(self, article):
        associations = dict()
        for group in article['groups']:
            for ref in group['refs']:
                if 'guid' in ref:
                    associations[group['id']] = {}
                    associations[group['id']]['_id'] = ref['residRef']
                    associations[group['id']]['type'] = ref['type']
        return associations
