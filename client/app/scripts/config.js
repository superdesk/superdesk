
require.config({
    baseUrl: './scripts/',
    paths: {
        d3: 'bower_components/d3/d3',
        jquery: 'bower_components/jquery/dist/jquery',
        lodash: 'bower_components/lodash/lodash',
        angular: 'bower_components/angular/angular',
        moment: 'bower_components/momentjs/moment',
        bower_components: 'bower_components/',

        'angular-ui': 'bower_components/angular-bootstrap/ui-bootstrap-tpls',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',
        'angular-mocks': 'bower_components/angular-mocks/angular-mocks',
        'angular-file-upload': 'bower_components/ng-file-upload/angular-file-upload',
        'angular-file-upload-shim': 'bower_components/ng-file-upload/angular-file-upload-shim',
        'moment-timezone': 'bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020',

        'raven-js': 'bower_components/raven-js/dist/raven'
    },
    shim: {
        jquery: {exports: 'jQuery'},
        d3: {exports: 'd3'},

        angular: {
            deps: ['jquery'],
            exports: 'angular'
        },

        'raven-js': {exports: 'Raven'},
        'angular-resource': ['angular'],
        'angular-route': ['angular'],
        'angular-gettext': ['angular'],
        'angular-mocks': ['angular'],
        'angular-file-upload': ['angular', 'angular-file-upload-shim'],

        'translations': ['angular-gettext'],
        'angular-ui': ['angular'],

        'bower_components/jcrop/js/jquery.Jcrop': ['jquery']
    }
});
