module.exports = {
    options: {
        configFile: 'karma.conf.js',
        singleRun: true,
        autoWatch: false,
        reporters: ['dots']
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
        reporters: ['dots']
    },
    bamboo: {
        browsers: ['PhantomJS'],
        reporters: ['dots', 'junit']
    }
};
