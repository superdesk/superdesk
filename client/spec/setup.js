'use strict';

/* global beforeEach */

var getToken = require('./helpers/auth').getToken;
var resetApp = require('./helpers/fixtures').resetApp;

// runs before every spec
beforeEach(function(done) {
	browser.driver.manage().window().setSize(1280, 800);
    getToken(function() {
        resetApp(function() {
            browser.get('/').then(function() {
                return browser.executeScript('sessionStorage.clear();localStorage.clear();');
            }).then(done);
        });
    });
});
