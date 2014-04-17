
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
    'require',
    'superdesk/modules',
    'angular-mocks'
], function(angular, require, modules) {
    'use strict';

    angular.module('test', []); // used for mocking
    modules.push('test');

    return function bootstrap(config) {
        angular.module('superdesk', []).constant('config', config);
        modules.push('superdesk');

        // build deps
        var deps = [];
        angular.forEach(config.apps, function(app) {
            deps.push('superdesk-' + app + '/module');
            modules.push('superdesk.' + app);
        });

        // load apps & bootstrap
        require(deps, function() {
            var body = angular.element('body');
            body.ready(function() {
                angular.bootstrap(body, modules);
            });
        });
    };
});
