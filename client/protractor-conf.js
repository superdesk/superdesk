'use strict';

//var ScreenShotReporter = require('protractor-screenshot-reporter');

exports.config = {
    allScriptsTimeout: 30000,
    baseUrl: 'http://localhost:9090',
    params: {
        baseBackendUrl: 'http://localhost:5000/api/',
        username: 'admin',
        password: 'admin'
    },
    specs: ['spec/setup.js', 'spec/**/*[Ss]pec.js'],
    capabilities: {
        browserName: 'chrome',
        chromeOptions: {
            args: ['--no-sandbox']
        }
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
        /*
        jasmine.getEnv().addReporter(new ScreenShotReporter({
            baseDirectory: './screenshots',
            pathBuilder:
                function pathBuilder(spec, descriptions, results, capabilities) {
                    return results.passed() + '_' + descriptions.reverse().join('-');
                },
            takeScreenShotsOnlyForFailedSpecs: true
        }));
        */
        require('jasmine-reporters');
        jasmine.getEnv().addReporter(
            new jasmine.JUnitXmlReporter('e2e-test-results', true, true)
        );
    }
};
