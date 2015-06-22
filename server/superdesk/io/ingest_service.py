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
import superdesk

from datetime import datetime
from superdesk.utc import utc, utcnow
from superdesk.errors import SuperdeskApiError, SuperdeskIngestError
from superdesk.io import register_provider


logger = logging.getLogger(__name__)


class AutoRegisteredMeta(type):
    """Metaclass for automatically registering the ingest service instances.

    An instance of an ingest class is registered as a provider when the class
    is instantiated - but only if the class defines a `PROVIDER` attribute
    containing the name under which to register the class instances.

    Every ingest provider class needs to define an `ERRORS` attribute
    representing a list of <error_number, error_message> pairs that might be
    raised by the class instances' methods.

    If another provider class with the same `PROVIDER` name has already been
    defined, a TypeError is raised.
    """
    _providers = {}  # keep track of all PROVIDER names defined in classes

    def __new__(metacls, name, bases, attrs):
        provider_name = attrs.get('PROVIDER')

        if provider_name is not None:
            if 'ERRORS' not in attrs:
                raise AttributeError(
                    "Provider class {} must define "
                    "the ERRORS list attribute.".format(name))

            if provider_name in metacls._providers:
                raise TypeError(
                    "PROVIDER {} already exists (class {}).".format(
                        provider_name, metacls._providers[provider_name])
                )

            metacls._providers[provider_name] = name

        return super().__new__(metacls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        # NOTE: Registration cannot be done in __new__ or __init__, because the
        # class cannot be instantiated there yet (a RuntimeError occurs), thus
        # we need to perform the registration here in __call__ (when a new
        # class instance is going to be created).

        new_instance = super().__call__(*args, **kwargs)

        if hasattr(cls, 'PROVIDER'):
            register_provider(cls.PROVIDER, new_instance, cls.ERRORS)

        return new_instance


class IngestService(metaclass=AutoRegisteredMeta):
    """Base ingest service class."""

    def get_items(self, guid):
        raise LookupError()

    def _update(self, provider):
        raise NotImplementedError()

    def update(self, provider):
        is_closed = provider.get('is_closed', False)
        if isinstance(is_closed, datetime):
            is_closed = False
        if is_closed:
            raise SuperdeskApiError.internalError('Ingest Provider is closed')
        else:
            try:
                return self._update(provider) or []
            except SuperdeskIngestError as error:
                self.close_provider(provider, error)
                raise error

    def close_provider(self, provider, error):
        if provider.get('critical_errors', {}).get(str(error.code)):
            update = {
                'is_closed': True,
                'last_closed': {
                    'closed_at': utcnow(),
                    'message': 'Channel closed due to critical error: {}'.format(error)
                }
            }

            ingest_service = superdesk.get_resource_service('ingest_providers')
            ingest_service.system_update(provider[superdesk.config.ID_FIELD], update, provider)

    def add_timestamps(self, item):
        """Adds firstcreated and versioncreated timestamps

        :param item:
        """
        item['firstcreated'] = utc.localize(item['firstcreated']) if item.get('firstcreated') else utcnow()
        item['versioncreated'] = utc.localize(item['versioncreated']) if item.get('versioncreated') else utcnow()

    def log_item_error(self, err, item, provider):
        """TODO: put item into provider error basket."""
        logger.warning('ingest error msg={} item={} provider={}'.format(
            str(err),
            item.get('guid'),
            provider.get('name')
        ))
