
'use strict';

var openUrl = require('./helpers/utils').open,
    masterDesks = require('./helpers/pages').masterDesks;

describe('Master Desk', function() {
	beforeEach(function(done) {openUrl('/#/desks/').then(done);});

    it('show content view', function() {
    	masterDesks.switchToTab('content');
    	// TODO: add checks
    });

    it('content view - show desk', function() {
    	masterDesks.switchToTab('content');
    	masterDesks.goToDesk(0);
    	expect(browser.getCurrentUrl()).toContain('#/workspace');
    });

    it('content view - edit desk', function() {
    	masterDesks.switchToTab('content');
    	masterDesks.editDesk(0);
    	browser.sleep(200);
    	expect(element(by.className('modal-content')).isDisplayed()).toBe(true);
    });

    it('show tasks view', function() {
    	masterDesks.switchToTab('tasks');
    	// TODO: add checks
    });

    it('tasks view - show desk', function() {
    	masterDesks.switchToTab('tasks');
    	masterDesks.goToDesk(0);
    	expect(browser.getCurrentUrl()).toContain('#/workspace');
    });

    it('tasks view - edit desk', function() {
    	masterDesks.switchToTab('tasks');
    	masterDesks.editDesk(0);
    	browser.sleep(200);
    	expect(element(by.className('modal-content')).isDisplayed()).toBe(true);
    });

    it('show user role view', function() {
    	masterDesks.switchToTab('users');
    	expect(masterDesks.getUser(0, 0, 0).element(by.tagName('div')).getText()).toContain('first name last name');
    	expect(masterDesks.getUser(0, 1, 0).element(by.tagName('div')).getText()).toContain('first name2 last name2');
    	expect(masterDesks.getUser(0, 1, 1).element(by.tagName('div')).getText()).toContain('first name3 last name3');
    	expect(masterDesks.getUser(0, 2, 0).element(by.tagName('div')).getText()).toContain('first name1 last name1');
    	expect(masterDesks.getUser(1, 2, 0).element(by.tagName('div')).getText()).toContain('first name1 last name1');
    });

    it('user role view - show desk', function() {
    	masterDesks.switchToTab('users');
    	masterDesks.goToDesk(0);
    	expect(browser.getCurrentUrl()).toContain('#/workspace');
    });

    it('user role view - edit desk', function() {
    	masterDesks.switchToTab('users');
    	masterDesks.editDesk(0);
    	browser.sleep(200);
    	expect(element(by.className('modal-content')).isDisplayed()).toBe(true);
    });
});
