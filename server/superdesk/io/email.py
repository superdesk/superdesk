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
from superdesk.upload import url_for_media
from superdesk.errors import IngestEmailError

from superdesk.io.rfc822 import rfc822Parser


class EmailReaderService(IngestService):

    PROVIDER = 'email'

    ERRORS = [IngestEmailError.emailError().get_error_description(),
              IngestEmailError.emailLoginError().get_error_description()]

    def __init__(self):
        self.parser = rfc822Parser()

    def _update(self, provider):
        config = provider.get('config', {})
        server = config.get('server', '')
        port = int(config.get('port', 993))

        try:
            imap = imaplib.IMAP4_SSL(host=server, port=port)
            try:
                imap.login(config.get('user', None), config.get('password', None))
            except imaplib.IMAP4.error:
                raise IngestEmailError.emailLoginError(imaplib.IMAP4.error, provider)

            rv, data = imap.select(config.get('mailbox', None), readonly=False)
            if rv == 'OK':
                rv, data = imap.search(None, config.get('filter', None))
                if rv == 'OK':
                    new_items = []
                    for num in data[0].split():
                        rv, data = imap.fetch(num, '(RFC822)')
                        if rv == 'OK':
                            try:
                                new_items.append(self.parser.parse_email(data, provider))
                            except IngestEmailError:
                                continue
                imap.close()
            imap.logout()
        except IngestEmailError:
            raise
        except Exception as ex:
            raise IngestEmailError.emailError(ex, provider)
        return new_items

    def prepare_href(self, href):
        return url_for_media(href)
