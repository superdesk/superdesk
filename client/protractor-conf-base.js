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

var config = {
    allScriptsTimeout: 20000,
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
        defaultTimeoutInterval: 200000
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
        function CustomReporter() {
            this.specDone = function(result) {
                if (result.failedExpectations.length > 0) {
                    var name = result.fullName.split(' ');
                    console.log('at Object.<anonymous> (spec/' + name[0] + '_spec.js:0:0)');
                }
            };
        }
        jasmine.getEnv().addReporter(new CustomReporter());
        browser.driver.manage().timeouts().setScriptTimeout(60000);
    }
};

module.exports = config;
