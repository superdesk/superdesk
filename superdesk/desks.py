import superdesk


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


superdesk.domain('desks', {
    'schema': desks_schema,
    'datasource': {
        'default_sort': [('created', -1)]
    }
})


superdesk.domain('user_desks', {
    'url': 'users/<regex("[a-f0-9]{24}"):user>/desks',
    'schema': desks_schema,
    'datasource': {
        'source': 'desks'
    },
    'resource_methods': ['GET'],
})
