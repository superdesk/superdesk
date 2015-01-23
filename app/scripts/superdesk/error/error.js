define([
    'angular',
    'raven-js'
], function(angular, Raven) {
    'use strict';

    var app = angular.module('superdesk.error', []);

    app.config(['config', '$httpProvider', function(config, $httpProvider) {
        if (config.raven && config.raven.dsn) {
            Raven.config(config.raven.dsn, {logger: 'javascript-client'}).install();
            $httpProvider.interceptors.push(ErrorHttpInterceptorFactory);

            app.factory('$exceptionHandler', function () {
                return function errorCatcherHandler(exception, cause) {
                    Raven.captureException(exception, {tags: {component: 'ui'}, extra: exception});
                    throw exception;
                };
            });
        }
    }]);

    ErrorHttpInterceptorFactory.$inject = ['$q'];
    function ErrorHttpInterceptorFactory($q) {
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
    }

    return app;
});
