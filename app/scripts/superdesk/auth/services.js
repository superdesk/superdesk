define([
    'angular',
    './authService'
], function(angular) {
    'use strict';
    angular.module('superdesk.auth.services', []).
        service('authService', require('superdesk/auth/authService'));
});