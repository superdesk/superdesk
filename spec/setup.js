'use strict';

/*global beforeEach, afterEach */

var getToken = require('./helpers/auth').getToken;
var resetApp = require('./helpers/fixtures').resetApp;

// runs before every spec
beforeEach(function(done) {
    getToken(function() {
        resetApp(function() {
            browser.driver.getCurrentUrl().then(function(url) {
                if (url.indexOf('data:') !== 0) {
                    browser.executeScript('sessionStorage.clear();localStorage.clear();');
                    protractor.getInstance().waitForAngular();
                }
                done();
            });
        });
    });
});

// runs after every spec
afterEach(function() {});
