define([], function() {
    'use strict';

    /**
     * Set timeout for requests and notify $rootScope when it is triggered
     */
    TimeoutInterceptor.$inject = ['$timeout', '$injector', '$rootScope'];
    function TimeoutInterceptor($timeout, $injector, $rootScope) {

        var TIMEOUT = 8000,
            STATUS = {
                OK: 0
            };

        $rootScope.serverStatus = STATUS.OK;

        return {

            // set timeout for every request
            request: function(config) {
                config.timeout = config.timeout || TIMEOUT;
                return config;
            },

            // reset server status on success
            response: function(response) {
                $rootScope.serverStatus = STATUS.OK;
                return response;
            },

            // repeat request once with higher timeout
            responseError: function(rejection) {
                if (!rejection.status) {
                    $rootScope.serverStatus += 1;
                    rejection.config.timeout = TIMEOUT;
                    return $injector.get('$http')(rejection.config);
                }

                $rootScope.serverStatus = STATUS.OK;
                return rejection;
            }
        };
    }

    return TimeoutInterceptor;
});
