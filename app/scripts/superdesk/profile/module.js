define([
    'angular',
    './controllers/main',
    './directives',
    './resources',
    '../users/module'
], function(angular) {
    'use strict';

    angular.module('superdesk.profile', ['superdesk.profile.directives', 'superdesk.profile.resources', 'superdesk.users']).
        config(['$routeProvider', function($routeProvider) {
            $routeProvider.
                when('/my-profile', {
                    controller: require('superdesk/profile/controllers/main'),
                    templateUrl: 'scripts/superdesk/profile/views/main.html',
                    resolve: {
                        user: function($rootScope, server) {
                            return server.read($rootScope.currentUser);
                        }
                    }
                });
        }]);
});
