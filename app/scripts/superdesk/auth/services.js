define([
    'angular',
    'superdesk/api',
    './authService'
], function(angular) {
    'use strict';
    angular.module('superdesk.auth.services', ['superdesk.api']).
        factory('Auth', function(resource) {
            return resource('/auth', {}, {
                save: {method: 'POST'}
            });
        }).
        service('authService', require('superdesk/auth/authService'));
});
