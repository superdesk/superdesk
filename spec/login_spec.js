
var gotoUri = require('./helpers/browser').gotoUri;
var Login = require('./helpers/pages').login;

var pp = protractor.getInstance().params;

describe('login', function() {
    'use strict';

    var modal;

    beforeEach(function() {
        browser.executeScript('sessionStorage.clear();localStorage.clear();');
        gotoUri('/#/');
        modal = new Login();
        protractor.getInstance().waitForAngular();
    });

    it('form renders modal on load', function() {
        expect(modal.btn).toBeDisplayed();
    });

    it('user can log in', function() {
        modal.login('admin', 'admin');
        expect(modal.btn).not.toBeDisplayed();
        expect(browser.getCurrentUrl()).toBe(pp.baseUrl + '/#/workspace');
        element(by.css('button.current-user')).click();
        expect(element(by.css('.user-info .displayname')).getText()).toBe('admin');
    });

    it('user can log out', function() {
        modal.login('admin', 'admin');
        element(by.css('button.current-user')).click();
        element(by.buttonText('SIGN OUT')).click();

        //protractor.getInstance().sleep(2000); // it reloads page @TODO: remove it?
        protractor.getInstance().waitForAngular();

        expect(modal.btn).toBeDisplayed();
        expect(modal.username).toBeDisplayed();
        expect(modal.username.getAttribute('value')).toBe('');
    });

    it('unknown user can\'t log in', function() {
        modal.login('foo', 'bar');
        expect(modal.btn).toBeDisplayed();
        expect(browser.getCurrentUrl()).not.toBe(pp.baseUrl + '/#/workspace');
        expect(modal.error).toBeDisplayed();
    });

});
