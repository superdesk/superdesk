module.exports = {
    options: {
        configFile: 'karma.conf.js',
        singleRun: true,
        autoWatch: false,
        reporters: ['dots', 'coverage']
    },
    unit: {
        coverageReporter: {
          type: 'html',
          dir: 'report/'
        }
    },
    travis: {
        browsers: ['PhantomJS'],
        coverageReporter: {
            type: 'lcov',
            dir: 'report/'
        }
    }
};
