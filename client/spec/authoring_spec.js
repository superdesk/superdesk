
'use strict';

var workspace = require('./helpers/workspace'),
    monitoring = require('./helpers/monitoring'),
    authoring = require('./helpers/authoring');

describe('authoring', function() {
    it('can open item stage', function() {
        workspace.open();
        workspace.editItem('item4', 'SPORTS');
        element(by.css('button.stage')).click();
        expect(browser.getCurrentUrl()).toMatch(/workspace\/content$/);
    });

    it('Can Undo content', function() {
        workspace.open();
        workspace.editItem('item4', 'SPORTS');
        authoring.writeText('Two');
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Two');
        });

        browser.sleep(500);

        authoring.writeText('Words');
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('TwoWords');
        });

        browser.sleep(500);

        var Key = protractor.Key;
        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Two');
        });
        // headline editor
        authoring.writeTextToHeadline('headline');
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('headlineitem4');
        });

        browser.sleep(500);

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('item4');
        });
    });

    it('Can Redo content', function () {
        workspace.open();
        workspace.editItem('item4', 'SPORTS');
        authoring.writeText('Undo');
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Undo');
        });

        browser.sleep(500);

        authoring.writeText('Redo');
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('UndoRedo');
        });

        browser.sleep(500);

        var Key = protractor.Key;

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Undo');
        });

        browser.sleep(500);

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'y')).perform();
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Undo');
        });

        // abstract editor
        authoring.writeTextToAbstract('Redo');
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Redo');
        });

        browser.sleep(500);

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('');
        });

        browser.sleep(500);

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'y')).perform();
        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('Redo');
        });

    });

    it('view item history create-fetch operation', function() {
        workspace.open();
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

        workspace.editItem('item5', 'Politic');
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(1);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Story \d+ \(Politic Desk\/one\) Created by.*/);
    });

    it('view item history spike-unspike operations', function() {
        workspace.open();
        workspace.actionOnItem('Spike', 'item5', 'Politic');
        workspace.actionOnItem('Unspike Item', 0, 'Politic', 'Spiked');
        workspace.editItem('item5', 'Politic');

        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Spiked from Politic Desk\/one by .*/);
        expect(authoring.getHistoryItem(2).getText()).toMatch(/Unspiked to Politic Desk\/one by .*/);
    });

    it('view item history move operation', function() {
        workspace.open();
        workspace.editItem('item5', 'Politic');
        authoring.sendTo('Politic Desk', 'two');
        workspace.selectStage('two');
        workspace.editItem('item5', 'Politic');
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Moved to Politic Desk\/two by .*/);
    });

    it('view item history duplicate operation', function() {
        workspace.open();
        workspace.duplicateItem('item5', 'Politic Desk', 'two');
        workspace.selectStage('two');
        workspace.editItem('item5', 'Politic');
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Copied to \d+ \(Politic Desk\/New\) by .*/);
        expect(authoring.getHistoryItem(2).getText()).toMatch(/Moved to Politic Desk\/two by .*/);
    });

    it('view item history publish operation', function() {
        workspace.open();
        workspace.editItem('item5', 'Politic');
        authoring.writeText('some text');
        authoring.save();
        authoring.publish();
        browser.sleep(500);
        workspace.selectStage('Published');
        workspace.filterItems('composite');
        workspace.actionOnItem('View item', 'item5', 'Politic', 'Published');
        authoring.showHistory();
        browser.sleep(500);
        expect(authoring.getHistoryItems().count()).toBe(1);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Published by.*/);
    });

    it('allows to create a new empty package', function () {
        monitoring.openMonitoring();
        browser.sleep(500);
        monitoring.createItemAction('create_package');
        expect(authoring.findItemTypeIcons('composite').count()).toBeGreaterThan(0);
    });

});
