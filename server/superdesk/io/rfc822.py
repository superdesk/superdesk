
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license*.

from superdesk.io import Parser
import datetime
from superdesk.utc import utcnow
from pytz import timezone
from superdesk.media.media_operations import process_file_from_stream
from apps.archive.archive_media import generate_guid, GUID_TAG
import io
from flask import current_app as app
import email


class rfc822Parser(Parser):

    def __init__(self):
        self.parser_app = app

    def parse_email(self, data):
        new_items = []
        # create an item for the body text of the email
        # either text or html
        item = dict()
        item['type'] = 'text'
        item['versioncreated'] = utcnow()

        comp_item = None

        # a list to keep the references to the attachments
        refs = []

        html_body = None
        text_body = None

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                item['headline'] = msg['subject']
                item['original_creator'] = msg['from']
                item['guid'] = msg['Message-ID']
                date_tuple = email.utils.parsedate_tz(msg['Date'])
                if date_tuple:
                    dt = datetime.datetime.utcfromtimestamp(email.utils.mktime_tz(date_tuple))
                    dt = dt.replace(tzinfo=timezone('utc'))
                    item['firstcreated'] = dt

                # this will loop through all the available multiparts in mail
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        text_body = body.decode('utf-8')
                        continue
                    if part.get_content_type() == "text/html":
                        body = part.get_payload(decode=True)
                        html_body = body.decode('utf-8')
                        continue
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    # we are only going to pull off image attachments at this stage
                    if part.get_content_maintype() != 'image':
                        continue

                    fileName = part.get_filename()
                    if bool(fileName):
                        image = part.get_payload(decode=True)
                        content = io.BytesIO(image)
                        res = process_file_from_stream(content, part.get_content_type())
                        file_name, content_type, metadata = res
                        content.seek(0)
                        image_id = self.parser_app.media.put(content, filename=fileName,
                                                             content_type=content_type, metadata=metadata)
                        renditions = {'baseImage': {'href': image_id}}

                        # if we have not got a composite item then create one
                        if not comp_item:
                            comp_item = dict()
                            comp_item['type'] = 'composite'
                            comp_item['guid'] = generate_guid(type=GUID_TAG)
                            comp_item['versioncreated'] = utcnow()
                            comp_item['groups'] = []
                            comp_item['headline'] = msg['subject']
                            comp_item['groups'] = []

                            # create a reference to the item that stores the body of the email
                            item_ref = {}
                            item_ref['guid'] = item['guid']
                            item_ref['residRef'] = item['guid']
                            item_ref['headline'] = msg['subject']
                            item_ref['location'] = 'ingest'
                            item_ref['itemClass'] = 'icls:text'
                            refs.append(item_ref)

                        media_item = dict()
                        media_item['guid'] = generate_guid(type=GUID_TAG)
                        media_item['versioncreated'] = utcnow()
                        media_item['type'] = 'picture'
                        media_item['renditions'] = renditions
                        media_item['mimetype'] = content_type
                        media_item['filemeta'] = metadata
                        media_item['slugline'] = fileName
                        if text_body is not None:
                            media_item['body_html'] = text_body
                        media_item['headline'] = item['headline']
                        new_items.append(media_item)

                        # add a reference to this item in the composite item
                        media_ref = {}
                        media_ref['guid'] = media_item['guid']
                        media_ref['residRef'] = media_item['guid']
                        media_ref['headline'] = fileName
                        media_ref['location'] = 'ingest'
                        media_ref['itemClass'] = 'icls:picture'
                        refs.append(media_ref)

        if html_body is not None:
            item['body_html'] = html_body
        else:
            item['body_html'] = text_body
            item['type'] = 'preformatted'

        # if there is composite item then add the main group and references
        if comp_item:
            grefs = {}
            grefs['refs'] = [{'idRef': 'main'}]
            grefs['id'] = 'root'
            grefs['role'] = 'grpRole:NEP'
            comp_item['groups'].append(grefs)

            grefs = {}
            grefs['refs'] = refs
            grefs['id'] = 'main'
            grefs['role'] = 'grpRole:Main'
            comp_item['groups'].append(grefs)

            new_items.append(comp_item)

        new_items.append(item)
        return new_items
