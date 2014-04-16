define([
    'angular',
    'require',
    './api-service',
    './timeout-interceptor',
    './es'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.data', [])
        .provider('api', require('./api-service'))
        .service('es', require('./es'))
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push(require('./timeout-interceptor'));
        }]);
});
