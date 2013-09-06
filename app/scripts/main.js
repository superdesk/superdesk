require.config({
    paths: {
        jquery: 'bower_components/jquery/jquery',
        bootstrap: 'bower_components/bootstrap/js',
        angular: 'bower_components/angular/angular',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
    },
    shim: {
        jquery: {
            exports: 'jQuery'
        },
        angular: {
            deps: ['jquery'],
            exports: 'angular'
        },
        'angular-resource': {
            deps: ['angular']
        },
        'angular-route': {
            deps: ['angular']
        },
        'bootstrap/dropdown': {
            deps: ['jquery']
        },
        'bootstrap/modal': {
            deps: ['jquery']
        }
    }
});

define([
    'angular',
    'superdesk/auth/module',
    'superdesk/items/module'
], function(angular) {
    'use strict';

    var modules = [
        'superdesk.auth',
        'superdesk.items'
    ];

    angular.module('superdesk', modules);
    angular.bootstrap(document, ['superdesk']);
});
