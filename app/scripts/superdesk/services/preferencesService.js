define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.services.preferencesService', [])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage', 'session',
            function($injector, $rootScope, $q, storage, session) {

            var USER_PREFERENCES = 'user_preferences',
                SESSION_PREFERENCES = 'session_preferences',
                PREFERENCES = 'preferences',
                userPreferences = ['feature:preview', 'archive:view', 'email:notification', 'workqueue:items'],
                //sessionPreferences = ['scratchpad:items', 'pinned:items', 'desk:items'],
                api,
                defer,
                original_preferences = null;

            function saveLocally(preferences, type, key) {

                //console.log('saving saveLocally:', preferences, type, key);

                if (type && key && original_preferences)
                {
                    original_preferences[type][key] = preferences[type][key];
                    original_preferences._etag = preferences._etag;
                } else
                {
                    original_preferences = preferences;
                }

                //console.log('saved saveLocally:', this.original_preferences);

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

            function getPreferences(sessionId) {
                if (!api) { api = $injector.get('api'); }
                return api('preferences').getById(sessionId);
            }

            this.get = function(key, sessionId) {

                var original_prefs = loadLocally();
                
                var result;

                sessionId = sessionId || $rootScope.sessionId;

                if (!original_prefs){

                    return session.getIdentity().then(function() {

                        console.log('fetch', sessionId);
                        return getPreferences(session.sessionId).then(function(preferences) {

                            saveLocally(preferences);
                            original_prefs = preferences;

                            if (!key){
                                result = original_prefs[USER_PREFERENCES];
                            } else if (userPreferences.indexOf(key) >= 0) {
                                result = original_prefs[USER_PREFERENCES][key];
                            } else {
                                result = original_prefs[SESSION_PREFERENCES][key];
                            }

                            return result;

                        });

                    });
                } else {
                    if (!key){
                        result = original_prefs[USER_PREFERENCES];
                    } else if (userPreferences.indexOf(key) >= 0) {
                        var prefs = original_prefs[USER_PREFERENCES] || {};
                        result =  prefs[key] || null;
                    } else {
                        var sess_prefs = original_prefs[SESSION_PREFERENCES] || {};
                        result = sess_prefs[key] || null;
                    }

                    return $q.when(result);
                }
                
                return $q.reject();
            };

            this.update = function(updates, key) {
                if (!key){
                    return updatePreferences(updates);
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

                defer = $q.defer();

                api('preferences', $rootScope.sessionId).save(original_prefs, user_updates)
                    .then(function(result) {
                                saveLocally(result, type, key);
                                return defer.resolve(result);
                            },
                            function(response) {
                                console.log('patch err response:', response);
                                return defer.reject(response);
                        });

                return defer.promise;

            }

    }]);

});
