/**
 * Actively wait for an element present and displayed up to specTimeoutMs
 * ignoring useless webdriver errors like StaleElementError.
 *
 * Usage:
 * Add `require('./waitReady.js');` in your onPrepare block or file.
 *
 * @example
 * expect($('.some-html-class').waitReady()).toBeTruthy();
 */
'use strict';

var ElementFinder = $('').constructor;

ElementFinder.prototype.waitReady = function(optStr) {
    var self = this;
    var specTimeoutMs = browser.allScriptsTimeout * 2;
    var driverWaitIterations = 0;
    var lastWebdriverError;
    function _throwError() {
        throw new Error('Expected "' + self.locator().toString() +
            '" to be present and visible. ' +
            'After ' + driverWaitIterations + ' driverWaitIterations. ' +
            'Last webdriver error: ' + lastWebdriverError);
    }

    function _isPresentError(err) {
        lastWebdriverError = (err != null) ? err.toString() : err;
        return false;
    }

    return browser.driver.wait(function() {
        driverWaitIterations++;
        if (optStr === 'withRefresh') {
            // Refresh page after more than some retries
            if (driverWaitIterations > 7) {
                _refreshPage();
            }
        }
        return self.isPresent().then(function(present) {
            if (present) {
                return self.isDisplayed().then(function(visible) {
                    lastWebdriverError = 'visible:' + visible;
                    return visible;
                }, _isPresentError);
            } else {
                lastWebdriverError = 'present:' + present;
                return false;
            }
        }, _isPresentError);
    }, specTimeoutMs).then(function(waitResult) {
        if (!waitResult) {
            _throwError();
        }
        return self;
    }, function(err) {
        _isPresentError(err);
        _throwError();
        return false;
    });
};

// Helpers
function _refreshPage() {
    // Swallow useless refresh page webdriver errors
    browser.navigate().refresh().then(function() {}, function(e) {});
}
