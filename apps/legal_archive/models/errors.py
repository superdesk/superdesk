# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from apps.common.models.base_model import BaseModel, Validator


class ErrorsValidator(Validator):
    def validate(self, doc):
        return True


class ErrorsModel(BaseModel):
    def __init__(self, data_layer):
        BaseModel.__init__(self, 'errors', data_layer, {}, ErrorsValidator())

    @classmethod
    def name(cls):
        return 'errors'
