'use strict';

/*global protractor */

var request = require('request');

var constructUrl = require('./utils').constructUrl;

exports.getBackendUrl = getBackendUrl;
exports.backendRequest = backendRequest;
exports.backendRequestAuth = backendRequestAuth;

function getBackendUrl(uri)
{
    return constructUrl(
        protractor.getInstance().params.baseBackendUrl, uri
    );
}

function backendRequest(params, callback) {
    callback = callback || function() {};
    if (params.uri) {
        params.url = exports.getBackendUrl(params.uri);
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
    var token = protractor.getInstance().params.token;
    if (!token) {
        throw new Error('No auth token');
    }
    if (!params.headers) {
        params.headers = {};
    }
    params.headers.Authorization = token;
    exports.backendRequest(params, callback);
}
