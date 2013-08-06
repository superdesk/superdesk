require.config({
    paths: {
        angular: 'bower_components/angular/angular',
        jquery: 'bower_components/jquery/jquery',
        bootstrap: 'bower_components/bootstrap/js',
    },
    shim: {
        angular: {
            deps: ['jquery'],
            exports: 'angular'
        },
        'bootstrap/bootstrap-dropdown': {
            deps: ['jquery']
        },
        'bootstrap/bootstrap-modal': {
            deps: ['jquery']
        }
    }
});

define([
    'angular',
    'bootstrap/bootstrap-modal',
    'bootstrap/bootstrap-dropdown',
    'superdesk/services/module',
    'superdesk/session/module',
    'superdesk/items/module'
], function(angular) {
    'use strict';

    var application = angular.module('superdesk', [
        'superdesk.services',
        'superdesk.session',
        'superdesk.items'
    ]);

    angular.bootstrap(document, ['superdesk']);
});
