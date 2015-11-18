/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

define([
    'angular',
    'require',

    'angular-ui',
    'angular-route',
    'angular-resource',

    './datetime/datetime',
    './ui/ui',
    './directives/all',
    './services/modalService',
    './config/config'

], function(angular, require) {
    'use strict';

    var modules = [
        'ngRoute',
        'ngResource',
        'ui.bootstrap',

        require('./datetime/datetime').name,
        require('./ui/ui').name,
        require('./services/modalService').name
    ];

    modules.push.apply(modules, require('./directives/all'));

    var app = angular.module('superdesk.docs.core', modules);

    return app;
});
