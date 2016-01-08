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
    var win = browser.driver.manage().window();
    return win.getSize().then(function(size) {
        if (size.width !== width || size.height !== height) {
            console.log('resize', size);
            return win.setSize(width, height);
        }
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
