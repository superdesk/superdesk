exports.config = {
    baseUrl: 'http://localhost:9000/',

    specs: [
        'test/e2e/*spec.js'
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
