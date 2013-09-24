module.exports = function(config) {
    config.set({
        frameworks: [
            'jasmine',
            'requirejs'
        ],

        // list of files / patterns to load in the browser
        files: [
          {pattern: 'app/**/*.js', included: false},
          {pattern: 'test/**/*Spec.js', included: false},
          'test/test-main.js'
        ],

        // list of files to exclude
        exclude: [
          'app/main.js'
        ],

        // test results reporter to use
        reporters: ['progress'],

        // web server port
        port: 8080,

        // cli runner port
        runnerPort: 9100,

        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,

        // Start these browsers, currently available:
        browsers: ['Firefox'],

        // If browser does not capture in given timeout [ms], kill it
        captureTimeout: 60000,

        // Continuous Integration mode
        singleRun: false
  });
};
