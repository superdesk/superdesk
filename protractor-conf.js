exports.config = {
    specs: [
        'test/e2e/*spec.js'
    ],

    capabilities: {
        browserName: 'chrome',
    },

    baseUrl: 'http://localhost:9000/',

    framework: 'jasmine',

    jasmineNodeOpts: {
        showColors: true
    }
}
