define([
    'angular',
    'require',
    './api-service',
    './timeout-interceptor',
    './request-service',
    './url-resolver-service'
], function(angular, require) {
    'use strict';

    return angular.module('superdesk.data', [])
        .provider('api', require('./api-service'))
        .service('request', require('./request-service'))
        .service('urls', require('./url-resolver-service'))
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push(require('./timeout-interceptor'));
        }]);
});
