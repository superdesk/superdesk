define([], function() {
    'use strict';

    /**
     * Set timeout for requests and notify $rootScope when it is triggered
     */
    TimeoutInterceptor.$inject = ['$timeout', '$q', '$injector', '$rootScope'];
    function TimeoutInterceptor($timeout, $q, $injector, $rootScope) {

        var TIMEOUT = 3000,
            TIMEOUT_MAX = 60000,
            STATUS = {
                OK: 0
            };

        var IS_VIEW_REGEXP = /\.html?$/;

        $rootScope.serverStatus = STATUS.OK;

        return {

            // set timeout for every request
            request: function(config) {
                if (!IS_VIEW_REGEXP.test(config.url) && !config.isUpload) {
                    config._ttl = config._ttl ? Math.min(TIMEOUT_MAX, config._ttl * 2) : TIMEOUT;
                    config.timeout = $timeout(function() {
                        config._isTimeout = true;
                    }, config._ttl);
                }

                return config;
            },

            // reset server status on success
            response: function(response) {
                if (response.config.timeout) {
                    $timeout.cancel(response.config.timeout);
                    $rootScope.serverStatus = STATUS.OK;
                }

                return response;
            },

            // repeat request with higher timeout
            responseError: function(rejection) {
                if (!rejection.status && !rejection.config.isUpload) {
                    $rootScope.serverStatus += 1;
                    return $injector.get('$http')(rejection.config);
                } else {
                    $timeout.cancel(rejection.config.timeout);
                }

                $rootScope.serverStatus = STATUS.OK;
                return $q.reject(rejection);
            }
        };
    }

    return TimeoutInterceptor;
});
