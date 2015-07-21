
'use strict';
var openUrl = require('./helpers/utils').open,
    masterDesks = require('./helpers/master_desks'),
    authoring = require('./helpers/authoring');

describe('Master Desk', function() {
    beforeEach(function(done) {
        openUrl('/#/desks/').then(done);
    });

    function itemHeadline(x, y, z) {
        return masterDesks.getItem(x, y, z).element(by.css('.headline')).getText();
    }

    it('show content view', function() {
        masterDesks.switchToTab('content');
        expect(itemHeadline(0, 1, 0)).toBe('item3');
        expect(itemHeadline(0, 3, 0)).toBe('item4');
        expect(itemHeadline(1, 1, 0)).toBe('item5');
        expect(itemHeadline(1, 2, 0)).toBe('item6');
    });

    it('show content view - preview item', function() {
        masterDesks.switchToTab('content');
        masterDesks.previewItem(0, 1, 0);
        expect(authoring.lock.isDisplayed()).toBe(true);
    });

    it('show content view - edit item', function() {
        masterDesks.switchToTab('content');
        masterDesks.editItem(0, 1, 0);
        expect(authoring.publish.isDisplayed()).toBe(true);
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
        expect(masterDesks.getTask(0, 0, 0).element(by.tagName('div')).getText()).toContain('item3 slugline');
        expect(masterDesks.getTask(0, 2, 0).element(by.tagName('div')).getText()).toContain('item4 slugline');
        expect(masterDesks.getTask(1, 0, 0).element(by.tagName('div')).getText()).toContain('item5 slugline');
        expect(masterDesks.getTask(1, 1, 0).element(by.tagName('div')).getText()).toContain('item6 slugline');
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

    it('show user role view all users', function() {
        masterDesks.switchToTab('users');
        expect(masterDesks.getUser(0, 1, 0).element(by.className('text')).getText())
            .toContain('first name last name');
        expect(masterDesks.getUser(0, 2, 0).element(by.className('text')).getText())
            .toContain('first name1 last name1');
        expect(masterDesks.getUser(0, 3, 0).element(by.className('text')).getText())
            .toContain('first name2 last name2');
        expect(masterDesks.getUser(0, 3, 1).element(by.className('text')).getText())
            .toContain('first name3 last name3');
        expect(masterDesks.getUser(1, 2, 0).element(by.className('text')).getText())
            .toContain('first name1 last name1');
    });

    it('show user role view online users', function() {
        masterDesks.switchToTab('users');
        masterDesks.toggleOnlineUsers();
        expect(masterDesks.getUser(0, 1, 0).element(by.className('text')).getText())
            .toContain('first name last name');
        expect(masterDesks.getUser(1, 1, 0).element(by.className('text')).getText())
            .toContain('first name last name');
        expect(masterDesks.getUsersCount(0, 0)).toBe(0);
        expect(masterDesks.getUsersCount(0, 1)).toBe(1);
        expect(masterDesks.getUsersCount(0, 2)).toBe(0);
        expect(masterDesks.getUsersCount(1, 0)).toBe(0);
        expect(masterDesks.getUsersCount(1, 1)).toBe(1);
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

    it('user role view - edit user', function() {
        masterDesks.switchToTab('users');
        masterDesks.editUser(0, 1, 0);
        browser.sleep(200);
        expect(element(by.className('modal-content')).isDisplayed()).toBe(true);
    });
});
