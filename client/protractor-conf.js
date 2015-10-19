'use strict';

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
    baseUrl: 'http://localhost:9090',
    params: {
        baseBackendUrl: 'http://localhost:5000/api/',
        username: 'admin',
        password: 'admin'
    },

    specs: ['spec/**/*[Ss]pec.js'],

    framework: 'jasmine2',
    jasmineNodeOpts: {
        showColors: true,
        defaultTimeoutInterval: 120000
    },

    capabilities: {
        browserName: 'chrome',
        chromeOptions: getChromeOptions()
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
