
from superdesk.resource import Resource
from apps.content import metadata_schema
from apps.archive.common import item_url
from apps.archive.archive import SOURCE as ARCHIVE
from apps.archive import ArchiveVersionsResource


class PackageVersionsResource(ArchiveVersionsResource):
    """
    Resource class for versions of archive_media
    """

    datasource = {
        'source': ARCHIVE + '_versions',
        'filter': {'type': 'composite'}
    }


class PackageResource(Resource):
    '''
    Package schema
    '''
    datasource = {
        'source': ARCHIVE,
        'default_sort': [('_updated', -1)],
        'filter': {'type': 'composite'},
        'elastic_filter': {'term': {'archive.type': 'composite'}}  # eve-elastic specific filter
    }
    item_url = item_url
    item_methods = ['GET', 'PATCH']

    schema = {}
    schema.update(metadata_schema)
    schema.update({
        'type': {
            'type': 'string',
            'readonly': True,
            'default': 'composite'
        },
        'groups': {
            'type': 'list',
            'minlength': 1
        },
        'profile': {
            'type': 'string'
        }
    })

    versioning = True
    privileges = {'POST': 'archive', 'PATCH': 'archive'}
