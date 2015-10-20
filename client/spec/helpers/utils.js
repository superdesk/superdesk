'use strict';

module.exports.route = route;
module.exports.login = login;
module.exports.open = openUrl;
module.exports.changeUrl = changeUrl;
module.exports.printLogs = printLogs;
module.exports.waitForSuperdesk = waitForSuperdesk;
module.exports.nav = nav;
module.exports.getListOption = getListOption;
module.exports.ctrlKey = ctrlKey;
module.exports.altKey = altKey;
module.exports.assertToastMsg = assertToastMsg;

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
        return browser.setLocation(location);
    });
}

/**
 * Nav shortcut for beforeEach, use like `beforeEach(route('/workspace'));`
 *
 * @param {string} location
 * @return {function}
 */
function route(location) {
    return function() {
        nav(location);
    };
}

/**
 * Finds and returns the n-th <option> element of the given dropdown list
 *
 * @param {ElementFinder} dropdown - the <select> element to pick the option from
 * @param {number} n - the option's position in the dropdown's list of options,
 *   must be an integer (NOTE: list positions start with 1!)
 *
 * @return {ElementFinder} the option element itself (NOTE: might not exist)
 */
function getListOption(dropdown, n) {
    var cssSelector = 'option:nth-child(' + n + ')';
    return dropdown.$(cssSelector);
}

/**
 * Performs CTRL + key action
 *
 * @param {char} key
 */
function ctrlKey(key) {
    var Key = protractor.Key;
    browser.actions().sendKeys(Key.chord(Key.CONTROL, key)).perform();
}

/**
 * Performs ALT + key action
 *
 * @param {char} key
 */
function altKey(key) {
    var Key = protractor.Key;
    browser.actions().sendKeys(Key.chord(Key.ALT, key)).perform();
}

/**
 * Asserts that a toast message of a particular type has appeared with its
 * message containing the given string.
 *
 * A workaround with setting the ignoreSyncronization flag is needed due to a
 * protractor issue that does not find DOM elements dynamically displayed in a
 * $timeout callback. More info here:
 *    http://stackoverflow.com/questions/25062748/
 *           testing-the-contents-of-a-temporary-element-with-protractor
 *
 * @param {string} type - type of the toast notificiation ("info", "success" or
 *   "error")
 * @param {string} msg - a string expected to be present in the toast message
 */
function assertToastMsg(type, msg) {
    var cssSelector = '.notification-holder .alert-' + type,
        toast = $(cssSelector);

    browser.sleep(500);
    browser.ignoreSynchronization = true;
    expect(toast.getText()).toContain(msg);
    browser.sleep(500);
    browser.ignoreSynchronization = false;
}
