# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
from superdesk.metadata.item import Priority


def map_priority(priority):
    """
    Map the IPTC NewsML Priority to Legacy
    :param int priority:
    :return: one character legacy priority
    """
    mapping = {
        Priority.Flash.value: 'f',
        Priority.Urgent.value: 'u',
        Priority.Three_Paragraph.value: 'b'
    }

    return mapping.get(priority, 'r')


def set_subject(category, article):
    """
    Sets the subject code in the odbc_item based on the category, if multiple subject codes are available
    :param category:
    :param article:
    :return:
    """
    subject_reference = None
    # Ensure that there is a subject in the article
    if article.get('subject') and 'qcode' in article['subject'][0]:
        # set the subject reference with the first value, in case we can't do better
        subject_reference = article['subject'][0].get('qcode')
        # we have multiple categories and multiple subjects
        if len(article['subject']) > 1 and category:
            # we need to find a more relevant subject reference if possible
            all_categories = superdesk.get_resource_service('vocabularies').find_one(req=None, _id='categories')
            ref_cat = [cat for cat in all_categories['items'] if
                       cat['qcode'].upper() == category['qcode'].upper()]
            # check if there is an associated subject with the category
            if ref_cat and len(ref_cat) == 1 and 'subject' in ref_cat[0]:
                # try to find the lowest level subject that matches
                ref = 0
                for s in article['subject']:
                    if s['qcode'][:2] == ref_cat[0]['subject'][:2]:
                        if int(s['qcode']) > ref:
                            ref = int(s['qcode'])
                if ref > 0:
                    subject_reference = '{0:0>8}'.format(ref)
    return subject_reference
