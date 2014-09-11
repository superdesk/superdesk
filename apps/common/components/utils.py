from superdesk import app_components
from .base_component import BaseComponent


def register_component(component):
    '''
    Register a component - to be used in bootstrap.
    @param component: object
        The component object.
    '''
    assert isinstance(component, BaseComponent), 'Invalid component %s' % component
    app_components[component.name()] = component


def get_component(name):
    '''
    Return an instance of the component identified by given name.
    '''
    if isinstance(name, BaseComponent) or (type(name) is type and issubclass(name, BaseComponent)):
        name = name.name()
    return app_components[name]
