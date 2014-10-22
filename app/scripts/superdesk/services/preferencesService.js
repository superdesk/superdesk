define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.services.preferencesService', [])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage',
            function($injector, $rootScope, $q, storage){
        
            var USER_PREFERENCES = 'user_preferences',
                SESSION_PREFERENCES = 'session_preferences',
                PREFERENCES = 'preferences',
                api,
                defer;

            this.original_preferences;

            
            this.saveLocally = function(preferences){
                storage.setItem(PREFERENCES, preferences);
                this.original_preferences = preferences
            }

            
            this.loadLocally = function()
            {
                if(!this.original_preferences)
                {
                    this.original_preferences = storage.getItem(PREFERENCES);
                }

                return this.original_preferences;
            }

            this.deleteLocally = function()
            {
                storage.removeItem(PREFERENCES);
                this.original_preferences = null;
            }


            this.getPreferences = function(sessionId) {
                if (!api) { api = $injector.get('api'); }

                defer = $q.defer();

                api('preferences').getById(sessionId)
                    .then(function(result) {
                        return defer.resolve(result);
                    });

                return defer.promise;
            };

            this.get = function(key) {
                
                var instance = this;
                var original_prefs = this.loadLocally();

                if (!original_prefs && $rootScope.sessionId)
                {
                    this.getPreferences($rootScope.sessionId).then(function(preferences){
                        instance.saveLocally(preferences);
                        original_prefs = preferences;
                    });
                }
                
                if (!original_prefs)
                {
                    return null;
                }
                
                if (key == "feature:preview") {
                    return original_prefs[USER_PREFERENCES][key];
                }
                else {
                    return original_prefs[SESSION_PREFERENCES][key];
                }
            };

            this.update = function(updates) {
                var instance = this;
                if (updates["feature:preview"]) {
                    this.updateUserPreferences(updates).then(function(results){
                        instance.saveLocally(results);
                    });
                } else {

                }
            };


            this.updateUserPreferences = function(updates) {
                
                var original_prefs = this.loadLocally();
                var user_updates = {"user_preferences": updates};

                if (!api) { api = $injector.get('api'); }

                defer = $q.defer();

                api('preferences', $rootScope.sessionId).save(this.original_preferences, user_updates)
                    .then(function(result) {
                            return defer.resolve(result);
                            }, 
                            function(response) {
                            console.log("patch err response:", response);
                            return defer.reject(response);
                        });

                return defer.promise;

            };

        
    }]);

});
