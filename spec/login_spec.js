
var Login = require('./pages').login;

describe('login', function() {
    'use strict';

    var modal;

    beforeEach(function() {
        browser.get('/#/');
        browser.executeScript('sessionStorage.clear();localStorage.clear();');
        browser.get('/#/');
        modal = new Login();
        protractor.getInstance().waitForAngular();
    });

    it('renders modal on load', function() {
        expect(modal.btn).toBeDisplayed();
    });

    xit('can login', function() {
        modal.login('admin', 'admin');
        expect(modal.btn).not.toBeDisplayed();
        expect(browser.getCurrentUrl()).toBe('http://localhost:9090/#/workspace');
        expect(element(by.binding('display_name')).getText()).toBe('John Doe');
    });

    xit('can logout', function() {
        modal.login('admin', 'admin');
        element(by.binding('display_name')).click();
        element(by.buttonText('SIGN OUT')).click();

        protractor.getInstance().sleep(2000); // it reloads page
        protractor.getInstance().waitForAngular();

        expect(modal.btn).toBeDisplayed();
        expect(modal.username).toBeDisplayed();
        expect(modal.username.getAttribute('value')).toBe('');
    });
});
