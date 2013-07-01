from types import Resource
from models import Item

def get_date(date):
    return date.isoformat()

def get_list_item(item):
    return {
        'guid': item.guid,
        'version': item.version,
        'urgency': item.urgency,
        'slugline': item.slugline,
        'headline': item.headline,
        'first_created': get_date(item.firstCreated),
        'version_created': get_date(item.versionCreated),
    }

class Items(Resource):
    '''Items resource.'''

    def get(self):
        query = Item.objects.order_by('-firstCreated').limit(25)
        return [get_list_item(item) for item in query]

