
import superdesk
from .workspace import WorkspaceService, WorkspaceResource


def init_app(app):
    superdesk.register_resource('workspaces', WorkspaceResource, WorkspaceService,
                                privilege=['POST', 'PATCH'])
