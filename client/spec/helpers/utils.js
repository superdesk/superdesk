'use strict';

exports.login = login;
exports.open = openUrl;

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
    return browser.sleep(100)
        .then(function() {
            return browser.waitForAngular();
        });
}

// open url and authenticate
function openUrl(url) {
    return function(done) {
        return browser.get('/')
            .then(login)
            .then(wait)
            .then(function() {
                return browser.get(url);
            })
            .then(done);
    };
}
