# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import imaplib
from .ingest_service import IngestService
from superdesk.io import register_provider
from superdesk.upload import url_for_media

from superdesk.io.rfc822 import rfc822Parser

PROVIDER = 'email'


class EmailReaderService(IngestService):

    def __init__(self):
        self.parser = rfc822Parser()

    def _update(self, provider):
        server = provider.get('config', {}).get('server', None)
        if not server:
            server = ''
        port = provider.get('config', {}).get('port', None)
        if not port:
            port = 993

        Imap = imaplib.IMAP4_SSL(host=server, port=port)
        try:
            Imap.login(provider.get('config', {}).get('user', None), provider.get('config', {}).get('password', None))
        except imaplib.IMAP4.error:
            return

        rv, data = Imap.select(provider.get('config', {}).get('mailbox', None), readonly=False)
        if rv == 'OK':
            rv, data = Imap.search(None, provider.get('config', {}).get('filter', None))
            if rv == 'OK':
                new_items = []
                for num in data[0].split():
                    rv, data = Imap.fetch(num, '(RFC822)')
                    if rv == 'OK':
                        new_items.append(self.parser.parse_email(data))
            Imap.close()
        Imap.logout()
        return new_items

    def prepare_href(self, href):
        return url_for_media(href)

register_provider(PROVIDER, EmailReaderService())
