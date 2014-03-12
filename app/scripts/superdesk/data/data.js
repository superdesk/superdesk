define([
    'angular',
    'require',
    './resource-provider',
    './timeout-interceptor'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.data', ['superdesk'])
        .provider('resource', require('./resource-provider'))
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push(require('./timeout-interceptor'));
        }]);
});
