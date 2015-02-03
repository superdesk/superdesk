# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from builtins import NotImplementedError


class DataLayer():
    def etag(self, doc):
        raise NotImplementedError()

    def find_one(self, resource, filter, projection, options):
        raise NotImplementedError()

    def find(self, resource, filter, projection, options):
        raise NotImplementedError()

    def create(self, resource, docs):
        raise NotImplementedError()

    def update(self, resource, filter, doc):
        raise NotImplementedError()

    def replace(self, resource, filter, doc):
        raise NotImplementedError()

    def delete(self, resource, filter):
        raise NotImplementedError()
