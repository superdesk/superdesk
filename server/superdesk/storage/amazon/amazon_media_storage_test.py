import unittest
from .amazon_media_storage import AmazonMediaStorage


class AmazonMediaStorageTestCase(unittest.TestCase):

    def test_url_for_media(self):
        import settings
        # create a dummy app containing only the settings
        app = type('MyObject', (object,), {})
        setattr(app, 'config', settings.__dict__)
        media_id = '123'
        # set s3 settings and test the output
        app.config['AMAZON_CONTAINER_NAME'] = 'AMAZON_CONTAINER_NAME'
        app.config['AMAZON_S3_USE_HTTPS'] = True
        app.config['AMAZON_SERVE_DIRECT_LINKS'] = True
        self.assertEquals(AmazonMediaStorage(app).url_for_media(media_id),
                          'https://AMAZON_CONTAINER_NAME.s3-us-east-1.amazonaws.com/%s' % (media_id))
        app.config['AMAZON_S3_USE_HTTPS'] = False
        self.assertEquals(AmazonMediaStorage(app).url_for_media(media_id),
                          'http://AMAZON_CONTAINER_NAME.s3-us-east-1.amazonaws.com/%s' % (media_id))
        app.config['AMAZON_REGION'] = 'eu-west-1'
        self.assertEquals(AmazonMediaStorage(app).url_for_media(media_id),
                          'http://AMAZON_CONTAINER_NAME.s3-eu-west-1.amazonaws.com/%s' % (media_id))
