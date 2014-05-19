
import re
from bson import ObjectId
from eve.io.mongo import Validator
from eve.utils import config
from flask import current_app as app


class SuperdeskValidator(Validator):
    def _validate_type_phone_number(self, field, value):
        """ Enables validation for `phone_number` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        if not re.match("^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$", value):
            self._error(field, {'format': 1})

    def _validate_type_email(self, field, value):
        """ Enables validation for `phone_number` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        regex = "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@" \
                "(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,4}[a-z0-9]){1}$"
        if not re.match(regex, value):
            self._error(field, {'format': 1})

    def _validate_unique(self, unique, field, value):
        """Override unique validation to return json."""

        if unique:
            query = {field: value}
            if self._id:
                try:
                    query[config.ID_FIELD] = {'$ne': ObjectId(self._id)}
                except:
                    query[config.ID_FIELD] = {'$ne': self._id}

            if app.data.find_one(self.resource, None, **query):
                self._error(field, {'unique': 1})
