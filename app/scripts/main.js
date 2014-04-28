define('main', [
    'gettext',
    'angular',
    'superdesk/superdesk'
], function(gettext, angular, superdesk) {
    'use strict';

    var modules = [superdesk.name];

    return function bootstrap(config, apps) {

        superdesk.constant('config', config);

        if (config.ga && window.ga) {
            superdesk.run(['$rootScope', function($rootScope) {
                $rootScope.$on('$routeChangeSuccess', function(ev, route) {
                    window.ga('send', 'pageview', {
                        page: route.$$route._id,
                        title: route.$$route.label
                    });
                });
            }]);
        }

        angular.forEach(apps, function(app) {
            if (angular.isFunction(app.config)) {
                modules.push(app.name);
            }
        });

        // load apps & bootstrap
        var body = angular.element('body');
        body.ready(function() {
            angular.bootstrap(body, modules);
        });
    };
});
