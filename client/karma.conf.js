'use strict';

module.exports = function(config) {
    config.set({
        frameworks: [
            'jasmine'
        ],

        preprocessors: {
            '**/*.html': ['ng-html2js'],
            '**/superdesk/**/*.js': ['coverage'],
            '**/superdesk-*/**/*.js': ['coverage']
        },

        // list of files / patterns to load in the browser
        files: [
            'app/scripts/bower_components/jquery/dist/jquery.js',
            'app/scripts/bower_components/lodash/lodash.js',
            'app/scripts/bower_components/bootstrap/dist/js/bootstrap.min.js',
            'app/scripts/bower_components/angular/angular.js',
            'app/scripts/bower_components/angular-route/angular-route.js',
            'app/scripts/bower_components/angular-mocks/angular-mocks.js',
            'app/scripts/bower_components/angular-resource/angular-resource.js',
            'app/scripts/bower_components/angular-gettext/dist/angular-gettext.js',
            'app/scripts/bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
            'app/scripts/bower_components/ng-file-upload/angular-file-upload.js',
            'app/scripts/bower_components/momentjs/moment.js',
            'app/scripts/bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020.js',
            'app/scripts/bower_components/angular-moment/angular-moment.js',
            'app/scripts/bower_components/d3/d3.js',
            //'app/scripts/superdesk/mocks.js',
            'app/scripts/superdesk-*/**/*.html',
            'app/scripts/superdesk/**/*.html',

            // activity
            // FIXME: not working
            // 'app/scripts/superdesk/activity/activity.js',
            //'app/scripts/superdesk/activity/activity-chooser-directive.js',
            //'app/scripts/superdesk/activity/activity-list-directive.js',
            //'app/scripts/superdesk/activity/activity-modal-directive.js',
            //'app/scripts/superdesk/activity/superdesk-service_spec.js',
            // analytics
            // NOTE: working! was easy...
            'app/scripts/superdesk/analytics/analytics.js',
            'app/scripts/superdesk/analytics/analytics_spec.js',
            // api
            // FIXME: not working
            // 'app/scripts/superdesk/api/api.js',
            // 'app/scripts/superdesk/api/api-service.js',
            // 'app/scripts/superdesk/api/http-endpoint-factory.js',
            // 'app/scripts/superdesk/api/request-service.js',
            // 'app/scripts/superdesk/api/timeout-interceptor.js',
            // 'app/scripts/superdesk/api/url-resolver-service.js',
            // 'app/scripts/superdesk/api/request-service_spec.js',
            // 'app/scripts/superdesk/api/timeout-interceptor_spec.js',
            // 'app/scripts/superdesk/api/api-service_spec.js',
            // 'app/scripts/superdesk/api/url-resolver_spec.js',
            // beta
            'app/scripts/superdesk/beta/beta.js',
            'app/scripts/superdesk/beta/beta_spec.js',
        ],

        // list of files to exclude
        exclude: [
            'app/scripts/bower_components/**/*[sS]pec.js',
            'app/main.js'
        ],

        ngHtml2JsPreprocessor: {
            stripPrefix: 'app/',
            moduleName: 'superdesk.templates-cache'
        },

        junitReporter: {
            outputFile: 'test-results.xml'
        },

        // test results reporter to use
        reporters: ['dots'],

        // web server port
        port: 8080,

        // cli runner port
        runnerPort: 9100,

        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,

        // Start these browsers, currently available:
        browsers: ['Chrome'],

        // Continuous Integration mode
        singleRun: false
    });
};
