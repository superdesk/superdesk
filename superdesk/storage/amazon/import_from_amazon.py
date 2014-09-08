'''Import from Amazon S3 into Content Archive'''

import superdesk
import json
from superdesk.media.image import get_meta
from eve.utils import ParsedRequest
import xml.etree.ElementTree as etree
from flask.globals import current_app as app
from superdesk.celery_app import celery
from celery import group


class ImportFromAmazonCommand(superdesk.Command):
    """
    Import content from Amazon S3 into content archive.
    """

    max_bucket_size = 50

    option_list = (
        superdesk.Option('--bucket-size', '-s', dest='bucket_size'),
    )

    def run(self, bucket_size=None):
        bucket_size = int(bucket_size) or self.max_bucket_size
        marker = process_bucket(bucket_size=bucket_size)
        while marker:
            marker = process_bucket(bucket_size, marker)
        print('Import completed')


def process_bucket(bucket_size, marker=None):
    print('Retrieving bucket with marker: ', marker)
    rv = app.media.get_bucket_objects(marker=marker)
    keys, marker = extract_keys(rv)
    if not keys:
        return marker
    paged_keys = [keys[i:i + bucket_size] for i in range(0, len(keys), bucket_size)]
    for key_group in paged_keys:
        res = group(import_file.si(key=key) for key in key_group)()
        rv = res.get()
        for value in rv:
            print(value['status'])
    return marker


@celery.task
def import_file(key):
    try:
        if check_if_file_already_imported(key):
            msg = 'File %s already imported' % key
            return {'status': msg}

        file = retrieve_file(key)
        if not file:
            return {'status': 'Failed to retrieve file: ' + key}

        data = [{'media': key, 'media_fetched': file, '_import': True}]
        id = superdesk.apps['archive_media'].create(data, True)
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
    req = ParsedRequest()
    req.args = {'filter': query_filter}
    res = app.data.find('archive', req, None).count()
    return res > 0


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
