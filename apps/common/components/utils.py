from superdesk import app_components
from .base_component import BaseComponent


def register_component(component):
    app_components[component.name()] = component


def get_component(name):
    if isinstance(name, BaseComponent) or (type(name) is type and issubclass(name, BaseComponent)):
        name = name.name()
    return app_components[name]
