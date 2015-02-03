define([], function() {
    'use strict';

    /**
     * Set timeout for requests and notify $rootScope when it is triggered
     */
    TimeoutInterceptor.$inject = ['$timeout', '$q', '$rootScope', 'request'];
    function TimeoutInterceptor($timeout, $q, $rootScope, request) {

        var TIMEOUT = 3000,
            TIMEOUT_MAX = 60000,
            STATUS = {
                OK: 0
            };

        var IS_VIEW_REGEXP = /\.html?$/;

        $rootScope.serverStatus = STATUS.OK;

        return {

            // set timeout for every request but upload
            xrequest: function(config) {
                if (!IS_VIEW_REGEXP.test(config.url) && !request.isUpload(config)) {
                    config._ttl = config._ttl ? Math.min(TIMEOUT_MAX, config._ttl * 2) : TIMEOUT;
                    config.timeout = $timeout(function() {
                        config._isTimeout = true;
                    }, config._ttl);
                }

                return config;
            },

            // reset server status on success
            xresponse: function(response) {
                if (response.config.timeout) {
                    $timeout.cancel(response.config.timeout);
                    $rootScope.serverStatus = STATUS.OK;
                }

                return response;
            },

            // repeat request with higher timeout
            xresponseError: function(rejection) {
                if (!rejection.status && !request.isUpload(rejection.config)) {
                    $rootScope.serverStatus += 1;
                    return request.resend(rejection.config);
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
