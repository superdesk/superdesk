define([
    'angular',
    'require',

    'angular-ui',
    'angular-route',
    'angular-resource',
    'angular-file-upload',

    './activity/activity',
    './analytics/analytics',
    './api/api',
    './auth/auth',
    './beta/beta',
    './config/config',
    './datetime/datetime',
    './elastic/elastic',
    './error/error',
    './notify/notify',
    './upload/upload',
    './ui/ui',

    './filters',
    './services/all',
    './directives/all'
], function(angular, require) {
    'use strict';

    var modules = [
        'ngRoute',
        'ngResource',
        'ui.bootstrap',
        'angularFileUpload',

        require('./activity/activity').name,
        require('./analytics/analytics').name,
        require('./api/api').name,
        require('./auth/auth').name,
        require('./beta/beta').name,
        require('./config/config').name,
        require('./datetime/datetime').name,
        require('./elastic/elastic').name,
        require('./error/error').name,
        require('./notify/notify').name,
        require('./upload/upload').name,
        require('./ui/ui').name,

        'superdesk.menu'
    ];

    modules.push(require('./filters').name);

    // todo(petr): refactor into func based modules
    modules.push.apply(modules, require('./services/all'));
    modules.push.apply(modules, require('./directives/all'));

    var app = angular.module('superdesk', modules);

    return app;
});
