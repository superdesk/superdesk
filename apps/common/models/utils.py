from superdesk import app_models
from .base_model import BaseModel


def register_model(model):
    '''
    Register a model - to be used in bootstrap.
    @param model: object
        The model object.
    '''
    assert isinstance(model, BaseModel), 'Invalid model %s' % model
    app_models[model.name()] = model


def get_model(name):
    '''
    Return an instance of the model identified by given name.
    '''
    if isinstance(name, BaseModel) or (type(name) is type and issubclass(name, BaseModel)):
        name = name.name()
    return app_models[name]
