require.config({
    paths: {
        angular: 'components/angular/angular',
        ngCookies: 'components/angular-cookies/angular-cookies',
        jquery: 'components/jquery/jquery',
        bootstrap: 'components/bootstrap/js'
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
    /*
    application.run(function(authService){
        
    });
    */

    angular.bootstrap(document, ['superdesk']);
});