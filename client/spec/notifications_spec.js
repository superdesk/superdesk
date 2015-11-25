
'use strict';

var openUrl = require('./helpers/utils').open,
    waitForSuperdesk = require('./helpers/utils').waitForSuperdesk,
    login = require('./helpers/utils').login,
    globalSearch = require('./helpers/search'),
    authoring = require('./helpers/authoring'),
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/content');

var Login = require('./helpers/pages').login;

describe('notifications', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
        monitoring.turnOffWorkingStage(0);
    });

    fit('authoring operations', function() {
        //undo and redo operations by using CTRL+Z and CTRL+y
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.showComments('@admin1 hello');

        element(by.css('button.current-user')).click();

        // wait for sidebar animation to finish
        browser.wait(function() {
            return element(by.buttonText('SIGN OUT')).isDisplayed();
        }, 200);

        element(by.buttonText('SIGN OUT')).click();

        var modal = new Login();
        modal.login('admin1', 'admin');
        expect(savedSearch.element(by.id('unread-count')).getText()).toBe('1');

    });
});
