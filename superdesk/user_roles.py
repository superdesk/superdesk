
import superdesk


def sync_users_role_name(data, **kwargs):
    if kwargs['updates'].get('name'):
        old_role = data.find_one('user_roles', _id=str(kwargs['id']))
        query = {'role': old_role['name']}
        update = {'role': kwargs['updates']['name']}
        data.update_all('users', query, update)


superdesk.connect('update:user_roles', sync_users_role_name)

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
