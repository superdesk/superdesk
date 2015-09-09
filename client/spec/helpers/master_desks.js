
'use strict';

module.exports = new MasterDesks();

function MasterDesks() {
    this.previewTitle = element(by.className('lightbox-title'));

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

    this.previewItem = function(desk, stage, item) {
        this.getItem(desk, stage, item).click();
        this.getItem(desk, stage, item).element(by.className('icon-external')).click();
    };

    this.editItem = function(desk, stage, item) {
        this.getItem(desk, stage, item).click();
        this.getItem(desk, stage, item).element(by.className('icon-pencil')).click();
        browser.wait(function() {
            return element(by.className('auth-screen')).isDisplayed();
        }, 100); // wait for editor sidebar animation
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

    this.getUsersCount = function(desk, role) {
        return this.getRole(desk, role).all(by.repeater('item in items')).count();
    };

    this.goToDesk = function(desk) {
        this.getDesk(desk).element(by.className('icon-external')).click();
    };

    this.editDesk = function(desk) {
        this.getDesk(desk).element(by.className('icon-dots')).click();
        this.getDesk(desk).element(by.className('icon-pencil')).click();
    };

    this.toggleOnlineUsers = function() {
        element(by.id('online_users')).click();
    };

    this.editUser = function(desk, role, user) {
        this.getUser(desk, role, user).element(by.className('icon-dots-vertical')).click();
        this.getUser(desk, role, user).element(by.className('icon-pencil')).click();
    };
}
