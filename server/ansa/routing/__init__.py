
import superdesk

from superdesk.notification import push_notification

PRIVILEGE = 'desk_routing'


class ClosedDeskResource(superdesk.Resource):
    """Custom resource to change desk.is_closed

    Allowing users without desk management privileges to close/open desk.
    """

    schema = {
        'is_closed': {'type': 'boolean'},
        'closed_destination': superdesk.Resource.rel('desks'),
    }

    datasource = {
        'source': 'desks',
    }

    privileges = {
        'PATCH': PRIVILEGE,  # anyone who can edit can turn it on/off
    }

    resource_methods = []
    item_methods = ['PATCH']


class ClosedDeskService(superdesk.Service):

    def on_updated(self, updates, original):
        push_notification('desks:closed',
                          is_closed=updates.get('is_closed'),
                          _id=original.get('_id'),
                          _etag=updates.get('_etag'))


def init_app(app):
    app.config['DOMAIN']['desks']['schema'].update({
        'is_closed': {'type': 'boolean'},
        'closed_destination': superdesk.Resource.rel('desks'),
    })

    app.config['SOURCES']['desks']['projection'].update({
        'is_closed': 1,
        'closed_destination': 1,
    })

    superdesk.register_resource('closed_desks', ClosedDeskResource, ClosedDeskService, _app=app)

    superdesk.privilege(
        name=PRIVILEGE,
        label='Desk routing',
        description='User can configure desk routing')
