'use strict';

/* global beforeEach */

var getToken = require('./helpers/auth').getToken;
var resetApp = require('./helpers/fixtures').resetApp;
var waitForSuperdesk = require('./helpers/utils').waitForSuperdesk;

// runs before every spec
beforeEach(function(done) {
	browser.driver.manage().window().setSize(1280, 800);
    getToken(function() {
        resetApp(function() {
            browser.driver.get(browser.baseUrl)
                .then(clearStorage)
                .then(waitForSuperdesk)
                .then(done);
        });
    });
});

function clearStorage() {
    return browser.driver.executeScript('sessionStorage.clear();localStorage.clear();');
}
