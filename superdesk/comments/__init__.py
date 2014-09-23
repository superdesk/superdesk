"""Generic comments module."""
from .comments import CommentsService, CommentsResource, comments_schema  # noqa
import superdesk


def init_app(app):
    endpoint_name = 'comments'
    service = CommentsService(endpoint_name, backend=superdesk.get_backend())
    CommentsResource(endpoint_name, app=app, service=service)
