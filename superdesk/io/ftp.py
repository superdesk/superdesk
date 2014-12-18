
import ftplib
import tempfile
from datetime import datetime
from superdesk.utc import utc
from superdesk.etree import etree
from superdesk.io import get_xml_parser, register_provider
from .ingest_service import IngestService

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class FTPService(IngestService):
    """FTP Ingest Service."""

    DATE_FORMAT = '%Y%m%d%H%M%S'
    FILE_SUFFIX = '.xml'

    def configFromURL(self, url):
        """Parse given url into ftp config.

        :param url: url in form `ftp://username:password@host:port/dir`
        """
        url_parts = urlparse(url)
        return {
            'username': url_parts.username,
            'password': url_parts.password,
            'host': url_parts.hostname,
            'path': url_parts.path.lstrip('/'),
        }

    def _update(self, provider):
        config = provider.get('config', {})
        last_updated = provider.get('last_updated')

        if 'dest_path' not in config:
            config['dest_path'] = tempfile.mkdtemp(prefix='superdesk_ingest_')

        items = []
        with ftplib.FTP(config.get('host')) as ftp:
            ftp.login(config.get('username'), config.get('password'))
            ftp.cwd(config.get('path', ''))

            for filename, facts in ftp.mlsd():
                if not filename.endswith(self.FILE_SUFFIX):
                    continue

                if last_updated:
                    item_last_updated = datetime.strptime(facts['modify'], self.DATE_FORMAT).replace(tzinfo=utc)
                    if item_last_updated < last_updated:
                        continue

                dest = '%s/%s' % (config['dest_path'], filename)

                try:
                    with open(dest, 'xb') as f:
                        ftp.retrbinary('RETR %s' % filename, f.write)
                except FileExistsError:
                    continue

                xml = etree.parse(dest).getroot()
                items.append(get_xml_parser(xml).parse_message(xml))
        return items


register_provider('ftp', FTPService())
