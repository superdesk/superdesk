(function() {
    'use strict';

    var Raven = window.Raven;

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

    angular.module('superdesk.error', [])
    .config(['config', '$httpProvider', '$provide', function(config, $httpProvider, $provide) {
        if (config.raven && config.raven.dsn) {
            Raven.config(config.raven.dsn, {logger: 'javascript-client'}).install();
            $httpProvider.interceptors.push(ErrorHttpInterceptorFactory);

            $provide.factory('$exceptionHandler', function () {
                return function errorCatcherHandler(exception, cause) {
                    Raven.captureException(exception, {tags: {component: 'ui'}, extra: exception});
                    throw exception;
                };
            });
        }
    }]);

})();
