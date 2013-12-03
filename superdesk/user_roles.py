
import superdesk

superdesk.domain('user_roles', {
    'schema': {
        'name': {
            'type': 'string',
            'unique': True,
            'required': True,
        },
        'child_of': {
            'type': 'objectid'
        },
        'permissions': {
            'type': 'dict'
        }
    },
    'datasource': {
        'default_sort': [('created', -1)]
    }
})
