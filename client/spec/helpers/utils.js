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
        return browser.get('/')
            .then(wait)
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
        if (browserLog.length) {
            console.log(prefix + 'log: ' + require('util').inspect(browserLog));
        }
    });
}
