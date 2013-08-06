define([
    'angular',
    'superdesk/session/controllers/login'
], function(angular, LoginController) {
    'use strict';

    var session = angular.module('superdesk.session', []);
    session.controller('LoginController', LoginController);
});
