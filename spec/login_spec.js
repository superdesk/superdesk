
var Login = require('./pages').login;

describe('login', function() {
    'use strict';

    var modal;

    beforeEach(function() {
        browser.get('/');
        browser.executeScript('sessionStorage.clear();localStorage.clear();');
        modal = new Login();
    });

    it('renders modal on load', function() {
        expect(modal.btn).toBeDisplayed();
    });

    it('can login', function() {
        modal.login('admin', 'admin');
        expect(modal.btn).not.toBeDisplayed();
        expect(browser.getCurrentUrl()).toBe('http://localhost:9090/#/dashboard');
        expect(element(by.binding('UserName')).getText()).toContain('john');
    });

    it('can logout', function() {
        modal.login('admin', 'admin');
        element(by.binding('UserName')).click();
        element(by.buttonText('SIGN OUT')).click();

        protractor.getInstance().sleep(500); // it reloads page
        protractor.getInstance().waitForAngular();

        expect(modal.btn).toBeDisplayed();
        expect(modal.username).toBeDisplayed();
        expect(modal.username.getAttribute('value')).toBe('');
    });

    xit('should not login with wrong credentials', function() {
        browser.get('/');
        modal.login('admin', 'wrongpass');
        expect(modal.btn).toBeDisplayed();
        expect($('.error')).toBeDisplayed();
    });
});
