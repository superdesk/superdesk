'use strict';

exports.login = login;
exports.open = openUrl;
exports.changeUrl = changeUrl;
exports.printLogs = printLogs;
exports.waitForSuperdesk = waitForSuperdesk;
exports.nav = nav;

// construct url from uri and base url
exports.constructUrl = function(base, uri) {
    return base.replace(/\/$/, '') + uri;
};

var webdriver = require('selenium-webdriver');
var LoginModal = require('./pages').login;
var path = require('path');

// authenticate if needed
function login(username, password) {
    username = username || 'admin';
    password = password || 'admin';
    var modal = new LoginModal();
    return modal.btn.isDisplayed()
        .then(function(needLogin) {
            if (needLogin) {
                return modal.login(username, password);
            }
        });
}

// open url
function changeUrl(url) {
    return browser.get(url).then(waitForSuperdesk).then(
            function() {
                return webdriver.promise.fulfilled();
            },
            function(err) {
                console.log('WARNING: catched error from waitForSuperdesk ' +
                    'in changeUrl.');
                console.log(err);
                console.log('trying again...');
                return browser.sleep(500).then(function() {
                    return changeUrl(url);
                });
            }
    );
}

// open url and authenticate
function openUrl(url) {
    return browser.get(url)
        .then(login)
        .then(waitForSuperdesk);
}

function printLogs(prefix) {
    prefix = prefix ? (prefix + ' ') : '';
    return browser.manage().logs().get('browser').then(function(browserLog) {
        var logs = browserLog.filter(function(log) {
            return log.level.value >= 1000;
        });

        console.log(prefix + 'log: ' + require('util').inspect(logs, {dept: 3}));
    });
}

var clientSideScripts = require(path.resolve('node_modules') + '/protractor/lib/clientsidescripts.js');
function waitForAngular(_description) {
    var description = _description ? ' - ' + _description : '';

    function doWork() {
        return browser.executeAsyncScript_(
            clientSideScripts.waitForAngular,
            'Protractor.waitForAngular()' + description,
            browser.rootEl
        ).then(function(browserErr) {
            if (browserErr) {
                throw 'Error while waiting for Protractor to ' +
                      'sync with the page: ' + JSON.stringify(browserErr);
            }
        }).then(null, function(err) {
            var timeout;
            if (/asynchronous script timeout/.test(err.message)) {
                // Timeout on Chrome
                timeout = /-?[\d\.]*\ seconds/.exec(err.message);
            } else if (/Timed out waiting for async script/.test(err.message)) {
                // Timeout on Firefox
                timeout = /-?[\d\.]*ms/.exec(err.message);
            } else if (/Timed out waiting for an asynchronous script/.test(err.message)) {
                // Timeout on Safari
                timeout = /-?[\d\.]*\ ms/.exec(err.message);
            }
            if (timeout) {
                console.log('WARNING: rejected because of timeout.');
                return webdriver.promise.rejected(err);
                //throw 'Timed out waiting for Protractor to synchronize with ' +
                    //'the page after ' + timeout + '. Please see ' +
                    //'https://github.com/angular/protractor/blob/master/docs/faq.md';
            } else {
                console.log('WARNING: rejected because of error.');
                return webdriver.promise.rejected(err);
            }
        });
    }

    return doWork();
}

function waitForSuperdesk() {
    return browser.driver.wait(function() {
        return browser.driver.executeScript('return window.superdeskIsReady || false');
    }, 5000, '"window.superdeskIsReady" is not here').then(function() {
        return waitForAngular();
    }).then(
        function() {
            return webdriver.promise.fulfilled();
        },
        function(err) {
            console.log('WARNING: catched error from waitForAngular ' +
                'in waitForSuperdesk:');
            console.log(err.message);
            //console.log(err.stack.replace('\\n', '\n'));
            return webdriver.promise.rejected(err);
        }
    );
}

/**
 * Navigate to given location.
 *
 * Unlinke openUrl it doesn't reload the page, only changes #hash in url
 *
 * @param {string} location Location where to navigate without # (eg. users, workspace/content)
 * @return {Promise}
 */
function nav(location) {
    return login().then(function() {
        browser.setLocation(location);
    });
}
