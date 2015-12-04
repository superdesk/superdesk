
'use strict';

var authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring');

var Login = require('./helpers/pages').login;

describe('notifications', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
        monitoring.turnOffWorkingStage(0);
    });

    it('create a new user mention', function() {
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.showComments();
        authoring.writeTextToComment('@admin1 hello');
        browser.sleep(500);

        expect(element.all(by.repeater('comment in comments')).count()).toBe(1);
        expect(element(by.id('unread-count')).getText()).toBe('2');

        element(by.css('button.current-user')).click();
        browser.sleep(500);

        element(by.buttonText('SIGN OUT')).click();

        var modal = new Login();
        modal.login('admin1', 'admin');
        expect(element(by.id('unread-count')).getText()).toBe('3');
        element(by.css('button.current-user')).click();
        browser.sleep(2000);
        expect(element(by.id('unread-count')).getText()).toBe('');

    });

    it('create a new desk mention', function() {
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleDesk(1);
        monitoring.toggleStage(1, 0);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.actionOnItem('Edit', 1, 0);
        authoring.showComments();
        authoring.writeTextToComment('#Sports_Desk hello');
        browser.sleep(500);
        expect(element(by.id('deskNotifications')).getText()).toBe('1');

    });
});
