define([
    'angular',
    'require',

    'angular-ui',
    'angular-route',
    'angular-resource',
    'angular-file-upload',

    './api/api',
    './auth/auth',
    './config/config',
    './datetime/datetime',
    './error/error',
    './notify/notify',
    './upload/upload',
    './beta/beta',
    './activity/activity',
    './elastic/elastic',

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
        require('./api/api').name,
        require('./auth/auth').name,
        require('./config/config').name,
        require('./datetime/datetime').name,
        require('./error/error').name,
        require('./notify/notify').name,
        require('./upload/upload').name,
        require('./beta/beta').name,
        require('./activity/activity').name,
        require('./elastic/elastic').name
    ];

    modules.push(require('./filters').name);

    // todo(petr): refactor into func based modules
    modules.push.apply(modules, require('./services/all'));
    modules.push.apply(modules, require('./directives/all'));

    return angular.module('superdesk', modules);
});
