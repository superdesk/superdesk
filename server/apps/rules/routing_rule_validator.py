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
import re

logger = logging.getLogger(__name__)


class RoutingRuleValidator():

    def is_valid_rule(self, item, rule_filter):
        if not rule_filter:
            return True

        return (
            self.__is_valid_category(item, rule_filter) and
            self.__is_valid_subject(item, rule_filter) and
            self.__is_valid_genre(item, rule_filter) and
            self.__is_valid_type(item, rule_filter) and
            self.__is_valid_field_regex(item.get('headline', ''),
                                        rule_filter.get('headline', ''), re.I) and
            self.__is_valid_field_regex(item.get('body_html', item.get('body_text', '')),
                                        rule_filter.get('body', ''), re.I | re.M) and
            self.__is_valid_field_regex(item.get('slugline', ''),
                                        rule_filter.get('slugline', ''), re.I)

        )

    def __is_valid_category(self, item, rule_filter):
        rule_categories = [category.get('qcode', '').lower() for category in rule_filter.get('category', [])]
        item_categories = [str.lower(item.get('anpa-category', {}).get('qcode', ''))]
        return self.__is_valid_field_values(item_categories, rule_categories)

    def __is_valid_subject(self, item, rule_filter):
        rule_subjects = [subject.get('qcode') for subject in rule_filter.get('subject', [])]
        item_subjects = [subject.get('qcode') for subject in item.get('subject', [])]
        return self.__is_valid_field_values(item_subjects, rule_subjects)

    def __is_valid_genre(self, item, rule_filter):
        return self.__is_valid_field_values(item.get('genre', []), rule_filter.get('genre', []))

    def __is_valid_type(self, item, rule_filter):
        return self.__is_valid_field_values([item.get('type')], rule_filter.get('type', []))

    def __is_valid_field_values(self, item_field_value_list, rule_field_value_list):
        return len(rule_field_value_list) == 0 or \
            len(set(rule_field_value_list) & set(item_field_value_list)) > 0

    def __is_valid_field_regex(self, item_field, rule_filter_field, options):
        if rule_filter_field:
            expression = re.compile(rule_filter_field, options)
            return expression.search(item_field) or False

        return True
