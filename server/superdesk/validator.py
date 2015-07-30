# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import re
import superdesk

from bson import ObjectId
from eve.io.mongo import Validator
from eve.utils import config
from werkzeug.datastructures import FileStorage
from eve.auth import auth_field_and_value


ERROR_PATTERN = {'pattern': 1}
ERROR_UNIQUE = {'unique': 1}
ERROR_MINLENGTH = {'minlength': 1}
ERROR_REQUIRED = {'required': 1}
ERROR_JSON_LIST = {'json_list': 1}


class SuperdeskValidator(Validator):

    def _validate_mapping(self, mapping, field, value):
        pass

    def _validate_index(self, field, value):
        pass

    def _validate_type_phone_number(self, field, value):
        """ Enables validation for `phone_number` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        if not re.match("^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$", value):
            self._error(field, ERROR_PATTERN)

    def _validate_type_email(self, field, value):
        """ Enables validation for `email` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        regex = "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@" \
                "(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+(?:\.[a-z0-9](?:[a-z0-9-]{0,4}[a-z0-9])?)*$"
        if not re.match(regex, value, re.IGNORECASE):
            self._error(field, ERROR_PATTERN)

    def _validate_type_file(self, field, value):
        """Enables validation for `file` schema attribute."""
        if not isinstance(value, FileStorage):
            self._error(field, ERROR_PATTERN)

    def _validate_unique(self, unique, field, value):
        """Validate unique with custom error msg."""

        if not self.resource.endswith("autosave") and unique:
            query = {field: value}
            self._set_id_query(query)

            if superdesk.get_resource_service(self.resource).find_one(req=None, **query):
                self._error(field, ERROR_UNIQUE)

    def _set_id_query(self, query):
            if self._id:
                try:
                    query[config.ID_FIELD] = {'$ne': ObjectId(self._id)}
                except:
                    query[config.ID_FIELD] = {'$ne': self._id}

    def _validate_iunique(self, unique, field, value):
        """Validate uniqueness ignoring case.MONGODB USE ONLY"""

        if unique:
            query = {field: re.compile('^{}$'.format(value.strip()), re.IGNORECASE)}
            self._set_id_query(query)

            if superdesk.get_resource_service(self.resource).find_one(req=None, **query):
                self._error(field, ERROR_UNIQUE)

    def _validate_iunique_per_parent(self, parent_field, field, value):
        """Validate uniqueness ignoring case.MONGODB USE ONLY"""
        original = self._original_document or {}
        update = self.document or {}

        parent_field_value = update.get(parent_field, original.get(parent_field))

        if parent_field:
            query = {field: re.compile('^{}$'.format(value.strip()),
                                       re.IGNORECASE), parent_field: parent_field_value}
            self._set_id_query(query)

            if superdesk.get_resource_service(self.resource).find_one(req=None, **query):
                self._error(field, ERROR_UNIQUE)

    def _validate_minlength(self, min_length, field, value):
        """Validate minlength with custom error msg."""
        if isinstance(value, (type(''), list)):
            if len(value) < min_length:
                self._error(field, ERROR_MINLENGTH)

    def _validate_required_fields(self, document):
        required = list(field for field, definition in self.schema.items()
                        if definition.get('required') is True)
        missing = set(required) - set(key for key in document.keys()
                                      if document.get(key) is not None
                                      or not self.ignore_none_values)
        for field in missing:
            self._error(field, ERROR_REQUIRED)

    def _validate_type_json_list(self, field, value):
        """It will fail later when loading."""
        if not isinstance(value, type('')):
            self._error(field, ERROR_JSON_LIST)

    def _validate_unique_to_user(self, unique, field, value):
        """Check that value is unique globally or to current user.

        In case 'user' is set within document it will check for unique within
        docs with same 'user' value.

        Otherwise it will check for unique within docs without any 'user' value.
        """
        doc = getattr(self, 'document', getattr(self, 'original_document', {}))

        if 'user' in doc:
            _, auth_value = auth_field_and_value(self.resource)
            query = {'user': auth_value}
        else:
            query = {'user': {'$exists': False}}

        self._is_value_unique(unique, field, value, query)
