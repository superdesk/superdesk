'use strict';

var request = require('request'),
    bt = require('btoa');

var constructUrl = require('./utils').constructUrl;

exports.getBackendUrl = getBackendUrl;
exports.backendRequest = backendRequest;
exports.backendRequestAuth = backendRequestAuth;

function getBackendUrl(uri) {
    return constructUrl(browser.params.baseBackendUrl, uri);
}

function backendRequest(params, callback) {
    callback = callback || function() {};
    if (params.uri) {
        params.url = getBackendUrl(params.uri);
        delete params.uri;
    }
    params.rejectUnauthorized = false;
    request(
        params,
        function(error, response, body) {
            if (error) {
                throw new Error(error);
            }
            if (
                (response.statusCode < 200) && (response.statusCode >= 300)
            ) {
                console.log('Request:');
                console.log(response.request.href);
                console.log(response.request);
                console.log('Response:');
                console.log(body);
                throw new Error('Status code: ' + response.statusCode);
            }
            callback(error, response, body);
        }
    );
}

function backendRequestAuth (params, callback) {
    callback = callback || function() {};
    var token = browser.params.token;
    if (token) {
        if (!params.headers) {
            params.headers = {};
        }
        params.headers.authorization = 'Basic ' + bt(token + ':');
    }
    exports.backendRequest(params, callback);
}
