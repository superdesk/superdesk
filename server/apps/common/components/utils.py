# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk import app_components
from .base_component import BaseComponent


def register_component(component):
    """
    Register a component - to be used in bootstrap.
    @param component: object
        The component object.
    """
    assert isinstance(component, BaseComponent), 'Invalid component %s' % component
    app_components[component.name()] = component


def get_component(name):
    """
    Return an instance of the component identified by given name.
    """
    if isinstance(name, BaseComponent) or (type(name) is type and issubclass(name, BaseComponent)):
        name = name.name()
    return app_components[name]
