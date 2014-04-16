define([
    'angular',
    'require',
    './api-service',
    './timeout-interceptor'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.data', [])
        .provider('api', require('./api-service'))
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push(require('./timeout-interceptor'));
        }]);
});
