'use strict';

var maxInstances = process.env.SUPERDESK_TESTING_INSTANCES || 2;

function getChromeOptions() {
    var chromeOptions = {
        args: ['no-sandbox']
    };

    if (process.env.CHROME_BIN) {
        chromeOptions.binary = process.env.CHROME_BIN;
    }

    return chromeOptions;
}

exports.config = {
    baseUrl: 'http://localhost:9090?',
    params: {
        baseBackendUrl: 'http://localhost:5000/api/',
        username: 'admin',
        password: 'admin'
    },

    specs: ['spec/**/*[Ss]pec.js'],
    exclude: ['spec/highlights_spec.js'],

    framework: 'jasmine2',
    jasmineNodeOpts: {
        showColors: true
    },

    capabilities: {
        browserName: 'chrome',
        chromeOptions: getChromeOptions(),
        shardTestFiles: true,
        maxInstances: maxInstances
    },

    directConnect: true,

    onPrepare: function() {
        require('./spec/helpers/setup')({fixture_profile: 'app_prepopulate_data'});
        var reporters = require('jasmine-reporters');
        jasmine.getEnv().addReporter(
            new reporters.JUnitXmlReporter({
                savePath: 'e2e-test-results',
                consolidateAll: true
            })
        );
    }
};
