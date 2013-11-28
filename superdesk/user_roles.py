
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
            'type': 'list'
        }
    }
})
