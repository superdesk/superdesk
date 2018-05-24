
import superdesk

from superdesk.notification import push_notification
from apps.content import push_content_notification
from superdesk import get_resource_service

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
        is_closed = updates.get('is_closed', False)
        if not is_closed and original.get('is_closed'):
            desk_id = updates['_id']
            self.remove_marks(desk_id)
        push_notification('desks:closed',
                          is_closed=is_closed,
                          _id=original.get('_id'),
                          _etag=updates.get('_etag'))

    def remove_marks(self, desk_id):
        """Remove "mark for desk" attribute

        :param ObjectId desk_id: id of the desk being re-opened
        """
        for service_name in ('archive', 'published'):
            service = get_resource_service(service_name)
            marked_items = service.find({'task.desk': desk_id, 'marked_desks': {'$exists': True, '$ne': []}})
            for item in marked_items:
                marked_desks = [m for m in item['marked_desks'] if 'user_marked' in m]
                service.system_update(item['_id'], {'marked_desks': marked_desks}, item)
                push_content_notification([item])


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
