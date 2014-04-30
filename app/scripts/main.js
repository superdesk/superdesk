define('main', [
    'gettext',
    'angular',
    'superdesk/superdesk'
], function(gettext, angular, superdesk) {
    'use strict';

    var modules = [superdesk.name];

    return function bootstrap(config, apps) {

        superdesk.constant('config', config);

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
