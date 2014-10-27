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
    'superdesk/superdesk'
], function(gettext, angular, superdesk) {
    'use strict';

    return function bootstrap(config, apps) {

        apps.unshift(superdesk.name);
        superdesk.constant('config', config);

        // load apps & bootstrap
        var body = angular.element('body');
        body.ready(function() {
            try {
                angular.bootstrap(body, apps);
            } catch (err) {
                console.error(err.message);
            }
        });
    };
});
