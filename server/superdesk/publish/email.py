# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.emails import send_email
from flask import current_app as app
from superdesk.publish import register_transmitter
from superdesk.publish.publish_service import PublishService
from superdesk.errors import PublishEmailError

errors = [PublishEmailError.emailError().get_error_description()]


class EmailPublishService(PublishService):
    """Email Publish Service."""

    def _transmit(self, queue_item, subscriber):
        config = queue_item.get('destination', {}).get('config', {})

        try:
            if not config.get('recipients'):
                raise PublishEmailError.recipientNotFoundError(LookupError('recipient field not found!'))

            admins = app.config['ADMINS']
            recipients = config.get('recipients').rstrip(';').split(';')
            subject = "Story: {}".format(queue_item['item_id'])
            text_body = queue_item['formatted_item']

            # sending email synchronously
            send_email(subject=subject,
                       sender=admins[0],
                       recipients=recipients,
                       text_body=text_body,
                       html_body=None)

        except PublishEmailError:
            raise
        except Exception as ex:
            raise PublishEmailError.emailError(ex, queue_item.get('destination'))

register_transmitter('email', EmailPublishService(), errors)
