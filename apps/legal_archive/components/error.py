# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from apps.common.components.base_component import BaseComponent
from apps.common.models.utils import get_model
from apps.legal_archive.models.errors import ErrorsModel


class Error(BaseComponent):
    def __init__(self, app):
        self.app = app

    @classmethod
    def name(cls):
        return 'error'

    def create(self, resource, docs, error):
        error = {'resource': resource, 'docs': docs, 'error': error}
        get_model(ErrorsModel).create(error)
