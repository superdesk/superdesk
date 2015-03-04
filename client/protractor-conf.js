'use strict';

var ScreenShotReporter = require('protractor-screenshot-reporter');

exports.config = {
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
    restartBrowserBetweenTests: process.env.bamboo_working_directory || false, // any bamboo env var will do
    framework: 'jasmine',
    jasmineNodeOpts: {
        showColors: true,
        isVerbose: true,
        includeStackTrace: true
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

        function Reporter() {
            var printLogs = require('./spec/helpers/utils').printLogs;
            this.reportSpecResults = function(spec) {
                if (!spec.results().passed()) {
                    browser.getCurrentUrl().then(function(url) {
                        console.log('url: ' + url);
                    });
                    printLogs('fail');
                }
            };
        }

        jasmine.getEnv().addReporter(new Reporter());
    }
};
