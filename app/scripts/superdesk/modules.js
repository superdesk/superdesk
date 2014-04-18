define([
    'angular',
    'require',

    'angular-ui',
    'angular-route',
    'angular-resource',
    'angular-file-upload',

    './auth/auth',
    './data/data',
    './datetime/datetime',
    './error/error',
    './notify/notify',
    './upload/upload',
    './beta/beta',

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
        require('./auth/auth').name,
        require('./data/data').name,
        require('./datetime/datetime').name,
        require('./error/error').name,
        require('./notify/notify').name,
        require('./upload/upload').name,
        require('./beta/beta').name,
        require('./filters').name
    ];

    modules.push.apply(modules, require('./services/all'));
    modules.push.apply(modules, require('./directives/all'));

    return modules;
});
