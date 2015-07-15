
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license*.

import superdesk
from superdesk.io import Parser
import datetime
from superdesk.utc import utcnow
from pytz import timezone
from superdesk.media.media_operations import process_file_from_stream
from apps.archive.archive_media import generate_guid, GUID_TAG
import io
from flask import current_app as app
import email
from email.header import decode_header
import logging
from superdesk.errors import IngestEmailError
from bs4 import BeautifulSoup, Comment, Doctype
import re
from eve.utils import ParsedRequest


logger = logging.getLogger(__name__)


class UserNotRegisteredException(Exception):
    pass


email_regex = re.compile('^.*<(.*)>$')


def get_user_by_email(field_from):
    email_address = email_regex.findall(field_from)[0]
    lookup = superdesk.get_resource_service('users').find_one(
        req=ParsedRequest(), email=email_address)
    if not lookup:
        raise UserNotRegisteredException()
    return lookup['_id']


class rfc822Parser(Parser):

    def __init__(self):
        self.parser_app = app

    def parse_email(self, data, provider):
        try:
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
                    item['headline'] = self.parse_header(msg['subject'])
                    field_from = self.parse_header(msg['from'])
                    item['original_source'] = field_from
                    try:
                        item['original_creator'] = get_user_by_email(
                            field_from)
                    except UserNotRegisteredException:
                        pass
                    item['guid'] = msg['Message-ID']
                    date_tuple = email.utils.parsedate_tz(msg['Date'])
                    if date_tuple:
                        dt = datetime.datetime.utcfromtimestamp(
                            email.utils.mktime_tz(date_tuple))
                        dt = dt.replace(tzinfo=timezone('utc'))
                        item['firstcreated'] = dt

                    # this will loop through all the available multiparts in mail
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            try:
                                # if we don't know the charset just have a go!
                                if part.get_content_charset() is None:
                                    text_body = body.decode()
                                else:
                                    charset = part.get_content_charset()
                                    text_body = body.decode(charset)
                                continue
                            except Exception as ex:
                                logger.exception(
                                    "Exception parsing text body for {0} "
                                    "from {1}: {2}".format(
                                        item['headline'], field_from),
                                    ex)
                                continue
                        if part.get_content_type() == "text/html":
                            body = part.get_payload(decode=True)
                            try:
                                if part.get_content_charset() is None:
                                    html_body = body.decode()
                                else:
                                    charset = part.get_content_charset()
                                    html_body = body.decode(charset)
                                html_body = self.safe_html(html_body)
                                continue
                            except Exception as ex:
                                logger.exception(
                                    "Exception parsing text html for {0} "
                                    "from {1}: {2}".format(
                                        item['headline'], field_from),
                                    ex)
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
                            if content_type == 'image/gif' or content_type == 'image/png':
                                continue
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
                                comp_item['headline'] = item['headline']
                                comp_item['groups'] = []
                                comp_item['original_source'] = item['original_source']
                                if 'original_creator' in item:
                                    comp_item['original_creator'] = item['original_creator']

                                # create a reference to the item that stores the body of the email
                                item_ref = {}
                                item_ref['guid'] = item['guid']
                                item_ref['residRef'] = item['guid']
                                item_ref['headline'] = item['headline']
                                item_ref['location'] = 'ingest'
                                item_ref['itemClass'] = 'icls:text'
                                item_ref['original_source'] = item['original_source']
                                if 'original_creator' in item:
                                    item_ref['original_creator'] = item['original_creator']
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
                            media_item['original_source'] = item['original_source']
                            if 'original_creator' in item:
                                media_item['original_creator'] = item['original_creator']
                            new_items.append(media_item)

                            # add a reference to this item in the composite item
                            media_ref = {}
                            media_ref['guid'] = media_item['guid']
                            media_ref['residRef'] = media_item['guid']
                            media_ref['headline'] = fileName
                            media_ref['location'] = 'ingest'
                            media_ref['itemClass'] = 'icls:picture'
                            media_ref['original_source'] = item['original_source']
                            if 'original_creator' in item:
                                media_ref['original_creator'] = item['original_creator']
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
        except Exception as ex:
            raise IngestEmailError.emailParseError(ex, provider)

    def parse_header(self, field):
        try:
            hdr = decode_header(field)
            encoding = hdr[0][1]
            if encoding and hdr:
                parsed_field = hdr[0][0].decode(encoding)
            else:
                parsed_field = hdr[0][0]
        except:
            try:
                parsed_field = str(field)
            except:
                parsed_field = 'Unknown'
            pass
        return parsed_field

    # from http://chase-seibert.github.io/blog/2011/01/28/sanitize-html-with-beautiful-soup.html
    def safe_html(self, html):
        if not html:
            return None

        # remove these tags, complete with contents.
        blacklist = ["script", "style", "head"]

        whitelist = [
            "div", "span", "p", "br", "pre",
            "table", "tbody", "thead", "tr", "td", "a",
            "blockquote",
            "ul", "li", "ol",
            "b", "em", "i", "strong", "u", "font"
        ]

        try:
            # BeautifulSoup is catching out-of-order and unclosed tags, so markup
            # can't leak out of comments and break the rest of the page.
            soup = BeautifulSoup(html)
        except Exception as e:
            # special handling?
            raise e

        # remove the doctype declaration if present
        if isinstance(soup.contents[0], Doctype):
            soup.contents[0].extract()

        # now strip HTML we don't like.
        for tag in soup.findAll():
            if tag.name.lower() in blacklist:
                # blacklisted tags are removed in their entirety
                tag.extract()
            elif tag.name.lower() in whitelist:
                # tag is allowed. Make sure the attributes are allowed.
                attrs = dict(tag.attrs)
                for a in attrs:
                    if self._attr_name_whitelisted(a):
                        tag.attrs[a] = [self.safe_css(a, tag.attrs[a])]
                    else:
                        del tag.attrs[a]
            else:
                tag.replaceWithChildren()

        # scripts can be executed from comments in some cases
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

        safe_html = str(soup)

        if safe_html == ", -":
            return None

        return safe_html.replace('</br>', '').replace('<br>', '<br/>')

    def _attr_name_whitelisted(self, attr_name):
        return attr_name.lower() in ["href", "style", "color", "size", "bgcolor", "border"]

    def safe_css(self, attr, css):
        if attr == "style":
            return re.sub("(width|height):[^;]+;", "", css)
        return css
