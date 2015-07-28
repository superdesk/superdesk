define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.preferences', ['superdesk.notify', 'superdesk.session'])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'session', 'notify', 'gettext',
            function PreferencesService($injector, $rootScope, $q, session, notify, gettext) {
                var USER_PREFERENCES = 'user_preferences',
                    SESSION_PREFERENCES = 'session_preferences',
                    ACTIVE_PRIVILEGES = 'active_privileges',
                    ACTIONS = 'allowed_actions',
                    userPreferences = {
                        'feature:preview': 1,
                        'archive:view': 1,
                        'email:notification': 1,
                        'workqueue:items': 1,
                        'dashboard:ingest': 1,
                        'agg:view': 1,
                        'workspace:active': 1
                    },
                    preferences,
                    preferencesPromise;

                $rootScope.$watch(function() {
                    return session.token;
                }, resetPreferences);

                /**
                 * Get privileges for current user.
                 *
                 * @returns {Promise}
                 */
                this.getPrivileges = function getPrivileges() {
                    return this.get().then(function() {
                        return preferences[ACTIVE_PRIVILEGES] || {};
                    });
                };

                /**
                 * Get available content actions for current user.
                 *
                 * @returns {Promise}
                 */
                this.getActions = function getActions() {
                    return this.get().then(function() {
                        return preferences[ACTIONS] || [];
                    });
                };

                /**
                 * Fetch preferences from server and store local copy.
                 * On next call it will remove local copy and fetch again.
                 */
                function getPreferences() {
                    preferences = null;
                    preferencesPromise = session.getIdentity()
                        .then(function() {
                            var api = $injector.get('api');
                            return api.find('preferences', session.sessionId, null, true)
                                .then(function(_preferences) {
                                    preferences = _preferences;
                                    initPreferences(preferences);
                                    return preferences;
                                });
                        });
                }

                /**
                 * Get preference value from user or session preferences based on key.
                 *
                 * @param {string} key
                 * @returns {Object}
                 */
                function getValue(key){
                    if (!key) {
                        return preferences[USER_PREFERENCES];
                    } else if (userPreferences[key]) {
                        return preferences[USER_PREFERENCES][key];
                    } else {
                        return preferences[SESSION_PREFERENCES][key];
                    }
                }

                /**
                 * Get preference value, in case preferences are not loaded yet it will fetch it.
                 *
                 * @param {string} key
                 * @returns {Promise}
                 */
                this.get = function(key) {
                    if (!preferencesPromise) {
                        getPreferences();
                    }

                    return preferencesPromise.then(returnValue);

                    function returnValue() {
                        return getValue(key);
                    }
                };

                /**
                 * Update preferences
                 *
                 * It's done in 2 steps - schedule and commit. Schedule caches the changes
                 * and calls commit async. Following calls to update in same $digest will
                 * only cache changes. In next $digest those changes are pushed to api.
                 * This way we can update multiple preferences without getting etag conflicts.
                 *
                 * @param {object} updates
                 * @param {string} key
                 */
                this.update = function(updates, key) {
                    if (!key){
                        return scheduleUpdate(USER_PREFERENCES, updates);
                    } else if (userPreferences[key]) {
                        return scheduleUpdate(USER_PREFERENCES, updates, key);
                    } else {
                        return scheduleUpdate(SESSION_PREFERENCES, updates, key);
                    }
                };

                var updates,
                    deferUpdate;

                /**
                 * Schedule an update.
                 *
                 * Cache the changes and schedule a commit if it's first update in currect $digest.
                 *
                 * @param {string} type
                 * @param {object} _updates
                 */
                function scheduleUpdate(type, _updates) {
                    angular.extend(preferences[type], _updates);

                    // schedule commit
                    if (!updates) {
                        updates = {};
                        deferUpdate = $q.defer();
                        $rootScope.$applyAsync(commitUpdates);
                    }

                    // adding updates to current schedule
                    updates[type] = updates[type] || {};
                    angular.extend(updates[type], _updates);

                    return deferUpdate.promise;
                }

                /**
                 * Commit updates.
                 */
                function commitUpdates() {
                    var api = $injector.get('api'),
                    serverUpdates = updates;
                    updates = null;
                    return api.save('preferences', preferences, serverUpdates)
                        .then(function(result) {
                            preferences._etag = result._etag;
                            deferUpdate.resolve(result);
                            return result;
                        }, function(response) {
                            console.error(response);
                            notify.error(gettext('User preference could not be saved...'));
                            deferUpdate.reject(response);
                        }).finally(function() {
                            deferUpdate = null;
                        });
                }

                /**
                 * Make preferences reload after session expiry - token is set from something to null.
                 */
                function resetPreferences(newId, oldId) {
                    if (oldId && !newId) {
                        preferencesPromise = null;
                    }
                }

                /**
                 * Make sure all segments are presented in preferences.
                 */
                function initPreferences(preferences) {
                    angular.forEach([
                        USER_PREFERENCES,
                        SESSION_PREFERENCES,
                        ACTIVE_PRIVILEGES,
                        ACTIONS
                    ], function(key) {
                        if (preferences[key] == null) {
                            preferences[key] = {};
                        }
                    });
                }
            }]);
});
