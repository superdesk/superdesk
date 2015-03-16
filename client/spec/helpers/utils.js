'use strict';

exports.login = login;
exports.open = openUrl;
exports.printLogs = printLogs;
exports.waitForSuperdesk = waitForSuperdesk;

// construct url from uri and base url
exports.constructUrl = function(base, uri) {
    return base.replace(/\/$/, '') + uri;
};

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
        }).then(waitForSuperdesk);
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
  var restartCounter = 0;
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
        console.log('WARNING: restarting waitForAngular');
        console.log(err.message);
        console.log(err);
        restartCounter++;
        if (false) {
            return browser.sleep(500).then(doWork);
        } else {
            throw 'Timed out waiting for Protractor to synchronize with ' +
                'the page after ' + timeout + '. Please see ' +
                'https://github.com/angular/protractor/blob/master/docs/faq.md';
        }
      } else {
        throw err;
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
    });
}
