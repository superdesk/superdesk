# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

''' Amazon media storage module'''
from eve.io.media import MediaStorage
import logging
import json
from io import BytesIO
import boto3

logger = logging.getLogger(__name__)


class AmazonObjectWrapper(BytesIO):

    def __init__(self, s3_object, name, metadata):
        super().__init__()

        s3_body = s3_object['Body']
        blocksize = 65636
        buf = s3_body.read(amt=blocksize)
        while len(buf) > 0:
            self.write(buf)
            buf = s3_body.read(amt=blocksize)

        self.seek(0)
        self.content_type = s3_object['ContentType']
        self.length = int(s3_object['ContentLength'])
        self.name = name
        self.metadata = metadata
        self.upload_date = s3_object['LastModified']
        self.md5 = s3_object['ETag'][1:-1]


class AmazonMediaStorage(MediaStorage):

    def __init__(self, app=None):
        super().__init__(app)
        username, api_key = self.read_from_config()
        self.client = boto3.client('s3',
                                   aws_access_key_id=username,
                                   aws_secret_access_key=api_key,
                                   region_name=self.region)
        self.user_metadata_header = 'x-amz-meta-'

    def url_for_media(self, media_id):
        if not self.app.config.get('AMAZON_SERVE_DIRECT_LINKS', False):
            return None
        protocol = 'https' if self.app.config.get('AMAZON_S3_USE_HTTPS', False) else 'http'
        endpoint = 's3-%s.amazonaws.com' % self.region
        return '%s://%s.%s/%s' % (protocol, self.container_name, endpoint, media_id)

    def read_from_config(self):
        self.region = self.app.config.get('AMAZON_REGION', 'us-east-1') or 'us-east-1'
        username = self.app.config['AMAZON_ACCESS_KEY_ID']
        api_key = self.app.config['AMAZON_SECRET_ACCESS_KEY']
        self.container_name = self.app.config['AMAZON_CONTAINER_NAME']
        return username, api_key

    def get(self, id_or_filename, resource=None):
        """ Opens the file given by name or unique id. Note that although the
        returned file is guaranteed to be a File object, it might actually be
        some subclass. Returns None if no file was found.
        """
        id_or_filename = str(id_or_filename)
        try:
            obj = self.client.get_object(Key=id_or_filename, Bucket=self.container_name)
            if obj:
                metadata = self.extract_metadata_from_headers(obj['Metadata'])
                return AmazonObjectWrapper(obj, id_or_filename, metadata)
        except:
            return None
        return None

    def extract_metadata_from_headers(self, request_headers):
        headers = {}
        for key, value in request_headers.items():
            if self.user_metadata_header in key:
                new_key = key.split(self.user_metadata_header)[1]
                if(value):
                    try:
                        headers[new_key] = json.loads(value)
                    except Exception as ex:
                        logger.exception(ex)
        return headers

    def transform_metadata_to_amazon_format(self, metadata):
        if not metadata:
            return {}
        file_metadata = {}
        for key, value in metadata.items():
            new_key = self.user_metadata_header + key
            file_metadata[new_key] = value
        return file_metadata

    def put(self, content, filename=None, content_type=None, resource=None, metadata=None):
        """ Saves a new file using the storage system, preferably with the name
        specified. If there already exists a file with this name name, the
        storage system may modify the filename as necessary to get a unique
        name. Depending on the storage system, a unique id or the actual name
        of the stored file will be returned. The content type argument is used
        to appropriately identify the file when it is retrieved.
        """
        logger.debug('Going to save media file with %s ' % filename)
        found = self._check_exists(filename)
        if found:
            return filename

        try:
            file_metadata = self.transform_metadata_to_amazon_format(metadata)
            self.client.put_object(Key=filename, Body=content, Bucket=self.container_name,
                                   ContentType=content_type, Metadata=file_metadata)
            return filename
        except Exception as ex:
            logger.exception(ex)
            raise

    def delete(self, id_or_filename, resource=None):
        id_or_filename = str(id_or_filename)
        del_res = self.client.delete_object(Key=id_or_filename, Bucket=self.container_name)
        logger.debug('Amazon S3 file deleted %s with status' % id_or_filename, del_res)

    def exists(self, id_or_filename, resource=None):
        """ Returns True if a file referenced by the given name or unique id
        already exists in the storage system, or False if the name is available
        for a new file.
        """
        id_or_filename = str(id_or_filename)
        found = self._check_exists(id_or_filename)
        return found

    def _check_exists(self, id_or_filename):
        try:
            self.client.head_object(Key=id_or_filename, Bucket=self.container_name)
            return True
        except Exception:
            # File not found
            return False
