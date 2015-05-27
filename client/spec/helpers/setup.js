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
        browser.driver.manage().window().setSize(1280, 800);
        getToken(function() {
            resetApp(params.fixture_profile, function() {
                browser.driver.get(browser.baseUrl)
                    .then(clearStorage)
                    .then(waitForSuperdesk)
                    .then(done);
            });
        });
    });
};
