/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

// loaded already
define('jquery', [], function() {
    'use strict';
    return window.jQuery;
});

// loaded already
define('angular', [], function() {
    'use strict';
    return window.angular;
});

define('main', [
    'gettext',
    'angular',
    'superdesk/superdesk',
    'lodash'
], function(gettext, angular, superdesk, _) {
    'use strict';

    return function bootstrap(config, apps) {

        apps.unshift(superdesk.name);
        superdesk.constant('config', config);
        superdesk.constant('lodash', _);

        // setup default route for superdesk - set it here to avoid it being used in unit tests
        superdesk.config(['$routeProvider', function($routeProvider) {
            $routeProvider.when('/', {redirectTo: '/workspace'});
        }]);

        // load apps & bootstrap
        var body = angular.element('body');
        body.ready(function() {
            angular.bootstrap(body, apps, {strictDi: true});
            window.superdeskIsReady = true;
        });
    };
});
