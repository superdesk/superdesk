
'use strict';

var workspace = require('./helpers/workspace'),
    monitoring = require('./helpers/monitoring'),
    content = require('./helpers/content'),
    authoring = require('./helpers/authoring');

describe('authoring', function() {
    it('can open item stage', function() {
        workspace.open();
        workspace.editItem('item4', 'SPORTS');
        element(by.css('button.stage')).click();
        expect(browser.getCurrentUrl()).toMatch(/workspace\/content/);
    });

    it('Can Undo content', function() {
        var TIMEOUT = 500;

        var ctrl = function(key) {
            var Key = protractor.Key;
            return browser.actions().sendKeys(Key.chord(Key.CONTROL, key)).perform();
        };

        workspace.open();
        workspace.editItem('item4', 'SPORTS');

        authoring.writeText('Two');
        expect(authoring.getBodyText()).toBe('Two');

        browser.sleep(TIMEOUT);

        authoring.writeText('Words');
        expect(authoring.getBodyText()).toBe('TwoWords');

        browser.sleep(TIMEOUT);

        ctrl('z');
        expect(authoring.getBodyText()).toBe('Two');

        browser.sleep(TIMEOUT);

        ctrl('y');
        expect(authoring.getBodyText()).toBe('TwoWords');
    });

    it('view item history create-fetch operation', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item6', 'Politic');

        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(1);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Fetched as \d+ to Politic Desk\/two by.*/);
    });

    it('view item history create-update operations', function() {
        workspace.open();
        authoring.createTextItem();
        authoring.writeTextToHeadline('new item');
        authoring.writeText('some text');
        authoring.save();

        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Story \d+ Created by.*/);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Updated by.*/);
        authoring.close();

        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item5', 'Politic');
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(1);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Story \d+ \(Politic Desk\/one\) Created by.*/);
    });

    it('view item history spike-unspike operations', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.actionOnItem('Spike', 'item5', 'Politic');
        workspace.actionOnItem('Unspike Item', 'item5', 'Politic', 'Spiked');
        workspace.editItem('item5', 'Politic');

        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Spiked from Politic Desk\/one by .*/);
        expect(authoring.getHistoryItem(2).getText()).toMatch(/Unspiked to Politic Desk\/one by .*/);
    });

    it('view item history move operation', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item5', 'Politic');
        authoring.writeText(' ');
        authoring.save();
        expect(authoring.sendToButton.isDisplayed()).toBe(true);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        authoring.sendTo('Politic Desk', 'two');
        authoring.confirmSendTo();
        workspace.selectStage('two');
        workspace.editItem('item5', 'Politic');
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
        expect(authoring.getHistoryItem(2).getText()).toMatch(/Moved to Politic Desk\/two by .*/);
    });

    it('view item history duplicate operation', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.duplicateItem('item5', 'Politic Desk');
        workspace.switchToDesk('SPORTS DESK');
        workspace.switchToDesk('POLITIC DESK');
        workspace.selectStage('New');
        workspace.editItem('item5', 'Politic Desk');
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Copied to \d+ \(Politic Desk\/New\) by .*/);
    });

    it('view item history publish operation', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item5', 'Politic');
        authoring.writeText('some text');
        authoring.save();
        authoring.publish();
        workspace.selectStage('Published');
        workspace.filterItems('composite');
        content.actionOnItem('View item', 0);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        var publishItem = authoring.getHistoryItem(1);
        expect(publishItem.getText()).toMatch(/Published by.*/);
        var queuedSwitch = authoring.getQueuedItemsSwitch(publishItem);
        expect(queuedSwitch.isDisplayed()).toBe(true);
        queuedSwitch.click();
        expect(authoring.getQueuedItems().count()).toBe(1);
    });

    it('allows to create a new empty package', function () {
        monitoring.openMonitoring();
        monitoring.createItemAction('create_package');
        expect(element(by.className('packaging-screen')).isDisplayed()).toBe(true);
    });

    it('can change normal theme', function () {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item6', 'Politic');
        authoring.changeNormalTheme('dark-theme');

        expect(monitoring.hasClass(element(by.className('main-article')), 'dark-theme')).toBe(true);
    });

    it('can change proofread theme', function () {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item6', 'Politic');
        authoring.changeProofreadTheme('dark-theme-mono');

        expect(monitoring.hasClass(element(by.className('main-article')), 'dark-theme-mono')).toBe(true);
    });

    it('can show correct and kill buttons based on the selected action', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item5', 'Politic');
        authoring.writeText('some text');
        authoring.save();
        authoring.publish();

        workspace.selectStage('Published');
        workspace.filterItems('text');

        content.actionOnItem('Correct item', 0);
        authoring.sendToButton.click();
        expect(authoring.correct_button.isDisplayed()).toBe(true);
        element(by.id('closeAuthoringBtn')).click();

        content.actionOnItem('Kill item', 0);
        authoring.sendToButton.click();
        expect(authoring.kill_button.isDisplayed()).toBe(true);
        element(by.id('closeAuthoringBtn')).click();
    });

});
