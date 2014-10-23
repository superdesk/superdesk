define(['angular','lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.services.preferencesService', [])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage',
            function($injector, $rootScope, $q, storage){
        
            var USER_PREFERENCES = 'user_preferences',
                SESSION_PREFERENCES = 'session_preferences',
                PREFERENCES = 'preferences',
                userPreferences = ["feature:preview", "archive:view"],
                api,
                defer;

            this.original_preferences;

            
            this.saveLocally = function(preferences, section, key){
                
                //console.log("saving saveLocally:", preferences, section, key);

                if(section && key && this.original_preferences)
                {
                    this.original_preferences[section][key] = preferences[section][key];
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

                            if (userPreferences.indexOf(key) >= 0 ) {
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

                    if (userPreferences.indexOf(key) >= 0 ) {
                        return original_prefs[USER_PREFERENCES][key];
                    }
                    else {
                        return original_prefs[SESSION_PREFERENCES][key];
                    }
                }
            };

            this.update = function(updates, key) {
                if (userPreferences.indexOf(key) >= 0 ) {
                    return this.updateUserPreferences(updates, key);
                } else {

                }
            };


            this.updateUserPreferences = function(updates, key) {
                
                var instance = this;
                var original_prefs = _.cloneDeep(this.loadLocally());
                var user_updates = {"user_preferences": updates};

                if (!api) { api = $injector.get('api'); }

                defer = $q.defer();

                api('preferences', $rootScope.sessionId).save(original_prefs, user_updates)
                    .then(function(result) {
                                instance.saveLocally(result, "user_preferences", key);
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
