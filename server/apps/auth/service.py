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
from flask import request, current_app as app
from superdesk import utils as utils, get_resource_service
from superdesk.services import BaseService
from eve.utils import config
from superdesk.errors import SuperdeskApiError


class AuthService(BaseService):

    def authenticate(self, document):
        raise NotImplementedError()

    def on_create(self, docs):
        for doc in docs:
            user = self.authenticate(doc)

            self.set_auth_default(doc, user['_id'])

    def on_created(self, docs):
        for doc in docs:
            get_resource_service('preferences').set_session_based_prefs(doc['_id'], doc['user'])

    def on_deleted(self, doc):
        """
        :param doc: A deleted auth doc AKA a session
        :return:
        """
        # notify that the session has ended
        app.on_session_end(doc['user'], doc['_id'])

    def set_auth_default(self, doc, user_id):
        doc['user'] = user_id
        doc['token'] = utils.get_random_string(40)
        del doc['password']


class UserSessionClearService(BaseService):

    def delete(self, lookup):
        """
        Deletes all the records from auth and corresponding
        session_preferences from user collections
        If there are any orphan session_preferences exist they get deleted as well
        """
        users_service = get_resource_service('users')
        user_id = request.view_args['user_id']
        user = users_service.find_one(req=None, _id=user_id)
        sessions = get_resource_service('auth').get(req=None, lookup={'user': user_id})

        error_message = self.__can_clear_sessions(user)
        if error_message:
            raise SuperdeskApiError.forbiddenError(message=error_message)

        # Delete all the sessions
        for session in sessions:
            get_resource_service('auth').delete_action({config.ID_FIELD: str(session[config.ID_FIELD])})

        # Check if any orphan session_preferences exist for the user
        if user.get('session_preferences'):
            # Delete the orphan sessions
            users_service.patch(user[config.ID_FIELD], {'session_preferences': {}})

        return [{'complete': True}]

    def __can_clear_sessions(self, user):
        """
        Checks if the session clear request is Invalid.
        Operation is invalid if one of the below is True:
            1. Check if the user exists.
            2. Check if the user is clearing his/her own sessions.
        :return: error message if invalid.
        """

        if not user:
            return 'Invalid user to clear sessions.'

        if str(user[config.ID_FIELD]) == str(flask.g.user[config.ID_FIELD]):
            return 'Not allowed to clear your own sessions.'
