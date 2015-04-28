# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import flask
import logging
from flask import current_app as app
from superdesk.activity import add_activity, ACTIVITY_CREATE, ACTIVITY_UPDATE
from superdesk.services import BaseService
from superdesk.utils import is_hashed, get_hash
from superdesk import get_resource_service
from superdesk.emails import send_user_status_changed_email, send_activate_account_email
from superdesk.utc import utcnow
from superdesk.privilege import get_privilege_list
from superdesk.errors import SuperdeskApiError
from apps.auth.errors import UserInactiveError


logger = logging.getLogger(__name__)


def get_display_name(user):
    if user.get('first_name') or user.get('last_name'):
        display_name = '%s %s' % (user.get('first_name', ''), user.get('last_name', ''))
        return display_name.strip()
    else:
        return user.get('username')


def is_admin(user):
    """Test if given user is admin.

    :param user
    """
    return user.get('user_type', 'user') == 'administrator'


def get_admin_privileges():
    """Get privileges for admin user."""
    return dict.fromkeys([p['name'] for p in get_privilege_list()], 1)


def get_privileges(user, role):
    """Get privileges for given user and role.

    :param user
    :param role
    """
    if is_admin(user):
        return get_admin_privileges()

    if role:
        role_privileges = role.get('privileges', {})
        return dict(
            list(role_privileges.items()) + list(user.get('privileges', {}).items())
        )

    return user.get('privileges', {})


def current_user_has_privilege(privilege):
    """Test if current user has given privilege.

    In case there is no current user we assume it's system (via worker/manage.py)
    and let it pass.

    :param privilege
    """
    if not getattr(flask.g, 'user', None):  # no user - worker can do it
        return True
    privileges = get_privileges(flask.g.user, getattr(flask.g, 'role', None))
    return privileges.get(privilege, False)


def is_sensitive_update(updates):
    """Test if given update is sensitive and might change user privileges."""
    return 'role' in updates or 'privileges' in updates or 'user_type' in updates


def get_invisible_stages(user):
    user_desks = get_resource_service('user_desks').get(req=None, lookup={'user_id': user['_id']})
    user_desk_ids = [d['_id'] for d in user_desks]
    return get_resource_service('stages').get_stages_by_visibility(False, user_desk_ids)


