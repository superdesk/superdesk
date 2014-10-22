define(['angular'], function(angular) {
    'use strict';

    /**
     * Preference Service stores current user data on MongoDB
     */
    return angular.module('superdesk.services.preferencesService', [])

        .service('preferencesService', ['$injector', '$rootScope', '$q', 'storage',
            function($injector, $rootScope, $q, storage){
        
            var api;

            var USER_PREFERENCES = 'user_preferences',
                SESSION_PREFERENCES = 'session_preferences',
                PREFERENCES = 'preferences',
                original_preferences,
                defer;

            
            this.user_preferences = {USER_PREFERENCES:""};
            this.session_preferences = {SESSION_PREFERENCES:""};

            this.saveLocally = function(preferences){
                storage.setItem(PREFERENCES, preferences);
            }

            this.getPreferences = function(sessionId) {
                if (!api) { api = $injector.get('api'); }

                defer = $q.defer();

                api('preferences').getById(sessionId)
                    .then(function(result) {
                        original_preferences = result;
                        //this.user_preferences = result[USER_PREFERENCES];
                        //this.session_preferences = result[SESSION_PREFERENCES];
                        //buildPreferences(orig);
                        return defer.resolve(result);
                    });

                return defer.promise;
            };


            this.updateUserPreferences = function(updates) {
                
                this.getPreferences($rootScope.sessionId).then(function(origin){
                    console.log("promise:", updates);
                });


                console.log("updateUserPreferences entered with updates:", updates);
                
                original_preferences[USER_PREFERENCES] = updates;

                console.log("user_preferences", original_preferences[USER_PREFERENCES]);

                if (!api) { api = $injector.get('api'); }

                console.log("sessionId:", $rootScope.sessionId);

                api('preferences', $rootScope.sessionId).save(original_preferences, updates)
                    .then(function(result) {
                            console.log("patch result:", result);
                            }, function(response) {
                            console.log("patch err response:", response);
                        });

                //storage.setItem(IDENTITY_KEY, this.identity);
            };


           

       
        
    }]);

});
