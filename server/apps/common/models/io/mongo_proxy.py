# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from apps.common.models.io.base_proxy import BaseProxy


class MongoProxy(BaseProxy):
    '''
    Data layer implementation used to connect the models to the Mongo data layer.
    Transforms the model data layer API into Eve data layer calls.
    '''
    def __init__(self, data_layer):
        self.data_layer = data_layer

    def create(self, resource, docs):
        return self.data_layer.insert(resource, docs)
