'use strict';

/* global beforeEach */

var resetApp = require('./fixtures').resetApp;

function clearStorage() {
    return browser.driver.executeScript('sessionStorage.clear();localStorage.clear();');
}

function setBrowserSize() {
    var BROWSER_WIDTH = 1366;
    var BROWSER_HEIGHT = 768;

    return browser.driver.manage().window().getSize().then(function(size) {
        if (size.width !== BROWSER_WIDTH || size.height !== BROWSER_HEIGHT) {
            return browser.driver.manage().window().setSize(BROWSER_WIDTH, BROWSER_HEIGHT);
        }
    });
}

module.exports = function(params) {

    // runs before every spec
    beforeEach(function(done) {

        var top = jasmine.getEnv().topSuite();
        var spec = top.children[0].description;
        var specUrl = '?' + spec;
        browser.params.specUrl = specUrl;

        browser.params.backendUrl = browser.params.baseBackendUrl.replace('api', spec + '/api');
        browser.baseUrl = browser.baseUrl.split('?')[0] + specUrl;

        resetApp(params.fixture_profile, function() {
            browser.get(specUrl)
                .then(setBrowserSize)
                .then(clearStorage)
                .then(done);
        });
    });
};
