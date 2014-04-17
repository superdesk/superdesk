
/* exported gettext */

/**
 * Noop for registering string for translation in js files.
 *
 * This is supposed to be used in angular config phase,
 * where we can't use the translate service.
 *
 * @param {string} input
 * @return {string} unmodified input
 */
function gettext(input) {
    'use strict';
    return input;
}

define('main', [
    'angular',
    'jquery',
    'lodash',
    'angular-ui',
    'angular-route',
    'angular-gettext',
    'angular-resource',
    'angular-mocks',
    'angular-file-upload',
    'gridster'
], function(angular) {
    'use strict';

    var modules = [
        'gettext',
        'ngRoute',
        'ngResource',
        'ui.bootstrap',
        'angularFileUpload',

        'superdesk',
        'superdesk.filters',
        'superdesk.services',
        'superdesk.directives',

        'superdesk.auth',
        'superdesk.data',
        'superdesk.datetime',
        'superdesk.error',

        'test'
    ];

    angular.module('superdesk', []); // todo replace .filters/.directives/.services with superdesk
    angular.module('superdesk.filters', []);
    angular.module('superdesk.services', []);
    angular.module('superdesk.directives', []);
    angular.module('test', []); // used for mocking

    return function bootstrap(config) {
        angular.module('superdesk').constant('config', config);

        // load core components
        require([
            'superdesk/auth/auth',
            'superdesk/data/data',
            'superdesk/datetime/datetime',
            'superdesk/error/error',
            'superdesk/filters',
            'superdesk/services/all',
            'superdesk/directives/all'
        ], function() {
            // build deps
            var deps = [];
            angular.forEach(config.apps, function(app) {
                deps.push('superdesk-' + app + '/module');
                modules.push('superdesk.' + app);
            });

            // load apps
            require(deps, function() {
                var body = angular.element('body');
                body.ready(function() {
                    angular.bootstrap(body, modules);
                });
            });
        });
    };
});
