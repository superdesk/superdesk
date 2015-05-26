'use strict';

var chromeOptions = {
    args: ['no-sandbox']
};

if (process.env.CHROME_BIN) {
    chromeOptions.binary = process.env.CHROME_BIN;
}

exports.config = {
    allScriptsTimeout: 30000,
    baseUrl: 'http://localhost:9090',
    params: {
        baseBackendUrl: 'http://localhost:5000/api/',
        username: 'admin',
        password: 'admin'
    },
    specs: ['spec/**/*[Ss]pec.js'],
    capabilities: {
        browserName: 'chrome',
        chromeOptions: chromeOptions
    },
    directConnect: true,
    framework: 'jasmine',
    jasmineNodeOpts: {
        showColors: true,
        isVerbose: true,
        includeStackTrace: true,
        defaultTimeoutInterval: 120000
    },
    /* global jasmine */
    onPrepare: function() {
        require('./spec/helpers/setup')({fixture_profile: 'app_prepopulate_data'});
        require('jasmine-reporters');

        jasmine.getEnv().addReporter(
            new jasmine.JUnitXmlReporter('e2e-test-results', true, true)
        );

        if (process.env.SCREENSHOT_DIR) {
            var ScreenShotReporter = require('protractor-screenshot-reporter');
            jasmine.getEnv().addReporter(
                new ScreenShotReporter({
                    baseDirectory: process.env.SCREENSHOT_DIR,
                    takeScreenShotsOnlyForFailedSpecs: true
                })
            );
        }
    }
};
