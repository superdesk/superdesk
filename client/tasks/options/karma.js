module.exports = {
    options: {
        configFile: 'karma.conf.js',
        singleRun: true,
        autoWatch: false,
        reporters: ['dots', 'coverage']
    },
    single: {
        reporters: 'dots'
    },
    watch: {
        singleRun: false,
        autoWatch: true,
        reporters: 'dots'
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
    },
    bamboo: {
        browsers: ['PhantomJS'],
        reporters: ['dots', 'junit']
    }
};
