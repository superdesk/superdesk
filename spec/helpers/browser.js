'use strict';

/*global protractor, browser */

var utils = require('./utils');
var constructUrl = utils.constructUrl;

var pp = protractor.getInstance().params;

exports.getUrl = getUrl;
exports.gotoUri = gotoUri;

function getUrl(uri) {
    return constructUrl(
        pp.baseUrl, uri
    );
}

// go to app's uri
function gotoUri(uri, callback) {
    callback = callback || function() {};
    var result;
    var url = exports.getUrl(uri);
    browser.getCurrentUrl().then(
        function(currentUrl) {
            if (url === currentUrl) {
                console.log('[BROWSER] refresh page');
                result = browser.refresh();
            } else {
                console.log('[BROWSER] open ' + url);
                result = browser.get(url);
            }
            callback(result);
        }
    );
}
