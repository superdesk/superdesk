'use strict';

exports.login = login;
exports.open = openUrl;
exports.changeUrl = changeUrl;
exports.printLogs = printLogs;
exports.waitForSuperdesk = waitForSuperdesk;

// construct url from uri and base url
exports.constructUrl = function(base, uri) {
    return base.replace(/\/$/, '') + uri;
};

var Q = require('q');
var LoginModal = require('./pages').login;

// authenticate if needed
function login() {
    var modal = new LoginModal();
    return modal.btn.isDisplayed()
        .then(function(needLogin) {
            if (needLogin) {
                return modal.login('admin', 'admin');
            }
        });
}

// open url and authenticate
function openUrl(url) {
    return browser.driver.get(browser.baseUrl)
        .then(waitForSuperdesk)
        .then(login)
        .then(waitForSuperdesk)
        .then(function() {
            return browser.get(url);
        }).then(waitForSuperdesk).then(
            function() {
                return Q.defer().resolve();
            },
            function(err) {
                console.log('catched error from waitForSuperdesk in openUrl.');
                return Q.defer().reject(err);
            }
    );
}

// open url
function changeUrl(url) {
    return browser.get(url).then(waitForSuperdesk).then(
            function() {
                return Q.defer().resolve();
            },
            function(err) {
                console.log('catched error from waitForSuperdesk in changeUrl.');
                return Q.defer().reject(err);
            }
    );
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

var clientSideScripts = require('./../../node_modules/protractor/lib/clientsidescripts.js');
function waitForAngular(opt_description) {
  var description = opt_description ? ' - ' + opt_description : '';
  var self = browser;
  var doWork = function() {
    return self.executeAsyncScript_(
      clientSideScripts.waitForAngular,
      'Protractor.waitForAngular()' + description,
      self.rootEl).
      then(function(browserErr) {
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
        return Q.defer().reject(err);
        //throw 'Timed out waiting for Protractor to synchronize with ' +
            //'the page after ' + timeout + '. Please see ' +
            //'https://github.com/angular/protractor/blob/master/docs/faq.md';
      } else {
        return Q.defer().reject(err);
      }
    });
  };
  return doWork();
}

function waitForSuperdesk() {
    return browser.driver.wait(function() {
        return browser.driver.executeScript('return window.superdeskIsReady || false');
    }, 5000, '"window.superdeskIsReady" is not here').then(function() {
        return waitForAngular();
    }).then(
        function() {
            return Q.defer().resolve();
        },
        function(err) {
            console.log('catched error from waitForAngular in waitForSuperdesk:');
            console.log(err);
            console.log(err.message);
            return Q.defer().reject(err);
        }
    );
}
