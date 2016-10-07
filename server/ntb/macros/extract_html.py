# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2016 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from bs4 import BeautifulSoup


def extract_html_macro(item, **kwargs):
    """
        Delete from body_html all html tags except links
    """
    if 'body_html' not in item:
        return None

    soup = BeautifulSoup(item['body_html'], "html.parser")

    links = {}
    count = 0
    # extract all links and add them to a dictionary with a unique
    # generated key for every link
    for a in soup.findAll('a'):
        links['__##link' + str(count) + '##__'] = str(a)
        count = count + 1

    # replace all text links with the generated keys
    # regenerate html back from soup in order to avoid issues
    # on link replacements where are used text links generated from soup
    body_html = str(soup)
    for link in links:
        body_html = body_html.replace(links[link], link)
    body_html = body_html.replace('<p>', '')
    body_html = body_html.replace('</p>', '__##br##__')
    body_html = body_html.replace('<br>', '__##br##__')

    # extract text from the html that don't contains any link,
    # it just contains link keys that are not affected by text extraction
    # because they are already text
    soup = BeautifulSoup(body_html, "html.parser")
    body_html = soup.text

    # in extracted text replace the link keys with links
    for link in links:
        body_html = body_html.replace(link, links[link])

    body_html = body_html.replace('__##br##__', '<br>')
    item['body_html'] = '<p>' + body_html + '</p>'
    return item


name = 'Extract Html Macro'
label = 'Extract Html Macro'
callback = extract_html_macro
access_type = 'frontend'
action_type = 'direct'
