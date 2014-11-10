'use strict';

exports.UUIDv4 = function b(a) {
    return a
        ? (a ^ Math.random() * 16 >> a / 4).toString(16)
        : ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, b);
};

exports.getIdFromHref = function(href) {
    return href.match(/\d+$/g)[0];
};

exports.constructGetParameters = function(data) {
    return '?' + Object.keys(data).map(
        function(key) {
            return [key, data[key]].map(encodeURIComponent).join('=');
    }).join('&');
};

// construct url from uri and base url
exports.constructUrl = function(base, uri) {
    return base.replace(/\/$/, '') + uri;
};
