define([
    'angular'
], function(angular) {
    'use strict';

    var authService = angular.module('superdesk.services.auth', []);
    
    authService.factory('authService', function(){
        var service = {
            getToken: function() {
            },
            setToken: function(newToken) {
            },
        };

        return service;
    });
});
