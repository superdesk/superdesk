define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.preferences', ['superdesk.notify', 'superdesk.services.storage', 'superdesk.session'])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage', 'session', 'notify', 'gettext',
            function PreferencesService($injector, $rootScope, $q, storage, session, notify, gettext) {
                var USER_PREFERENCES = 'user_preferences',
                    SESSION_PREFERENCES = 'session_preferences',
                    ACTIVE_PRIVILEGES = 'active_privileges',
                    PREFERENCES = 'preferences',
                    ACTIONS = 'allowed_actions',
                    userPreferences = {
                        'feature:preview': 1,
                        'archive:view': 1,
                        'email:notification': 1,
                        'workqueue:items': 1,
                        'dashboard:ingest': 1,
                        'agg:view': 1
                    },
                    original_preferences = null,
                    defaultPreferences = {};

                defaultPreferences[USER_PREFERENCES] = {};
                defaultPreferences[SESSION_PREFERENCES] = {};
                defaultPreferences[ACTIVE_PRIVILEGES] = {};
                defaultPreferences[ACTIONS] = {};

                function saveLocally(preferences, type) {
                    if (type && original_preferences) {
                        angular.extend(original_preferences[type], preferences[type]);
                    } else {
                        original_preferences = preferences;
                    }

                    original_preferences._etag = preferences._etag;
                    storage.setItem(PREFERENCES, original_preferences);
                }

                function loadLocally() {
                    if (!original_preferences) {
                        original_preferences = storage.getItem(PREFERENCES);
                    }

                    return original_preferences;
                }

                this.remove = function() {
                    storage.removeItem(PREFERENCES);
                    original_preferences = null;
                };

                this.getPrivileges = function getPrivileges() {
                    return this.get().then(function() {
                        var preferences = loadLocally();
                        return preferences[ACTIVE_PRIVILEGES] || {};
                    });
                };

                this.getActions = function getActions() {
                    return this.get().then(function() {
                        var preferences = loadLocally();
                        return preferences[ACTIONS] || [];
                    });
                };

                function getPreferences(sessionId, key) {
                    var api = $injector.get('api');

                    if (!sessionId) {
                        return $q.reject();
                    }

                    return api.find('preferences', sessionId, null, true).then(function(preferences) {
                        _.defaults(preferences, defaultPreferences);
                        saveLocally(preferences);
                        return processPreferences(preferences, key);
                    });
                }

                function processPreferences(preferences, key){
                    if (!key) {
                        return preferences[USER_PREFERENCES];
                    } else if (userPreferences[key]) {
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
                    } else if (userPreferences[key]) {
                        return updatePreferences(USER_PREFERENCES, updates, key);
                    } else {
                        return updatePreferences(SESSION_PREFERENCES, updates, key);
                    }
                };

                function updatePreferences(type, updates, key) {
                    var api = $injector.get('api');
                    var original_prefs = _.cloneDeep(loadLocally());
                    var user_updates = {};
                    user_updates[type] = updates;

                    if (type) {
                        // make changes available right away
                        angular.extend(original_preferences[type], updates);
                    }

                    return api.save('preferences', original_prefs, user_updates)
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
