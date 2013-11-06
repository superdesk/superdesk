
import superdesk

schema = {
    'guid': {
        'type': 'string'
    },
    'uri': {
        'type': 'string'
    },
    'version': {
        'type': 'string'
    },
    'headline': {
        'type': 'string'
    },
    'slugline': {
        'type': 'string'
    },
    'creditline': {
        'type': 'string'
    },
    'copyrightHolder': {
        'type': 'string'
    },
    'description_text': {
        'type': 'string'
    },
    'firstcreated': {
        'type': 'datetime'
    },
    'versioncreated': {
        'type': 'datetime'
    },
    'type': {
        'type': 'string'
    },
    'provider': {
        'type': 'string'
    },
    'ingest_provider': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'ingest_providers',
            'field': '_id',
            'embeddable': True
        }
    },
    'urgency': {
        'type': 'int'
    },
    'contents': {
        'type': 'list'
    },
    'groups': {
        'type': 'list'
    },
    'keywords': {
        'type': 'list'
    },
    'subject': {
        'type': 'list'
    },
    'body_html': {
        'type': 'string'
    },
    'renditions': {
        'type': 'dict'
    }
}

superdesk.domain('items', {
    'schema': schema,
    'extra_response_fields': ['headline', 'guid'],
    'item_url': '[-_a-zA-Z0-9]{1,32}',
    'datasource': {
        'backend': 'elastic'
    }
})
