
/* jshint -W098 */
/**
 * Noop for registering string for translation in js files.
 *
 * This is supposed to be used in angular config phase,
 * where we can't use the translate service.
 *
 * @param {string} input
 * @return {string} unmodified input
 *
 */

function gettext(input)
{
    'use strict';
    return input;
}

define('main', [
    'jquery',
    'lodash',
    'angular',
    'angular-ui',
    'angular-route',
    'angular-gettext',
    'angular-resource',
    'angular-mocks',
    'angular-file-upload',
    'gridster',
    'error-catcher'
], function($, _, angular) {
    'use strict';

    angular.module('superdesk', ['errorCatcher']); // todo replace .filters/.directives/.services with superdesk
    angular.module('superdesk.filters', []);
    angular.module('superdesk.services', []);
    angular.module('superdesk.directives', []);
    angular.module('test', []); // used for mocking
    angular.module('superdesk').constant('config', {server: Configuration.server});

    return function bootstrap(apps) {
        // load core components
        require([
            'superdesk/auth/auth',
            'superdesk/data/data',
            'superdesk/datetime/datetime',
            'superdesk/filters/all',
            'superdesk/services/all',
            'superdesk/directives/all'
        ], function() {
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
                'test'
            ];

            var deps = [];
            angular.forEach(apps, function(app) {
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
