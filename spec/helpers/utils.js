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
    modal.btn.isDisplayed().then(function(needLogin) {
        if (needLogin) {
            modal.login('admin', 'admin');
        }
    });
}

// open url and authenticate
function openUrl(url) {
    return function() {
        browser.get(url);
        login();
    };
}
