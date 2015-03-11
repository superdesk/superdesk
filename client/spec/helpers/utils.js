'use strict';

exports.login = login;
exports.open = openUrl;
exports.printLogs = printLogs;

// construct url from uri and base url
exports.constructUrl = function(base, uri) {
    return base.replace(/\/$/, '') + uri;
};

var LoginModal = require('./pages').login;

// authenticate if needed
function login() {
    var modal = new LoginModal();
    return modal.btn.isDisplayed()
        .then(function(needLogin) {
            if (needLogin) {
                return modal.login('admin', 'admin');
            }
        });
}

// wait for login to finish
function wait() {
    return browser.sleep(500)
        .then(function() {
            return browser.waitForAngular();
        });
}

// open url and authenticate
function openUrl(url) {
    return function() {
        return browser.driver.get(browser.baseUrl)
            .then(waitForSuperdesk)
            .then(login)
            .then(wait)
            .then(function() {
                return browser.get(url);
            });
    };
}

function printLogs(prefix) {
    prefix = prefix ? (prefix + ' ') : '';
    return browser.manage().logs().get('browser').then(function(browserLog) {
        var logs = browserLog.filter(function(log) {
            return log.level.value >= 1000;
        });

        console.log(prefix + 'log: ' + require('util').inspect(logs, {dept: 3}));
    });
}

function waitForSuperdesk() {
    return browser.driver.wait(function() {
        return browser.driver.executeScript('return window.superdeskIsReady || false');
    }).then(function() {
        return browser.waitForAngular();
    });
}
