define([
    'angular',
    './piwik-tracking',
    './google-tracking'
], function(angular, PiwikTracking, GoogleTracking) {
    'use strict';

    function NoopTracking() {
        this.track = angular.noop;
    }

    return angular.module('superdesk.analytics', [])

        .service('analytics', ['config', function(config) {
            if (config.analytics.piwik.url) {
                PiwikTracking.call(this, config.analytics.piwik);
            } else if (config.analytics.ga.id) {
                GoogleTracking.call(this, config.analytics.ga);
            } else {
                NoopTracking.call(this);
            }
        }])

        .run(['$rootScope', 'analytics', function($rootScope, analytics) {
            $rootScope.$on('$routeChangeSuccess', function(ev, route) {
                if (angular.isDefined(route)) {
                    analytics.track(route);
                }
            });
        }]);
});
