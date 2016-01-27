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
        reporters: ['dots', 'coverage'],
        coverageReporter: {
            dir: '.',
            includeAllSources: true,
            reporters: [
                {type: 'lcovonly', subdir: '.', file: 'lcov.info'}
            ]
        }
    },
    bamboo: {
        browsers: ['PhantomJS'],
        reporters: ['dots', 'junit']
    }
};
