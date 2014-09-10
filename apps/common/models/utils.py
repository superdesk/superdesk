from superdesk import app_models
from .base_model import BaseModel


def register_model(model):
    app_models[model.name()] = model


def get_model(name):
    if isinstance(name, BaseModel) or (type(name) is type and issubclass(name, BaseModel)):
        name = name.name()
    return app_models[name]
