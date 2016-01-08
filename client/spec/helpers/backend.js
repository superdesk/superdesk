'use strict';

var request = require('request');
var bt = require('btoa');

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

    function isErrorResponse(response) {
        return response.statusCode < 200 || response.statusCode >= 300;
    }

    // how many times it will try to request before throwing error
    var ttl = 3;

    function responseHandler(error, response, body) {
        if (!error && !isErrorResponse(response)) {
            return callback(error, response, body);
        }

        if (error) {
            console.error('request error', JSON.stringify(error), JSON.stringify(params));
        }

        if (ttl) {
            ttl -= 1;
            params.timeout *= 2;
            return request(params, responseHandler);
        }

        if (!error) {
            console.log('Request:');
            console.log(response.request.href);
            console.log(response.request);
            console.log('Response:');
            console.log(body);
            throw new Error('Status code: ' + response.statusCode);
        }

        throw new Error('Request error=' + JSON.stringify(error) + ' params=' + JSON.stringify(params));
    }

    params.rejectUnauthorized = false;
    params.timeout = 5000;
    request(params, responseHandler);
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
