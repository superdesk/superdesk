module.exports = function(config) {
    config.set({
        frameworks: [
            'jasmine',
            'requirejs'
        ],

        preprocessors: {
            '**/*.html': ['ng-html2js'],
            '**/superdesk/**/*.js': ['coverage'],
            '**/test/*[sS]pec.js': ['coverage']
        },

        // list of files / patterns to load in the browser
        files: [
          'app/scripts/bower_components/jquery/dist/jquery.js',
          'app/scripts/bower_components/angular/angular.js',
          {pattern: 'app/**/*.js', included: false},
          {pattern: 'test/*[sS]pec.js', included: false},
          {pattern: 'app/scripts/superdesk/**/*[sS]pec.js', included: false},
          'app/scripts/superdesk/views/*.html',
          'test/test-main.js'
        ],

        // list of files to exclude
        exclude: [
          'app/scripts/bower_components/**/*[sS]pec.js',
          'app/main.js'
        ],

        ngHtml2JsPreprocessor: {
          stripPrefix: 'app/',
          moduleName: 'templates'
        },

        coverageReporter: {
          type: 'text',
          dir: 'report'
        },

        // test results reporter to use
        reporters: ['progress', 'coverage'],

        // web server port
        port: 8080,

        // cli runner port
        runnerPort: 9100,

        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,

        // Start these browsers, currently available:
        browsers: ['Chrome'],

        // If browser does not capture in given timeout [ms], kill it
        captureTimeout: 60000,

        // Continuous Integration mode
        singleRun: false
  });
};
