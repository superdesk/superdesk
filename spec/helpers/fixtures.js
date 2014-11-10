'use strict';

var backendRequestAuth = require('./backend').backendRequestAuth;

exports.resetApp = resetApp;

function resetApp(callback) {
    backendRequestAuth({
        uri: '/prepopulate',
        method: 'POST',
        json: {
            'Name': 'default',
            'ApplyOnDatabase': true,
            'ApplyOnFiles': true
        }
    }, function(e, r, j) {
        callback(e, r, j);
    });
}
