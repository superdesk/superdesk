from superdesk.activity import add_activity
from superdesk.services import BaseService
from superdesk.utils import is_hashed, get_hash
from superdesk import get_resource_service, SuperdeskError
from flask import current_app as app, render_template
from settings import ADMINS, ACTIVATE_ACCOUNT_TOKEN_TIME_TO_LIVE as activate_ttl, CLIENT_URL
from superdesk.emails import send_email
from .users import UsersResource
from superdesk.utc import utcnow


import logging


logger = logging.getLogger(__name__)


def get_display_name(user):
    if user.get('first_name') or user.get('last_name'):
        display_name = '%s %s' % (user.get('first_name'), user.get('last_name'))
        return display_name.strip()
    else:
        return user.get('username')


class UsersService(BaseService):

    def on_create(self, docs):
        for user_doc in docs:
            user_doc.setdefault('display_name', get_display_name(user_doc))

    def on_created(self, docs):
        for user_doc in docs:
            self.update_user_defaults(user_doc)
            add_activity('created user {{user}}', user=user_doc.get('display_name', user_doc.get('username')))

    def on_updated(self, updates, user):
        self.handle_status_changed(updates, user)

    def handle_status_changed(self, updates, user):
        status = updates.get('status', None)
        if status and status != user.get('status', UsersResource.active):
            if status == UsersResource.inactive:
                # remove active tokens
                get_resource_service('auth').delete_action({'username': user.get('username')})
            # send email notification
            send_email = get_resource_service('preferences').email_notification_is_enabled(user['_id'])
            if send_email:
                self._send_user_status_changed_email([user['email']], status)

    def _send_user_status_changed_email(self, recipients, status):
        send_email.delay(subject='Your Superdesk account is %s' % status,
                         sender=ADMINS[0],
                         recipients=recipients,
                         text_body=render_template("account_status_changed.txt", status=status),
                         html_body=render_template("account_status_changed.html", status=status))

    def on_deleted(self, doc):
        add_activity('removed user {{user}}', user=doc.get('display_name', doc.get('username')))

    def on_fetched(self, document):
        for doc in document['_items']:
            self.update_user_defaults(doc)

    def update_user_defaults(self, doc):
        """Set default fields for users"""
        doc.setdefault('display_name', get_display_name(doc))
        doc.pop('password', None)


class DBUsersService(UsersService):
    """
    Service class for UsersResource and should be used when AD is inactive.
    """

    def on_create(self, docs):
        super().on_create(docs)
        for doc in docs:
            if doc.get('password', None) and not is_hashed(doc.get('password')):
                doc['password'] = get_hash(doc.get('password'), app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))

    def on_created(self, docs):
        """Send email to user with reset password token."""
        super().on_created(docs)
        resetService = get_resource_service('reset_user_password')
        for doc in docs:
            if doc['status'] == UsersResource.needs_activation:
                tokenDoc = {'user': doc['_id'], 'email': doc['email']}
                id = resetService.store_reset_password_token(tokenDoc, doc['email'], activate_ttl)
                if not id:
                    raise SuperdeskError('Failed to send account activation email.')
                self._send_activate_account_email(tokenDoc)

    def user_is_waiting_activation(self, doc):
        return doc['status'] == UsersResource.needs_activation

    def update_password(self, user_id, password):
        """
        Update the user password.
        Returns true if successful.
        """
        user = self.find_one(req=None, _id=user_id)
        if not user:
            raise SuperdeskError(payload='Invalid user.')

        updates = {}
        updates['password'] = get_hash(password, app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))
        updates[app.config['LAST_UPDATED']] = utcnow()
        if self.user_is_waiting_activation(user):
            updates['status'] = UsersResource.active

        self.patch(user_id, updates=updates)

    def _send_activate_account_email(self, doc):
        url = '{}/#/reset-password?token={}'.format(CLIENT_URL, doc['token'])
        hours = activate_ttl * 24
        text_body = render_template("account_created.txt", email=doc['email'], expires=hours, url=url)
        html_body = render_template("account_created.html", email=doc['email'], expires=hours, url=url)
        send_email.delay(subject='Superdesk account created', sender=ADMINS[0], recipients=[doc['email']],
                         text_body=text_body, html_body=html_body)


class ADUsersService(UsersService):
    """
    Service class for UsersResource and should be used when AD is active.
    """

    readonly_fields = ['username', 'display_name', 'password', 'email', 'phone', 'first_name', 'last_name']

    def on_fetched(self, doc):
        super().on_fetched(doc)
        for document in doc['_items']:
            document['_readonly'] = ADUsersService.readonly_fields
