
require.config({
    baseUrl: './scripts/',
    paths: {
        jquery: 'bower_components/jquery/dist/jquery',
        lodash: 'bower_components/lodash/lodash',
        angular: 'bower_components/angular/angular',
        bower_components: 'bower_components/',

        'angular-ui': 'bower_components/angular-bootstrap/ui-bootstrap-tpls',
        'angular-resource': 'bower_components/angular-resource/angular-resource',
        'angular-route': 'bower_components/angular-route/angular-route',
        'angular-gettext': 'bower_components/angular-gettext/dist/angular-gettext',
        'angular-mocks': 'bower_components/angular-mocks/angular-mocks',
        'angular-file-upload': 'bower_components/ng-file-upload/angular-file-upload',
        'angular-file-upload-shim': 'bower_components/ng-file-upload/angular-file-upload-shim',

        'raven-js': 'bower_components/raven-js/dist/raven'
    },
    shim: {
        jquery: {exports: 'jQuery'},

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
