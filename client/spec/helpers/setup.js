'use strict';

/* global beforeEach */

var getToken = require('./auth').getToken;
var resetApp = require('./fixtures').resetApp;
var waitForSuperdesk = require('./utils').waitForSuperdesk;

function clearStorage() {
    return browser.driver.executeScript('sessionStorage.clear();localStorage.clear();');
}

function openBaseUrl() {
    return browser.driver.get(browser.baseUrl);
}

function resize(width, height) {
    return browser.driver.manage().window().setSize(width, height)
        .then(function() {
            browser.driver.manage().window().getSize()
            .then(function(size) {
                if (size.width === width && size.height === height) {
                    return true;
                } else {
                    return resize(width, height);
                }
            });
        });
}

module.exports = function(params) {
    // runs before every spec
    beforeEach(function(done) {
        require('./waitReady');
        resize(1280, 800)
        .then(function() {
            getToken(function() {
                resetApp(params.fixture_profile, function() {
                    openBaseUrl()
                        .then(clearStorage)
                        .then(openBaseUrl)
                        .then(waitForSuperdesk)
                        .then(done);
                });
            });
        });
    });
};
