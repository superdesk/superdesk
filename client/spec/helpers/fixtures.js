'use strict';

var backendRequest = require('./backend').backendRequest;
var pp = browser.params;

exports.resetApp = resetApp;
exports.post = post;

function resetApp(profile, callback) {
    backendRequest({
        uri: '/prepopulate',
        method: 'POST',
        json: {'profile': profile}
    }, function(e, r, j) {
        console.assert(r.statusCode === 201, r.statusCode);
        pp.token = null;
        callback(e, r, j);
    });
}

function post(params, callback) {
    params.method = 'POST';
    backendRequest(params, callback);
}
