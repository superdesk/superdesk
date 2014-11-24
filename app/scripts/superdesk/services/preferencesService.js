define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.preferences', ['superdesk.notify'])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage', 'session', 'notify', 'gettext',
            function PreferencesService($injector, $rootScope, $q, storage, session, notify, gettext) {

            var USER_PREFERENCES = 'user_preferences',
                SESSION_PREFERENCES = 'session_preferences',
                ACTIVE_PRIVILEGES = 'active_privileges',
                PREFERENCES = 'preferences',
                userPreferences = ['feature:preview', 'archive:view', 'email:notification', 'workqueue:items'],
                api,
                original_preferences = null;

            function saveLocally(preferences, type, key) {

                if (type && key && original_preferences)
                {
                    original_preferences[type][key] = preferences[type][key];
                    original_preferences._etag = preferences._etag;
                } else
                {
                    original_preferences = preferences;
                }

                storage.setItem(PREFERENCES, original_preferences);
            }

            function loadLocally()
            {
                if (!original_preferences)
                {
                    original_preferences = storage.getItem(PREFERENCES);
                }

                return original_preferences;
            }

            this.remove = function() {
                storage.removeItem(PREFERENCES);
                original_preferences = null;
            };

            this.getPrivileges = function getPrivileges(key) {
                return this.get().then(function() {
                    var preferences = loadLocally();

                    if (!key){
                        return $q.when(preferences[ACTIVE_PRIVILEGES]);
                    } else {
                        return $q.when(preferences[ACTIVE_PRIVILEGES][key]);
                    }
                });
            };

            function getPreferences(sessionId, key){
                if (!api) { api = $injector.get('api'); }

                if (!sessionId) {
                    return $q.reject();
                }

                return api('preferences').getById(sessionId).then(function(preferences) {
                    saveLocally(preferences);
                    return processPreferences(preferences, key);
                });
            }

            function processPreferences(preferences, key){

                if (!key){
                    return preferences[USER_PREFERENCES];
                } else if (userPreferences.indexOf(key) >= 0) {
                    return preferences[USER_PREFERENCES][key];
                } else {
                    return preferences[SESSION_PREFERENCES][key];
                }
            }

            this.get = function(key, sessionId) {

                var original_prefs = loadLocally();
                sessionId = sessionId || session.sessionId || $rootScope.sessionId;

                if (!original_prefs) {

                    if (sessionId) {
                        return getPreferences(sessionId, key);
                    } else {
                        return session.getIdentity().then(function() {
                            return getPreferences(session.sessionId, key);
                        });
                    }

                } else {

                    return $q.when(processPreferences(original_prefs, key));
                }

                return $q.reject();
            };

            this.update = function(updates, key) {
                if (!key){
                    return updatePreferences(USER_PREFERENCES, updates);
                } else if (userPreferences.indexOf(key) >= 0) {
                    return updatePreferences(USER_PREFERENCES, updates, key);
                } else {
                    return updatePreferences(SESSION_PREFERENCES, updates, key);
                }
            };

            function updatePreferences (type, updates, key) {

                var original_prefs = _.cloneDeep(loadLocally());
                var user_updates = {};
                user_updates[type] = updates;

                if (!api) { api = $injector.get('api'); }

                return api('preferences').save(original_prefs, user_updates)
                    .then(function(result) {
                        saveLocally(result, type, key);
                        return result;
                    }, function(response) {
                        console.error(response);
                        notify.error(gettext('User preference could not be saved...'));
                    });
            }

            $rootScope.$watch(function() {
                return session.sessionId;
            }, getPreferences);
    }]);

});
