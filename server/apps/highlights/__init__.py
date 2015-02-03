from apps.highlights.resource import HighlightsResource, MarkedForHighlightsResource
from apps.highlights.service import HighlightsService, MarkedForHighlightsService
from superdesk import get_backend
import superdesk


def init_app(app):
    endpoint_name = 'highlights'
    service = HighlightsService(endpoint_name, backend=get_backend())
    HighlightsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'marked_for_highlights'
    service = MarkedForHighlightsService(endpoint_name, backend=get_backend())
    MarkedForHighlightsResource(endpoint_name, app=app, service=service)

    superdesk.privilege(name='highlights', label='Highlights/Summary List Management',
                        description='User can manage highlights/summary lists.')
    superdesk.privilege(name='mark_for_highlights', label='Mark items for Highlights/Summary Lists',
                        description='User can mark items for Highlights/Summary Lists.')
