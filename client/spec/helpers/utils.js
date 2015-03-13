'use strict';

var browserManager = new BrowserManager();

exports.login = LoginModal;
exports.open = openUrl;
exports.printLogs = printLogs;
exports.browserManager = browserManager;

// construct url from uri and base url
exports.constructUrl = function(base, uri) {
    return base.replace(/\/$/, '') + uri;
};

function BrowserManager() {
    var currBrowser = browser;

    this.setBrowser = function(userBrowser) {
        currBrowser = userBrowser;
    };

    this.getBrowser = function() {
        return currBrowser;
    };

    this.getElement = function() {
        return currBrowser.element;
    };
}

function LoginModal() {
    var currBrowser = browserManager.getBrowser();
    this.username = currBrowser.element(by.model('username'));
    this.password = currBrowser.element(by.model('password'));
    this.btn = currBrowser.element(by.id('login-btn'));
    this.error = currBrowser.element(by.css('p.error'));

    this.login = function(username, password) {
        username = username || currBrowser.params.username;
        password = password || currBrowser.params.password;
        this.username.clear();
        this.username.sendKeys(username);
        this.password.sendKeys(password);
        return this.btn.click();
    };
}

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

// wait for login to finish
function wait() {
    var currBrowser = browserManager.getBrowser();
    return currBrowser.sleep(500)
        .then(function() {
            return currBrowser.waitForAngular();
        });
}

// open url and authenticate
function openUrl(url) {
    return function() {
        var currBrowser = browserManager.getBrowser();
        return currBrowser.driver.get(currBrowser.baseUrl)
            .then(waitForSuperdesk)
            .then(login)
            .then(wait)
            .then(function() {
                return currBrowser.get(url);
            });
    };
}

function printLogs(prefix) {
    prefix = prefix ? (prefix + ' ') : '';
    return browserManager.getBrowser().manage().logs().get('browser').then(function(browserLog) {
        var logs = browserLog.filter(function(log) {
            return log.level.value >= 1000;
        });

        console.log(prefix + 'log: ' + require('util').inspect(logs, {dept: 3}));
    });
}

function waitForSuperdesk() {
    var currBrowser = browserManager.getBrowser();
    return currBrowser.driver.wait(function() {
        return currBrowser.driver.executeScript('return window.superdeskIsReady || false');
    }).then(function() {
        return currBrowser.waitForAngular();
    });
}
