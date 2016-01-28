(function() {
    'use strict';

    var modules = [
        'ngRoute',
        'ngResource',
        'ui.bootstrap',
        'angularFileUpload',
        'superdesk.activity',
        'superdesk.analytics',
        'superdesk.api',
        'superdesk.auth',
        'superdesk.services.beta',
        'superdesk.config',
        'superdesk.datetime',
        'superdesk.elastic',
        'superdesk.error',
        'superdesk.notify',
        'superdesk.ui',
        'superdesk.upload',
        'superdesk.menu',
        'superdesk.filters',
        // services/
        'superdesk.services.data',
        'superdesk.services.modal',
        'superdesk.services.dragdrop',
        'superdesk.services.server',
        'superdesk.services.entity',
        'superdesk.services.permissions',
        'superdesk.services.storage',
        'superdesk.preferences',
        'superdesk.translate',
        'superdesk.workflow',
        // directives/
        'superdesk.directives.autofocus',
        'superdesk.directives.throttle',
        'superdesk.directives.sort',
        'superdesk.links',
        'superdesk.check.directives',
        'superdesk.confirm.directives',
        'superdesk.select.directives',
        'superdesk.permissions.directives',
        'superdesk.avatar',
        'superdesk.dragdrop.directives',
        'superdesk.typeahead.directives',
        'superdesk.slider.directives',
        'superdesk.directives.searchList'
    ];

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

    angular.module('superdesk', modules);
})();
