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

    var modules = [
        'ngRoute',
        'ngResource',
        'ui.bootstrap',

        'superdesk.datetime',
        'superdesk.ui',
        'superdesk.services.modal',

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

    var app = angular.module('superdesk.docs.core', modules);

    return app;
})();
