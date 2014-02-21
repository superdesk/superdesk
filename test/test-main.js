var tests = [];
for (var file in window.__karma__.files) {
    if (window.__karma__.files.hasOwnProperty(file)) {
        if (/[sS]pec\.js$/.test(file)) {
            tests.push(file);
        }
    }
}

requirejs.config({
    baseUrl: '/base/app/scripts',

    deps: ['angular', 'angular-mocks'],
    callback: function(angular) {
        'use strict';

        angular.module('superdesk', []);
        angular.module('superdesk.filters', []);
        angular.module('superdesk.services', []);
        angular.module('superdesk.directives', []);

        require(tests, function(tests) {
            return window.__karma__.start(tests);
        });
    },

    paths: {
        jquery: 'bower_components/jquery/dist/jquery',
        bootstrap: 'bower_components/bootstrap/js',
        angular: 'bower_components/angular/angular',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'angular-mocks': 'bower_components/angular-mocks/angular-mocks',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',
        'moment': 'bower_components/momentjs/moment',
        'lodash': 'bower_components/lodash/dist/lodash'
    },

    shim: {
        jquery: {
            exports: 'jQuery'
        },
        angular: {
            exports: 'angular',
            deps: ['jquery']
        },
        'angular-resource': {
            deps: ['angular']
        },
        'angular-route': {
            deps: ['angular']
        },
        'angular-mocks': {
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
