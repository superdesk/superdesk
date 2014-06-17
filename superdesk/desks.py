import superdesk
from bson.objectid import ObjectId


desks_schema = {
    'name': {
        'type': 'string',
        'unique': True,
        'required': True,
    },
    'members': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'user': {
                    'type': 'objectid',
                    'data_relation': {'resource': 'users', 'field': '_id', 'embeddable': True}
                }
            }
        }
    }
}


def on_lookup_user_desks(data, lookup):
    if lookup.get('user_id'):
        lookup["members.user"] = ObjectId(lookup['user_id'])
        del lookup['user_id']


superdesk.connect('before_read:user_desks', on_lookup_user_desks)


superdesk.domain('desks', {
    'schema': desks_schema,
    'datasource': {
        'default_sort': [('created', -1)]
    }
})


superdesk.domain('user_desks', {
    'url': 'users/<regex("[a-f0-9]{24}"):user_id>/desks',
    'schema': desks_schema,
    'datasource': {
        'source': 'desks'
    },
    'resource_methods': ['GET'],
})
