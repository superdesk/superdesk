'use strict';

var backendRequestAuth = require('./backend').backendRequestAuth;

exports.resetApp = resetApp;
exports.post = post;

function resetApp(profile, callback) {
    backendRequestAuth({
        uri: '/prepopulate',
        method: 'POST',
        json: {'profile': profile}
    }, function(e, r, j) {
        browser.params.token = null;
        callback(e, r, j);
    });
}

function post(params, callback) {
    params.method = 'POST';
    backendRequestAuth(params, callback);
}
