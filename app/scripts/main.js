require.config({
    paths: {
        jquery: 'bower_components/jquery/jquery',
        bootstrap: 'bower_components/bootstrap/dist/js/bootstrap',
        angular: 'bower_components/angular/angular',
        'angular-ui': 'bower_components/angular-bootstrap/ui-bootstrap',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'moment': 'bower_components/momentjs/moment',
        'moment-timezone': 'bower_components/moment-timezone/moment-timezone',
        'restangular': 'bower_components/restangular/dist/restangular',
        'lodash': 'bower_components/lodash/dist/lodash',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',

        'file-upload' : 'bower_components/blueimp-file-upload/js/',
        'canvas-to-blob' : 'bower_components/blueimp-canvas-to-blob/js/canvas-to-blob',
        'load-image': 'bower_components/blueimp-load-image/js/load-image',
        'load-image-meta': 'bower_components/blueimp-load-image/js/load-image-meta',
        'load-image-exif': 'bower_components/blueimp-load-image/js/load-image-exif',
        'load-image-ios': 'bower_components/blueimp-load-image/js/load-image-ios',
        'jquery.ui.widget': 'bower_components/blueimp-file-upload/js/vendor/jquery.ui.widget',

        'gridster': 'bower_components/gridster/dist/jquery.gridster.with-extras',
        'd3': 'bower_components/d3/d3',

        'ng-aloha-editor': 'bower_components/ng-aloha-editor/',
        'aloha': 'bower_components/ng-aloha-editor/libs/alohaeditor-0.23.26/aloha/lib/aloha'
    },
    shim: {
        jquery: {
            exports: 'jQuery'
        },
        bootstrap: {
            deps: ['jquery']
        },
        angular: {
            deps: ['jquery'],
            exports: 'angular'
        },
        'angular-ui': {
            deps: ['angular', 'bootstrap']
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
        },
        'gridster': {
            deps: ['angular']
        },
        d3: {
            exports: 'd3'
        }
    }
});

/*jshint -W098 */
/**
 * Noop for registering string for translation in js files.
 *
 * This is supposed to be used in angular config phase,
 * where we can't use the translate service.
 *
 * @param {string} input
 * @return {string} unmodified input
 *
 */
function gettext(input)
{
    'use strict';
    return input;
}

define([
    'jquery',
    'lodash',
    'angular',
    'angular-ui',
    'angular-route',
    'angular-gettext',
    'angular-resource',
    'gridster'
], function($, _, angular) {
    'use strict';

    angular.module('superdesk.filters', []);
    angular.module('superdesk.services', []);
    angular.module('superdesk.directives', []);

    // load core components
    require([
        'superdesk/filters/all',
        'superdesk/services/all',
        'superdesk/directives/all'
    ], function() {
        var modules = [
            'gettext',
            'ngRoute',
            'ngResource',
            'ui.bootstrap',
            'blueimp.fileupload',

            'superdesk.filters',
            'superdesk.services',
            'superdesk.directives'
        ];

        var apps = [
            'dashboard',
            'settings',
            'auth',
            'users',
            'desks',
            'items'
        ];

        var deps = [];
        angular.forEach(apps, function(app) {
            deps.push('superdesk-' + app + '/module');
            modules.push('superdesk.' + app);
        });

        // load apps
        require(deps, function() {
            angular.element(document).ready(function() {
                angular.bootstrap(document, modules);
            });
        });
    });
});
