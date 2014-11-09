from superdesk.resource import Resource

metadata_schema = {
    'guid': {
        'type': 'string',
        'unique': True
    },
    'unique_id': {
        'type': 'integer',
        'unique': True
    },
    'unique_name': {
        'type': 'string',
        'unique': True
    },
    'parent_id': {
        'type': 'string',
        'unique': True
    },
    'version': {
        'type': 'integer'
    },
    'original_creator': Resource.rel('users', True),
    'version_creator': Resource.rel('users', True),
    'provider': {
        'type': 'string'
    },
    'type': {
        'type': 'string',
        'required': True,
        'allowed': ['text', 'audio', 'video', 'picture', 'graphic', 'composite'],
        'default': 'text'
    },
    'mimetype': {
        'type': 'string'
    },
    'versioncreated': {
        'type': 'datetime'
    },
    'pubstatus': {
        'type': 'string'
    },
    'copyrightholder': {
        'type': 'string'
    },
    'copyrightnotice': {
        'type': 'string'
    },
    'usageterms': {
        'type': 'string'
    },
    'language': {
        'type': 'string'
    },
    'place': {
        'type': 'list'
    },
    'subject': {
        'type': 'list'
    },
    'byline': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'located': {
        'type': 'string'
    },
    'renditions': {
        'type': 'dict'
    },
    'slugline': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    'description_text': {
        'type': 'string',
        'nullable': True
    },
    'firstcreated': {
        'type': 'datetime'
    },
    'filemeta': {
        'type': 'dict'
    },
    'ingest_provider': {
        'type': 'string'
    },
    'urgency': {
        'type': 'integer'
    },
    'groups': {
        'type': 'list'
    },
    'keywords': {
        'type': 'list'
    },
    'body_html': {
        'type': 'string'
    },
    'media_file': {
        'type': 'string'
    },
    'contents': {
        'type': 'list'
    },
    'task_id': {
        'type': 'string'
    },
    'lock_user': {
        'type': 'objectid',
        'data_relation': {'resource': 'users', 'field': '_id', 'embeddable': True}
    },
    'lock_time': {
        'type': 'datetime'
    },
    'lock_session': {
        'type': 'objectid',
        'data_relation': {'resource': 'auth', 'field': '_id', 'embeddable': True}
    },
    'is_spiked': {
        'type': 'boolean'
    },
    'expiry': {
        'type': 'datetime'
    }
}
