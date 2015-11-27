(function() {
    'use strict';

    angular.module('superdesk.api', ['superdesk.config'])
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push('timeoutInterceptor');
        }]);
})();
