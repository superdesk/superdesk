# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


class BaseComponent():
    '''
    This is a basic interface for defining components. The only requirement is
    to implement the name method that uniquely identifies a component. It
    should also define other methods that implement the component functionality.
    '''

    @classmethod
    def name(cls):
        raise NotImplementedError()
