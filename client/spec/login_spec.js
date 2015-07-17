
var waitForSuperdesk = require('./helpers/utils').waitForSuperdesk;
var Login = require('./helpers/pages').login;

describe('Login', function() {
    'use strict';

    var modal;

    beforeEach(function() {
        modal = new Login();
    });

    it('form renders modal on load', function() {
        expect(modal.btn.isDisplayed()).toBe(true);
    });

    it('user can log in', function() {
        modal.login('admin', 'admin');
        waitForSuperdesk();
        expect(modal.btn.isDisplayed()).toBe(false);
        expect(browser.getCurrentUrl()).toBe(browser.baseUrl + '/#/workspace');
        element(by.css('button.current-user')).click();
        expect(
            element(by.css('.user-info .displayname'))
                .waitReady()
                .then(function(elem) {
                    return elem.getText();
                })
        ).toBe('admin');
    });

    it('user can log out', function() {
        modal.login('admin', 'admin');
        waitForSuperdesk();
        element(by.css('button.current-user')).click();

        // wait for sidebar animation to finish
        browser.wait(function() {
            return element(by.buttonText('SIGN OUT')).isDisplayed();
        }, 200);

        element(by.buttonText('SIGN OUT')).click();

        browser.wait(function() {
            return browser.driver.isElementPresent(by.id('login-btn'));
        }, 5000);
    });

    it('unknown user can\'t log in', function() {
        modal.login('foo', 'bar');
        expect(modal.btn.isDisplayed()).toBe(true);
        expect(browser.getCurrentUrl()).not.toBe(browser.baseUrl + '/#/workspace');
        expect(modal.error.isDisplayed()).toBe(true);
    });
});