class UsersService(BaseService):

    def __is_invalid_operation(self, user, updates, method):
        """
        Checks if the requested 'PATCH' or 'DELETE' operation is Invalid.
        Operation is invalid if one of the below is True:
            1. Check if the user is updating his/her own status.
            2. Check if the user is changing the changing role/user_type/privileges of other logged-in users.
            3. A user without 'User Management' privilege is changing status/role/user_type/privileges

        :return: error message if invalid.
        """

        if 'user' in flask.g:
            if method == 'PATCH':
                if ('is_active' in updates or 'is_enabled' in updates):
                    if str(user['_id']) == str(flask.g.user['_id']):
                        return 'Not allowed to change your own status'
                    elif not current_user_has_privilege('users'):
                        return 'Insufficient privileges to change user state'
                if str(user['_id']) != str(flask.g.user['_id']) and user.get('session_preferences') \
                        and is_sensitive_update(updates):
                    return 'Not allowed to change the role/user_type/privileges of a logged-in user'
            elif method == 'DELETE' and str(user['_id']) == str(flask.g.user['_id']):
                return 'Not allowed to disable your own profile.'

        if method == 'PATCH' and is_sensitive_update(updates) and not current_user_has_privilege('users'):
            return 'Insufficient privileges to update role/user_type/privileges'

    def __handle_status_changed(self, updates, user):
        enabled = updates.get('is_enabled', None)
        active = updates.get('is_active', None)

        if enabled is not None or active is not None:
            get_resource_service('auth').delete_action({'username': user.get('username')})  # remove active tokens
            updates.update({'session_preferences', {}})

            # send email notification
            can_send_mail = get_resource_service('preferences').email_notification_is_enabled(user_id=user['_id'])

            status = ''

            if enabled is not None:
                status = 'enabled' if enabled else 'disabled'

            if (status == '' or status == 'enabled') and active is not None:
                status = 'enabled and active' if active else 'enabled but inactive'

            if can_send_mail:
                send_user_status_changed_email([user['email']], status)

    def on_create(self, docs):
        for user_doc in docs:
            user_doc.setdefault('display_name', get_display_name(user_doc))
            if not user_doc.get('role', None):
                user_doc['role'] = get_resource_service('roles').get_default_role_id()
            get_resource_service('preferences').set_user_initial_prefs(user_doc)

    def on_created(self, docs):
        for user_doc in docs:
            self.__update_user_defaults(user_doc)
            add_activity(ACTIVITY_CREATE, 'created user {{user}}', self.datasource,
                         user=user_doc.get('display_name', user_doc.get('username')))

    def on_update(self, updates, original):
        """
        Overriding the method to prevent user from the below:
            1. Check if the user is updating his/her own status.
            2. Check if the user is changing the status of other logged-in users.
            3. A user without 'User Management' privilege is changing role/user_type/privileges
        """
        error_message = self.__is_invalid_operation(original, updates, 'PATCH')
        if error_message:
            raise SuperdeskApiError.forbiddenError(message=error_message)

        if updates.get('is_enabled', False):
            updates['is_active'] = True

    def on_updated(self, updates, user):
        if 'role' in updates or 'privileges' in updates:
            get_resource_service('preferences').on_update(updates, user)
        self.__handle_status_changed(updates, user)

    def on_delete(self, user):
        """
        Overriding the method to prevent user from the below:
            1. Check if the user is updating his/her own status.
            2. Check if the user is changing the status of other logged-in users.
            3. A user without 'User Management' privilege is changing role/user_type/privileges
        """

        updates = {'is_enabled': False, 'is_active': False}
        error_message = self.__is_invalid_operation(user, updates, 'DELETE')
        if error_message:
            raise SuperdeskApiError.forbiddenError(message=error_message)

    def delete(self, lookup):
        """
        Overriding the method to prevent from hard delete
        """

        user = super().find_one(req=None, _id=str(lookup['_id']))
        return super().update(id=lookup['_id'], updates={'is_enabled': False, 'is_active': False}, original=user)

    def __clear_locked_items(self, user_id):
        archive_service = get_resource_service('archive')
        archive_autosave_service = get_resource_service('archive_autosave')

        doc_to_unlock = {'lock_user': None, 'lock_session': None, 'lock_time': None, 'force_unlock': True}

        items_locked_by_user = archive_service.get(req=None, lookup={'lock_user': user_id})
        if items_locked_by_user and items_locked_by_user.count():
            for item in items_locked_by_user:
                # delete the item if nothing is saved so far
                if item['_version'] == 1 and item['state'] == 'draft':
                    get_resource_service('archive').delete(lookup={'_id': item['_id']})
                else:
                    archive_service.update(item['_id'], doc_to_unlock, item)
                    archive_autosave_service.delete(lookup={'_id': item['_id']})

    def on_deleted(self, doc):
        """
        Overriding to add to activity stream and handle user clean up:
            1. Authenticated Sessions
            2. Locked Articles
            3. Reset Password Tokens
        """

        add_activity(ACTIVITY_UPDATE, 'disabled user {{user}}', self.datasource,
                     user=doc.get('display_name', doc.get('username')))
        self.__clear_locked_items(str(doc['_id']))
        self.__handle_status_changed(updates={'is_enabled': False, 'is_active': False}, user=doc)

    def on_fetched(self, document):
        for doc in document['_items']:
            self.__update_user_defaults(doc)

    def on_fetched_item(self, doc):
        self.__update_user_defaults(doc)

    def __update_user_defaults(self, doc):
        """Set default fields for users"""
        doc.setdefault('display_name', get_display_name(doc))
        doc.pop('password', None)
        doc.setdefault('is_enabled', doc.get('is_active'))

    def user_is_waiting_activation(self, doc):
        return doc.get('needs_activation', False)

    def is_user_active(self, doc):
        return doc.get('is_active', False)

    def get_role(self, user):
        if user:
            role_id = user.get('role', None)
            if role_id:
                return get_resource_service('roles').find_one(_id=role_id, req=None)
        return None

    def set_privileges(self, user, role):
        user['active_privileges'] = get_privileges(user, role)

    def get_users_by_user_type(self, user_type='user'):
        return list(self.get(req=None, lookup={'user_type': user_type}))

    def get_invisible_stages(self, user_id):
        user = self.find_one(_id=user_id, req=None)
        return get_invisible_stages(user) if user and user.get('_id') else []

    def get_invisible_stages_ids(self, user_id):
        return [str(stage['_id']) for stage in self.get_invisible_stages(user_id)]


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
                    raise SuperdeskApiError.internalError('Failed to send account activation email.')
                tokenDoc.update({'username': doc['username']})
                send_activate_account_email(tokenDoc)

    def on_update(self, updates, user):
        super().on_update(updates, user)
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
            raise SuperdeskApiError.unauthorizedError('User not found')

        if not self.is_user_active(user):
            raise UserInactiveError()

        updates = {'password': get_hash(password, app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12)),
                   app.config['LAST_UPDATED']: utcnow()}

        if self.user_is_waiting_activation(user):
            updates['needs_activation'] = False

        self.patch(user_id, updates=updates)

    def on_deleted(self, doc):
        """
        Overriding clean up reset password tokens:
        """

        super().on_deleted(doc)
        get_resource_service('reset_user_password').remove_all_tokens_for_email(doc.get('email'))


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
        super().on_fetched_item(doc)
        doc['_readonly'] = ADUsersService.readonly_fields


class RolesService(BaseService):

    def on_update(self, updates, original):
        if updates.get('is_default'):
            # if we are updating the role that is already default that is OK
            if original.get('is_default'):
                return
            self.remove_old_default()

    def on_create(self, docs):
        for doc in docs:
            # if this new one is default need to remove the old default
            if doc.get('is_default'):
                self.remove_old_default()

    def on_delete(self, docs):
        if docs.get('is_default'):
            raise SuperdeskApiError.forbiddenError('Cannot delete the default role')
        # check if there are any users in the role
        user = get_resource_service('users').find_one(req=None, role=docs.get('_id'))
        if user:
            raise SuperdeskApiError.forbiddenError('Cannot delete the role, it still has users in it!')

    def remove_old_default(self):
        # see if there is already a default role and set it to no longer default
        role_id = self.get_default_role_id()
        # make it no longer default
        if role_id:
            role = self.find_one(req=None, is_default=True)
            get_resource_service('roles').update(role_id, {"is_default": False}, role)

    def get_default_role_id(self):
        role = self.find_one(req=None, is_default=True)
        return role.get('_id') if role is not None else None
