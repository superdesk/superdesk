from superdesk.activity import add_activity, ACTIVITY_CREATE, ACTIVITY_DELETE
from superdesk.services import BaseService
from superdesk.utils import is_hashed, get_hash
from superdesk import get_resource_service, SuperdeskError
from flask import current_app as app
from superdesk.emails import send_user_status_changed_email, send_activate_account_email
from superdesk.utc import utcnow
from eve.validation import ValidationError

import logging


logger = logging.getLogger(__name__)


def get_display_name(user):
    if user.get('first_name') or user.get('last_name'):
        display_name = '%s %s' % (user.get('first_name', ''), user.get('last_name', ''))
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
            add_activity(ACTIVITY_CREATE, 'created user {{user}}',
                         user=user_doc.get('display_name', user_doc.get('username')))

    def on_updated(self, updates, user):
        self.handle_status_changed(updates, user)

    def handle_status_changed(self, updates, user):
        status = updates.get('is_active', None)
        if status is not None and status != self.user_is_active(user):
            if not status:
                # remove active tokens
                get_resource_service('auth').delete_action({'username': user.get('username')})
            # send email notification
            send_email = get_resource_service('preferences').email_notification_is_enabled(user['_id'])
            if send_email:
                send_user_status_changed_email([user['email']], status)

    def on_deleted(self, doc):
        add_activity(ACTIVITY_DELETE, 'removed user {{user}}', user=doc.get('display_name', doc.get('username')))

    def on_fetched(self, document):
        for doc in document['_items']:
            self.update_user_defaults(doc)

    def update_user_defaults(self, doc):
        """Set default fields for users"""
        doc.setdefault('display_name', get_display_name(doc))
        doc.pop('password', None)

    def user_is_waiting_activation(self, doc):
        return doc.get('needs_activation', False)

    def user_is_active(self, doc):
        return doc.get('is_active', False)


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
        activate_ttl = app.config['ACTIVATE_ACCOUNT_TOKEN_TIME_TO_LIVE']
        for doc in docs:
            if self.user_is_waiting_activation(doc):
                tokenDoc = {'user': doc['_id'], 'email': doc['email']}
                id = resetService.store_reset_password_token(tokenDoc, doc['email'], activate_ttl, doc['_id'])
                if not id:
                    raise SuperdeskError('Failed to send account activation email.')
                tokenDoc.update({'username': doc['username']})
                send_activate_account_email(tokenDoc)

    def on_update(self, updates, user):
        if updates.get('first_name') or updates.get('last_name'):
            updated_user = {'first_name': user.get('first_name', ''),
                            'last_name': user.get('last_name', ''),
                            'username': user.get('username', '')}
            if updates.get('first_name'):
                updated_user['first_name'] = updates.get('first_name')
            if updates.get('last_name'):
                updated_user['last_name'] = updates.get('last_name')
            updates['display_name'] = get_display_name(updated_user)

    def update_password(self, user_id, password):
        """
        Update the user password.
        Returns true if successful.
        """
        user = self.find_one(req=None, _id=user_id)

        if not user:
            raise SuperdeskError(payload='Invalid user.')

        if not self.user_is_active(user):
            raise SuperdeskError(status_code=403, message='Updating password is forbidden.')

        updates = {}
        updates['password'] = get_hash(password, app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))
        updates[app.config['LAST_UPDATED']] = utcnow()
        if self.user_is_waiting_activation(user):
            updates['needs_activation'] = False

        self.patch(user_id, updates=updates)


class ADUsersService(UsersService):
    """
    Service class for UsersResource and should be used when AD is active.
    """

    readonly_fields = ['username', 'display_name', 'password', 'email', 'phone', 'first_name', 'last_name']

    def on_fetched(self, doc):
        super().on_fetched(doc)
        for document in doc['_items']:
            document['_readonly'] = ADUsersService.readonly_fields

    def on_fetched_item(self, doc):
        super().update_user_defaults(doc)
        doc['_readonly'] = ADUsersService.readonly_fields


class RolesService(BaseService):

    def on_update(self, updates, original):
        if updates.get('extends'):
            if updates.get('extends') == original.get('_id'):
                raise ValidationError('A role can not extend its self')
            self.check_parents(original.get('_id'), updates.get('extends'))

    def check_parents(self, myid, parentid):
        parent = self.find_one(req=None, _id=parentid)
        if parent:
            if parent['_id'] == myid:
                raise ValidationError('Circular role inheritance')
            self.check_parents(myid, parent.get('extends'))
