'use strict';

/* global beforeEach */

var getToken = require('./auth').getToken;
var resetApp = require('./fixtures').resetApp;
var waitForSuperdesk = require('./utils').waitForSuperdesk;

function clearStorage() {
    return browser.driver.executeScript('sessionStorage.clear();localStorage.clear();');
}

module.exports = function(params) {
    // runs before every spec
    beforeEach(function(done) {
        require('./waitReady');
        browser.driver.manage().window().setPosition(0, 0);
        browser.driver.manage().window().setSize(1366, 768);
        getToken(function() {
            resetApp(params.fixture_profile, function() {
                browser.driver.get(browser.baseUrl)
                    .then(clearStorage)
                    .then(waitForSuperdesk)
                    .then(assertWindowSize)
                    .then(done);
            });
        });
    });
};

function assertWindowSize() {
    browser.driver.manage().window().getSize()
        .then(function(size) {
            console.assert(size.height >= 768, 'height is ' + size.height);
            console.assert(size.width >= 1366, 'width is ' + size.width);
        });
}
