define([
    'angular',
    'angular-route',
    './controllers/main',
    './directives',
    './resources',
], function(angular) {
    'use strict';

    angular.module('superdesk.profile', ['ngRoute','superdesk.profile.directives','superdesk.profile.resources']).
        config(function($routeProvider) {
            $routeProvider.
                when('/my-profile', {
                    controller: require('superdesk/profile/controllers/main'),
                    templateUrl: 'scripts/superdesk/profile/views/main.html',
                });
        });
});
