'use strict';

var backendRequest = require('./backend').backendRequest;
var backendRequestAuth = require('./backend').backendRequestAuth;

exports.post = post;
exports.resetApp = resetApp;

function resetApp(profile, callback) {
    backendRequest({
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
