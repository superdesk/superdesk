from superdesk.resource import Resource
LINKED_IN_PACKAGES = 'linked_in_packages'


metadata_schema = {
    # Identifiers
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

    # Audit Information
    'original_creator': Resource.rel('users'),
    'version_creator': Resource.rel('users'),
    'firstcreated': {
        'type': 'datetime'
    },
    'versioncreated': {
        'type': 'datetime'
    },

    # Ingest Details
    'ingest_provider': Resource.rel('ingest_providers'),
    'source': {     # The value is copied from the ingest_providers vocabulary
        'type': 'string'
    },
    'original_source': {    # This value is extracted from the ingest
        'type': 'string'
    },
    'ingest_provider_sequence': {
        'type': 'string'
    },

    # Copyright Information
    'usageterms': {
        'type': 'string'
    },

    # Category Details
    'anpa-category': {
        'type': 'dict',
        'mapping': {
            'type': 'object',
            'properties': {
                'qcode': {'type': 'string'},
                'name': {'type': 'string', 'index': 'not_analyzed'}
            }
        }
    },

    'subject': {
        'type': 'list'
    },
    'genre': {
        'type': 'list'
    },

    # Story Metadata
    'type': {
        'type': 'string',
        'required': True,
        'allowed': ['text', 'preformatted', 'audio', 'video', 'picture', 'graphic', 'composite'],
        'default': 'text'
    },
    'language': {
        'type': 'string',
        'default': 'en'
    },
    'abstract': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'slugline': {
        'type': 'string'
    },
    'anpa_take_key': {
        'type': 'string'
    },
    'keywords': {
        'type': 'list'
    },
    'word_count': {
        'type': 'integer'
    },
    'priority': {
        'type': 'string'
    },
    'urgency': {
        'type': 'integer'
    },
    'pubstatus': {
        'type': 'string',
        'allowed': ['Usable', 'Withhold', 'Canceled'],
        'default': 'Usable'
    },
    'signal': {
        'type': 'string'
    },
    'byline': {
        'type': 'string'
    },
    'ednote': {
        'type': 'string'
    },
    'description': {
        'type': 'string',
        'nullable': True
    },
    'groups': {
        'type': 'list'
    },
    'body_html': {
        'type': 'string'
    },
    'dateline': {
        'type': 'string'
    },
    'is_spiked': {
        'type': 'boolean'
    },
    'expiry': {
        'type': 'datetime'
    },

    # Media Related
    'media': {
        'type': 'file'
    },
    'mimetype': {
        'type': 'string'
    },
    'renditions': {
        'type': 'dict'
    },
    'filemeta': {
        'type': 'dict'
    },
    'media_file': {
        'type': 'string'
    },
    'contents': {
        'type': 'list'
    },

    # Not Categorized
    'place': {
        'type': 'list'
    },
    'located': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    LINKED_IN_PACKAGES: {
        'type': 'list',
        'readonly': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'package': Resource.rel('packages')
            }
        }
    },

    # Task and Lock Details
    'task_id': {
        'type': 'string'
    },
    'lock_user': Resource.rel('users'),
    'lock_time': {
        'type': 'datetime'
    },
    'lock_session': Resource.rel('auth')
}
