
import superdesk

superdesk.domain('desks', {
    'schema': {
        'name': {
            'type': 'string',
            'unique': True,
            'required': True,
        },
        'members': {
            'type': 'list'
        }
    },
    'datasource': {
        'default_sort': [('created', -1)]
    }
})
