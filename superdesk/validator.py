import re
import json

from bson import ObjectId

from eve.io.mongo import Validator
from eve.utils import config, ParsedRequest
from eve_elastic.elastic import Elastic
from werkzeug.datastructures import FileStorage

import superdesk
from superdesk import get_backend


ERROR_PATTERN = {'pattern': 1}
ERROR_UNIQUE = {'unique': 1}
ERROR_MINLENGTH = {'minlength': 1}
ERROR_REQUIRED = {'required': 1}


class SuperdeskValidator(Validator):
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
                "(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,4}[a-z0-9]){1}$"
        if not re.match(regex, value):
            self._error(field, ERROR_PATTERN)

    def _validate_type_file(self, field, value):
        """Enables validation for `file` schema attribute."""
        if not isinstance(value, FileStorage):
            self._error(field, ERROR_PATTERN)

    def _validate_unique(self, unique, field, value):
        """Validate unique with custom error msg."""

        if not self.resource.endswith("autosave") and unique:
            backend = get_backend()._lookup_backend(self.resource)

            if isinstance(backend, Elastic) and self._id:
                query = {"query": {"filtered": {"query": {"match": {field: value}},
                                                "filter": {"bool": {"must_not": {"term": {"_id": self._id}}}}}}}

                req = ParsedRequest()
                req.args = {'source': json.dumps(query)}
                docs = superdesk.get_resource_service(self.resource).get(req=req, lookup=None)

                if docs.count():
                    self._error(field, ERROR_UNIQUE)
            else:
                query = {field: value}
                if self._id:
                    try:
                        query[config.ID_FIELD] = {'$ne': ObjectId(self._id)}
                    except:
                        query[config.ID_FIELD] = {'$ne': self._id}

                if superdesk.get_resource_service(self.resource).find_one(req=None, **query):
                    self._error(field, ERROR_UNIQUE)

    def _validate_iunique(self, unique, field, value):
        """Validate uniqueness ignoring case.MONGODB USE ONLY"""

        if unique:
            query = {field: re.compile(value, re.IGNORECASE)}

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
