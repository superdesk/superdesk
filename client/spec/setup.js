'use strict';

/* global beforeEach */

var getToken = require('./helpers/auth').getToken;
var resetApp = require('./helpers/fixtures').resetApp;

// runs before every spec
beforeEach(function(done) {
	browser.driver.manage().window().setSize(1280, 800);
    getToken(function() {
        resetApp(function() {
            browser.driver.get(browser.baseUrl)
            .then(function() {
                return browser.driver.executeScript('sessionStorage.clear();localStorage.clear();');
            }).then(function() {
                return browser.driver.wait(function() {
                    return browser.driver.executeScript('return window.superdeskIsReady || false');
                });
            }).then(function () {
                return browser.waitForAngular();
            }).then(done);
        });
    });
});
