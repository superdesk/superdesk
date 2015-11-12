define([
    'angular',
    'require',

    'angular-ui',
    'angular-route',
    'angular-resource',
    'angular-file-upload',

    './activity/activity',
    './analytics/analytics',
    './api/api',
    './auth/auth',
    './beta/beta',
    './config/config',
    './datetime/datetime',
    './elastic/elastic',
    './error/error',
    './notify/notify',
    './upload/upload',
    './ui/ui',

    './filters',
    './services/all',
    './directives/all'
], function(angular, require) {
    'use strict';

    var modules = [
        'ngRoute',
        'ngResource',
        'ui.bootstrap',
        'angularFileUpload',

        require('./activity/activity').name,
        require('./analytics/analytics').name,
        require('./api/api').name,
        require('./auth/auth').name,
        require('./beta/beta').name,
        require('./config/config').name,
        require('./datetime/datetime').name,
        require('./elastic/elastic').name,
        require('./error/error').name,
        require('./notify/notify').name,
        require('./upload/upload').name,
        require('./ui/ui').name,

        'superdesk.menu'
    ];

    modules.push(require('./filters').name);

    // todo(petr): refactor into func based modules
    modules.push.apply(modules, require('./services/all'));
    modules.push.apply(modules, require('./directives/all'));

    angular.module('superdesk.loading', [])

        // prevent routing before there is auth token
        .run(['$rootScope', '$route', '$location', '$http', 'session', 'preferencesService',
        function($rootScope, $route, $location, $http, session, preferencesService) {
            var stopListener = angular.noop;
            $rootScope.loading = true;

            // fetch preferences on load
            preferencesService.get().then(function() {
                stopListener();
                $http.defaults.headers.common.Authorization = session.token;
                $rootScope.loading = false;
                // do this in next $digest so that beta service can setup route redirects
                // for features that should not be available
                $rootScope.$applyAsync($route.reload);
            });

            // prevent routing when there is no token
            stopListener = $rootScope.$on('$locationChangeStart', function (e) {
                $rootScope.requiredLogin = requiresLogin($location.path());
                if ($rootScope.loading && $rootScope.requiredLogin) {
                    e.preventDefault();
                }
            });

            /**
             * Finds out if there is a route matching given url that requires a login
             *
             * @param {string} url
             */
            function requiresLogin(url) {
                var routes = _.values($route.routes);
                for (var i = routes.length - 1; i >= 0; i--) {
                    if (routes[i].regexp.test(url)) {
                        return routes[i].auth;
                    }
                }
                return false;
            }
        }]);

    return angular.module('superdesk', modules);
});
