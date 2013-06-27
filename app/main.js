require.config({
    paths: {
        angular: 'components/angular/angular',
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
        }
    }
});

define([
    'angular',
    'bootstrap/bootstrap-dropdown',
    'superdesk/items/module'
], function(angular) {
    'use strict';

    angular.module('superdesk', ['superdesk.items']);
    angular.bootstrap(document, ['superdesk']);
});
