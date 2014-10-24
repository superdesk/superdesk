define(['angular','lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.services.preferencesService', [])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage',
            function($injector, $rootScope, $q, storage){
        
            var USER_PREFERENCES = 'user_preferences',
                SESSION_PREFERENCES = 'session_preferences',
                PREFERENCES = 'preferences',
                userPreferences = ["feature:preview", "archive:view", "email:notification"],
                sessionPreferences = ["scratchpad:items", "pinned:items", "desk:items"],
                api,
                defer;

            this.original_preferences;

            
            this.saveLocally = function(preferences, type, key){
                
                //console.log("saving saveLocally:", preferences, type, key);

                if(type && key && this.original_preferences)
                {
                    this.original_preferences[type][key] = preferences[type][key];
                    this.original_preferences["_etag"] = preferences["_etag"];
                }
                else
                {
                    this.original_preferences = preferences
                }

                //console.log("saved saveLocally:", this.original_preferences);

                
                storage.setItem(PREFERENCES, this.original_preferences);
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

                if (!original_prefs){

                    if ($rootScope.sessionId){
                        this.getPreferences($rootScope.sessionId).then(function(preferences){
                            instance.saveLocally(preferences);
                            original_prefs = preferences;

                            if(!key){
                                return original_prefs[USER_PREFERENCES];
                            }
                            else if (userPreferences.indexOf(key) >= 0 ) {
                                return original_prefs[USER_PREFERENCES][key];
                            }
                            else {
                                return original_prefs[SESSION_PREFERENCES][key];
                            }

                        });
                    
                    } else {
                        
                        return null;
                    }
                } else {

                    if(!key){
                        return original_prefs[USER_PREFERENCES];
                    }
                    else if (userPreferences.indexOf(key) >= 0 ) {
                        return original_prefs[USER_PREFERENCES][key];
                    }
                    else {
                        return original_prefs[SESSION_PREFERENCES][key];
                    }
                }
            };

            this.update = function(updates, key) {
                if(!key){
                    return this.updateUserPreferences(updates)
                }
                else if (userPreferences.indexOf(key) >= 0 ) {
                    return this.updatePreferences(USER_PREFERENCES, updates, key);
                } else {
                    return this.updatePreferences(SESSION_PREFERENCES, updates, key);
                }
            };


            this.updatePreferences = function(type, updates, key) {
                
                var instance = this;
                var original_prefs = _.cloneDeep(this.loadLocally());
                var user_updates = {};
                user_updates[type] = updates;

                if (!api) { api = $injector.get('api'); }

                defer = $q.defer();

                api('preferences', $rootScope.sessionId).save(original_prefs, user_updates)
                    .then(function(result) {
                                instance.saveLocally(result, type, key);
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
