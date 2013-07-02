define([
    'angular',
    'ngCookies'
], function(angular) {
    'use strict';

    var authService = angular.module('superdesk.services.auth', ['ngCookies']);
    
    authService.factory('authService', function($cookieStore){
        var service = {
            getToken: function() {
                return $cookieStore.get('token');
            },
            setToken: function(newToken) {
                $cookieStore.put('token', newToken);
            },
        };

        return service;
    });
});