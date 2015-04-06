
'use strict';
var openUrl = require('./helpers/utils').open;

function MasterDesks() {
    this.switchToTab = function(name) {
        element(by.id(name)).click();
    };

    this.getDesk = function(desk) {
        return element.all(by.repeater('desk in desks._items')).get(desk);
    };

    this.getStage = function(desk, stage) {
        return this.getDesk(desk).all(by.repeater('stage in deskStages[desk._id]')).get(stage);
    };

    this.getItem = function(desk, stage, item) {
        return this.getStage(desk, stage).all(by.repeater('item in items')).get(item);
    };

    this.getStatus = function(desk, status) {
        return this.getDesk(desk).all(by.repeater('status in statuses')).get(status);
    };

    this.getTask = function(desk, status, task) {
        return this.getStatus(desk, status).all(by.repeater('item in items')).get(task);
    };

    this.getRole = function(desk, role) {
        return this.getDesk(desk).all(by.repeater('role in roles')).get(role);
    };

    this.getUser = function(desk, role, user) {
        return this.getRole(desk, role).all(by.repeater('item in items')).get(user);
    };

    this.goToDesk = function(desk) {
        this.getDesk(desk).element(by.className('icon-external')).click();
    };

    this.editDesk = function(desk) {
        this.getDesk(desk).element(by.className('icon-dots')).click();
        this.getDesk(desk).element(by.className('icon-pencil')).click();
    };
}

var masterDesks = new MasterDesks();

describe('Master Desk', function() {
    beforeEach(function(done) {openUrl('/#/desks/').then(done);});

    it('show content view', function() {
        masterDesks.switchToTab('content');
        expect(masterDesks.getItem(0, 1, 0).element(by.tagName('span')).getText()).toContain('ITEM3 SLUGLINE');
        expect(masterDesks.getItem(0, 3, 0).element(by.tagName('span')).getText()).toContain('ITEM4 SLUGLINE');
        expect(masterDesks.getItem(1, 1, 0).element(by.tagName('span')).getText()).toContain('ITEM5 SLUGLINE');
        expect(masterDesks.getItem(1, 2, 0).element(by.tagName('span')).getText()).toContain('ITEM6 SLUGLINE');
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

    it('show user role view', function() {
        masterDesks.switchToTab('users');
        expect(masterDesks.getUser(0, 0, 0).element(by.className('text')).getText()).toContain('first name last name');
        expect(masterDesks.getUser(0, 1, 0).element(by.className('text')).getText()).toContain('first name2 last name2');
        expect(masterDesks.getUser(0, 1, 1).element(by.className('text')).getText()).toContain('first name3 last name3');
        expect(masterDesks.getUser(0, 2, 0).element(by.className('text')).getText()).toContain('first name1 last name1');
        expect(masterDesks.getUser(1, 2, 0).element(by.className('text')).getText()).toContain('first name1 last name1');
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
