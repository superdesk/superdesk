'use strict';

var ScreenShotReporter = require('protractor-screenshot-reporter');

exports.config = {
    params: {

        baseUrl: 'https://master.sd-test.sourcefabric.org',
        baseBackendUrl: 'https://master.sd-test.sourcefabric.org/api/',
        username: 'admin',
        password: 'admin'

    },
    specs: ['spec/setup.js', 'spec/matchers.js', 'spec/**/*[Ss]pec.js'],
    capabilities: {
        browserName: 'chrome'
    },
    framework: 'jasmine',
    jasmineNodeOpts: {
        showColors: true,
        isVerbose: false,
        includeStackTrace: false,
        defaultTimeoutInterval: 30000
    },
    /* global jasmine */
    onPrepare: function() {
        jasmine.getEnv().addReporter(new ScreenShotReporter({
            baseDirectory: './screenshots',
            pathBuilder:
                function pathBuilder(spec, descriptions, results, capabilities) {
                    return results.passed() + '_' + descriptions.reverse().join('-');
                },
            takeScreenShotsOnlyForFailedSpecs: true
        }));
        require('jasmine-reporters');
        jasmine.getEnv().addReporter(
            new jasmine.JUnitXmlReporter('e2e-test-results', true, true)
        );
    }
};
