'use strict';

var request = require('request');

var getBackendUrl = require('./backend').getBackendUrl;

var pp = browser.params;

exports.getToken = getToken;

// acquire auth token using API
function getToken(callback) {
    var username = pp.username,
        password = pp.password;
    request.post({
            rejectUnauthorized: false,
            url: getBackendUrl('/auth'),
            json: {
                'username': username,
                'password': password
            }
        }, function(error, response, json) {
            if (error) {
                throw new Error(error);
            }
            if (!json.token) {
                console.log(json);
                throw new Error('Auth failed');
            }
            pp.token = json.token;
            callback(error, response, json);
        }
    );
}
