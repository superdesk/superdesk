require.config({
    paths: {
        jquery: 'bower_components/jquery/jquery',
        bootstrap: 'bower_components/bootstrap/js',
        bootstrap_ui: 'bower_components/angular-bootstrap/ui-bootstrap',
        angular: 'bower_components/angular/angular',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'moment': 'bower_components/momentjs/moment',
        'restangular': 'bower_components/restangular/dist/restangular',
        'lodash': 'bower_components/lodash/dist/lodash',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',

        'file-upload' : 'bower_components/blueimp-file-upload/js/',
        'canvas-to-blob' : 'bower_components/blueimp-canvas-to-blob/js/canvas-to-blob',
        'load-image': 'bower_components/blueimp-load-image/js/load-image',
        'load-image-meta': 'bower_components/blueimp-load-image/js/load-image-meta',
        'load-image-exif': 'bower_components/blueimp-load-image/js/load-image-exif',
        'load-image-ios': 'bower_components/blueimp-load-image/js/load-image-ios',
        'jquery.ui.widget': 'bower_components/blueimp-file-upload/js/vendor/jquery.ui.widget'
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
        'angular-gettext': {
            deps: ['angular']
        },
        'translations': {
            deps: ['angular-gettext']
        },
        'bootstrap/dropdown': {
            deps: ['jquery']
        },
        'bootstrap/modal': {
            deps: ['jquery']
        },
        'bootstrap_ui': {
            deps: ['angular']
        },
        'restangular': {
            deps: ['lodash']
        }
    }
});

/**
 * Noop for registering string for translation in js files.
 *
 * This is supposed to be used in angular config phase,
 * where we can't use the translate service.
 *
 * @param {string} input
 * @return {string} unmodified input
 */
function gettext(input)
{
    return input;
}

define([
    'angular',
    'superdesk/services/translate',
    'superdesk/auth/module',
    'superdesk/menu/module',
    'superdesk/dashboard/module',
    'superdesk/items/module',
    'superdesk/users/module',
    'superdesk/profile/module'
], function(angular) {
    'use strict';

    angular.module('superdesk.directives', []);

    require(['superdesk/directives/all'], function() {
        var modules = [
            'superdesk.directives',
            'superdesk.services.translate',
            'superdesk.auth',
            'superdesk.menu',
            'superdesk.dashboard',
            'superdesk.items',
            'superdesk.users',
            'superdesk.profile'
        ];

        angular.element(document).ready(function() {
            angular.bootstrap(document, modules);
        });
    });
});
