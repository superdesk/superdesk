require.config({
    paths: {
        d3: 'bower_components/d3/d3',
        jquery: 'bower_components/jquery/dist/jquery',
        lodash: 'bower_components/lodash/dist/lodash',
        angular: 'bower_components/angular/angular',
        bootstrap: 'bower_components/bootstrap/dist/js/bootstrap',
        moment: 'bower_components/momentjs/moment',
        gridster: 'bower_components/gridster/dist/jquery.gridster.with-extras',

        'angular-ui': 'bower_components/angular-bootstrap/ui-bootstrap',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',
        'angular-mocks': 'bower_components/angular-mocks/angular-mocks',
        'angular-file-upload': 'bower_components/ng-file-upload/angular-file-upload',
        'angular-slider': 'bower_components/angular-slider-royale/angular-slider',

        'moment-timezone': 'bower_components/moment-timezone/moment-timezone',

        'jquery-ui': 'bower_components/jquery-ui/ui/jquery-ui',

        'bootstrap-daterange': 'bower_components/bootstrap-daterangepicker/daterangepicker'
    },
    shim: {
        jquery: {exports: 'jQuery'},
        d3: {exports: 'd3'},

        angular: {
            deps: ['jquery'],
            exports: 'angular'
        },

        'angular-resource': ['angular'],
        'angular-route': ['angular'],
        'angular-gettext': ['angular'],
        'angular-mocks': ['angular'],
        'angular-file-upload': ['angular'],
        'bootstrap_ui': ['angular'],
        'gridster': ['angular'],
        'translations': ['angular-gettext'],
        'angular-ui': ['angular', 'bootstrap'],

        'bootstrap': ['jquery'],
        'jquery-ui': ['jquery'],
        'bootstrap/modal': ['jquery'],
        'bootstrap/dropdown': ['jquery']
    }
});

/* jshint -W098 */
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
    'angular-mocks',
    'angular-file-upload',
    'gridster'
], function($, _, angular) {
    'use strict';

    angular.module('superdesk', []); // todo replace .filters/.directives/.services with superdesk
    angular.module('superdesk.filters', []);
    angular.module('superdesk.services', []);
    angular.module('superdesk.directives', []);
    angular.module('test', []); // used for mocking

    angular.module('superdesk').constant('config', {server: ServerConfig});

    angular.element(document).ready(function() {

        // load core components
        require([
            'superdesk/auth/auth',
            'superdesk/data/data',
            'superdesk/datetime/datetime',
            'superdesk/filters/all',
            'superdesk/services/all',
            'superdesk/directives/all'
        ], function() {
            var modules = [
                'gettext',
                'ngRoute',
                'ngResource',
                'ui.bootstrap',
                'angularFileUpload',

                'superdesk',
                'superdesk.filters',
                'superdesk.services',
                'superdesk.directives',
                'superdesk.auth',
                'superdesk.data',
                'superdesk.datetime',
                'test'
            ];

            // todo(petr): put somewhere in index.html..
            var apps = [
                'dashboard',
                'users',
                'planning'
                //'settings',
                //'desks',
                //'archive',
                //'items',
                //'scratchpad',
            ];

            var deps = [];
            angular.forEach(apps, function(app) {
                deps.push('superdesk-' + app + '/module');
                modules.push('superdesk.' + app);
            });

            // load apps
            require(deps, function() {
                var body = angular.element('body');
                angular.bootstrap(body, modules);
            });
        });
    });
});
