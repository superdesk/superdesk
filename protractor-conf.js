exports.config = {
    baseUrl: 'http://localhost:9090/',

    specs: [
        'spec/**/*[Ss]pec.js'
    ],

    capabilities: {
        browserName: 'chrome',
    },

    framework: 'jasmine',

    jasmineNodeOpts: {
        showColors: true,
        isVerbose: false,
        includeStackTrace: false,
        defaultTimeoutInterval: 30000
    }
}
