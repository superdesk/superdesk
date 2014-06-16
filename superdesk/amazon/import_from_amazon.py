'''Import from Amazon S3 into Content Archive'''

import superdesk
import json
from superdesk.file_meta.image import get_meta
from eve.utils import ParsedRequest
import xml.etree.ElementTree as etree
from flask.globals import current_app as app


class ImportFromAmazonCommand(superdesk.Command):
    """
    Import content from Amazon S3 into content archive.
    """

    def run(self):
        self.marker = None
        self.process_bucket()
        while self.marker:
            self.process_bucket()
        print('Import completed')

    def process_bucket(self):
        rv = app.media.get_bucket_objects(marker=self.marker)
        keys = self.extract_keys(rv)
        print('Marker for next bucket is %s' % self.marker)
        for key in keys:
            self.import_file(key)

    def import_file(self, key):
        if self.check_if_file_already_imported(key):
            print('File %s already imported' % key)
            return

        file = self.retrieve_file(key)
        if not file:
            print('Failed to retrieve file: %s' % key)
            return

        data = [{'media': key, 'media_fetched': file, '_import': True}]
        id = app.data.insert('archive_media', data)
        print('Imported file %s to archive media with id= %s' % (key, id))

    def retrieve_file(self, key):
        file = app.media.get(key)
        if file and not file.metadata:
            metadata = get_meta(file)
            if metadata:
                metadata['content-type'] = file.content_type
                file.metadata = metadata
                app.media.update_metadata(key, metadata)
            file.seek(0)
        return file

    def extract_keys(self, xml_content):
        rv = etree.fromstring(xml_content)
        namespace = ''
        if rv.tag[0] == '{':
            uri, tag = rv.tag[0:].split('}')
            namespace = uri + '}'
        keys = [key.text for key in rv.iter(namespace + 'Key')]
        truncated = rv.find(namespace + 'IsTruncated')
        if keys and json.loads(truncated.text):
            self.marker = keys[-1]
        return keys

    def check_if_file_already_imported(self, key):
        query_filter = self.get_query_for_already_imported(key)
        with app.test_request_context('?filter=' + query_filter):
            req = ParsedRequest()
            res = app.data.find('archive_media', req, None).count()
            return res > 0
        return False

    def get_query_for_already_imported(self, file_id):
        query = {'bool':
                 {'should':
                  [{'term': {'archive.media': file_id}},
                   {'term': {'archive.renditions.baseImage.media': file_id}},
                   {'term': {'archive.renditions.original.media': file_id}},
                   {'term': {'archive.renditions.thumbnail.media': file_id}},
                   {'term': {'archive.renditions.viewImage.media': file_id}}]}
                 }
        return json.dumps(query)
