'''Import from Amazon S3 into Content Archive'''

import superdesk
import json
from superdesk.file_meta.image import get_meta
from eve.utils import ParsedRequest
import xml.etree.ElementTree as etree
from flask.globals import current_app as app
from superdesk.celery_app import celery
from celery import group


class ImportFromAmazonCommand(superdesk.Command):
    """
    Import content from Amazon S3 into content archive.
    """

    def run(self):
        marker = process_bucket()
        while marker:
            marker = process_bucket(marker)
        print('Import completed')


def process_bucket(marker=None):
    print('Retrieving bucket with marker: ', marker)
    rv = app.media.get_bucket_objects(marker=marker)
    keys, marker = extract_keys(rv)
    if not keys:
        return marker
    res = group(import_file.si(key=key) for key in keys)()
    rv = res.get()
    for value in rv:
        print(value['status'])
    return marker


@celery.task
def import_file(key):
    try:
        if check_if_file_already_imported(key):
            return {'status': 'File %s already imported' % key}

        file = retrieve_file(key)
        if not file:
            return {'status': 'Failed to retrieve file: ' + key}

        data = [{'media': key, 'media_fetched': file, '_import': True}]
        id = app.data.insert('archive_media', data)
        return {'status': 'Imported file %s to archive media with id= %s' % (key, id)}
    except Exception as ex:
        return {'status': ex}


def retrieve_file(key):
    file = app.media.get(key)
    if file and not file.metadata:
        metadata = get_meta(file)
        if metadata:
            metadata['content-type'] = file.content_type
            file.metadata = metadata
            app.media.update_metadata(key, metadata)
        file.seek(0)
    return file


def extract_keys(xml_content):
    rv = etree.fromstring(xml_content)
    namespace = ''
    if rv.tag[0] == '{':
        uri, tag = rv.tag[0:].split('}')
        namespace = uri + '}'
    keys = [key.text for key in rv.iter(namespace + 'Key')]
    truncated = rv.find(namespace + 'IsTruncated')
    marker = None
    if keys and json.loads(truncated.text):
        marker = keys[-1]
    return keys, marker


def check_if_file_already_imported(key):
    query_filter = get_query_for_already_imported(key)
    with app.test_request_context('?filter=' + query_filter):
        req = ParsedRequest()
        res = app.data.find('archive_media', req, None).count()
        return res > 0
    return False


def get_query_for_already_imported(file_id):
    query = {'bool':
             {'should':
              [{'term': {'archive.media': file_id}},
               {'term': {'archive.renditions.baseImage.media': file_id}},
               {'term': {'archive.renditions.original.media': file_id}},
               {'term': {'archive.renditions.thumbnail.media': file_id}},
               {'term': {'archive.renditions.viewImage.media': file_id}}]}
             }
    return json.dumps(query)
