/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */
(function() {
    'use strict';

    window.bootstrapSuperdesk = function bootstrap(config, apps) {

        angular.module('superdesk.config').constant('config', config);
        angular.module('superdesk').constant('lodash', _);

        angular.module('superdesk')
        // setup default route for superdesk - set it here to avoid it being used in unit tests
        .config(['$routeProvider', function($routeProvider) {
            $routeProvider.when('/', {redirectTo: '/workspace'});
        }]);

        // load apps & bootstrap
        var body = angular.element('body');
        body.ready(function() {
            angular.bootstrap(body, apps, {strictDi: true});
            window.superdeskIsReady = true;
        });
    };
})();
