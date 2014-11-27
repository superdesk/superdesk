from superdesk.resource import Resource
LINKED_IN_PACKAGES = 'linked_in_packages'


not_analyzed = {'type': 'string', 'index': 'not_analyzed'}


metadata_schema = {
    # Identifiers
    'guid': {
        'type': 'string',
        'unique': True,
        'mapping': not_analyzed
    },
    'unique_id': {
        'type': 'integer',
        'unique': True,
    },
    'unique_name': {
        'type': 'string',
        'unique': True,
        'mapping': not_analyzed
    },
    'parent_id': {
        'type': 'string',
        'unique': True,
        'mapping': not_analyzed
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
        'type': 'string',
        'mapping': not_analyzed
    },
    'original_source': {    # This value is extracted from the ingest
        'type': 'string',
        'mapping': not_analyzed
    },
    'ingest_provider_sequence': {
        'type': 'string',
        'mapping': not_analyzed
    },

    # Copyright Information
    'usageterms': {
        'type': 'string',
        'mapping': not_analyzed
    },

    # Category Details
    'anpa-category': {
        'type': 'dict',
        'mapping': {
            'type': 'object',
            'properties': {
                'qcode': not_analyzed,
                'name': not_analyzed,
            }
        }
    },

    'subject': {
        'type': 'list',
        'mapping': {
            'properties': {
                'qcode': not_analyzed,
                'name': not_analyzed
            }
        }
    },
    'genre': {
        'type': 'list',
        'mapping': {
            'properties': {
                'name': not_analyzed
            }
        }
    },

    # Story Metadata
    'type': {
        'type': 'string',
        'required': True,
        'allowed': ['text', 'preformatted', 'audio', 'video', 'picture', 'graphic', 'composite'],
        'default': 'text',
        'mapping': not_analyzed
    },
    'language': {
        'type': 'string',
        'default': 'en',
        'mapping': not_analyzed
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
        'type': 'string',
        'mapping': not_analyzed
    },
    'urgency': {
        'type': 'integer'
    },
    'pubstatus': {
        'type': 'string',
        'allowed': ['Usable', 'Withhold', 'Canceled'],
        'default': 'Usable',
        'mapping': not_analyzed
    },
    'signal': {
        'type': 'string',
        'mapping': not_analyzed
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
        'type': 'string',
        'mapping': not_analyzed
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
        'type': 'string',
        'mapping': not_analyzed,
        'versioned': False
    },

    'lock_user': Resource.rel('users'),
    'lock_time': {
        'type': 'datetime',
        'versioned': False
    },
    'lock_session': Resource.rel('auth')
}

metadata_schema['lock_user']['versioned'] = False
metadata_schema['lock_session']['versioned'] = False
