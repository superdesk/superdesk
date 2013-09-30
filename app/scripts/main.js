require.config({
    paths: {
        jquery: 'bower_components/jquery/jquery',
        bootstrap: 'bower_components/bootstrap/js',
        bootstrap_ui: 'bower_components/angular-bootstrap/ui-bootstrap',
        angular: 'bower_components/angular/angular',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'moment': 'bower_components/momentjs/moment'
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
        },
        'bootstrap_ui': {
            deps: ['angular']
        }
    }
});

define([
    'angular',
    'superdesk/l10n/module',
    'superdesk/auth/module',
    'superdesk/menu/module',
    'superdesk/dashboard/module',
    'superdesk/items/module',
    'superdesk/users/module'
], function(angular) {
    'use strict';

    var modules = [
        'superdesk.l10n',
        'superdesk.auth',
        'superdesk.menu',
        'superdesk.dashboard',
        'superdesk.items',
        'superdesk.users'
    ];

    angular.module('superdesk', modules);
    angular.bootstrap(document, ['superdesk']);
});
