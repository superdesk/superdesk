define([
    'angular',
    'raven-js',
], function(angular, Raven) {
    'use strict';

    var app = angular.module('errorCatcher', []);
    
    if (Configuration.raven.dsn) {
        Raven.config(Configuration.raven.dsn, {logger: 'javascript-client'}).install();

        app
        .factory('$exceptionHandler', function () {
            return function errorCatcherHandler(exception, cause) {
                Raven.captureException(exception, {tags: {component: 'ui'}, extra: exception});
                console.log(exception.stack);
                console.log(cause);
            };
        })
        .factory('errorHttpInterceptor', ['$q', function ($q) {
            return {
                responseError: function responseError(rejection) {
                    if (rejection.status >= 500 && rejection.status < 600) {
                        Raven.captureException(new Error('HTTP response error'), {
                            tags: {component: 'server'},
                            extra: {
                                config: rejection.config,
                                status: rejection.status
                            }
                        });
                    }
                    return $q.reject(rejection);
                }
            };
        }])
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push('errorHttpInterceptor');
        }]);
    }
});
