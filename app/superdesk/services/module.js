define([
    'angular',
    'superdesk/services/test',
    'superdesk/services/auth'
], function(angular) {
    'use strict';

    var services = angular.module('superdesk.services', [
        'superdesk.services.test',
        'superdesk.services.auth'
    ]);
});