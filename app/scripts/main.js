define('main', [
    'gettext',
    'angular',
    'superdesk/modules'
], function(gettext, angular, modules) {
    'use strict';

    return function bootstrap(config, apps) {

        angular.module('superdesk', []).constant('config', config);
        modules.push('superdesk');

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
