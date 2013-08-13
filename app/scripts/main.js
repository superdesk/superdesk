require.config({
    paths: {
        angular: 'bower_components/angular/angular',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        jquery: 'bower_components/jquery/jquery',
        bootstrap: 'bower_components/bootstrap/js',
    },
    shim: {
        angular: {
            deps: ['jquery'],
            exports: 'angular'
        },
        'angular-resource': {
            deps: ['angular']
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
    'superdesk/auth/module',
    'superdesk/items/module'
], function(angular) {
    'use strict';

    var application = angular.module('superdesk', [
        'superdesk.auth',
        'superdesk.items'
    ]);

    angular.bootstrap(document, ['superdesk']);
});
