(function() {
    'use strict';

    angular.module('superdesk.api', [
        'superdesk.config',
        'superdesk.api.http',
        'superdesk.api.service',
        'superdesk.api.request',
        'superdesk.api.urls',
        'superdesk.api.timeout'
    ])
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.interceptors.push('timeoutInterceptor');
        }]);
})();
