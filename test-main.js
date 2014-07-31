var tests = [];
var APP_SPEC_REG_EXP = /^\/base\/app\/scripts\/(.*)\.js$/;

for (var file in window.__karma__.files) {
    if (window.__karma__.files.hasOwnProperty(file)) {
        if (/[sS]pec\.js$/.test(file)) {
            var matches = APP_SPEC_REG_EXP.exec(file);
            if (matches && matches.length === 2) {
                tests.push(matches[1]);
            } else {
                tests.push(file);
            }
        }
    }
}

// we have to put here files tested without requirejs
tests.push('superdesk-authoring/widgets/widgets');

requirejs.config({
    baseUrl: '/base/app/scripts',
    deps: ['angular-mocks', 'gettext'],

    callback: function() {
        'use strict';
        require(tests, window.__karma__.start);
    },

    paths: {
        jquery: 'bower_components/jquery/dist/jquery',
        bootstrap: 'bower_components/bootstrap/js',
        angular: 'bower_components/angular/angular',
        moment: 'bower_components/momentjs/moment',
        lodash: 'bower_components/lodash/dist/lodash',
        d3: 'bower_components/d3/d3',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'angular-mocks': 'bower_components/angular-mocks/angular-mocks',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',
        'moment-timezone': 'bower_components/moment-timezone/moment-timezone'
    },

    shim: {
        jquery: {
            exports: 'jQuery'
        },

        angular: {
            exports: 'angular',
            deps: ['jquery']
        },

        'angular-resource': ['angular'],
        'angular-route': ['angular'],
        'angular-mocks': ['angular']
    }
});
