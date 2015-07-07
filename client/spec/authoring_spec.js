
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring');

describe('authoring', function() {
    it('can open item stage', function() {
        workspace.open();
        workspace.editItem(0, 'SPORTS DESK');
        element(by.css('button.stage')).click();
        expect(browser.getCurrentUrl()).toMatch(/workspace\/content$/);
    });
    it('Can Undo content', function() {
        workspace.open();
        workspace.editItem(1);
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
            expect(text).toEqual('headlineitem1');
        });

        browser.sleep(500);

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        browser.driver.switchTo().activeElement().getText().then(function(text) {
            expect(text).toEqual('item1');
        });
    });
    it('Can Redo content', function () {
        workspace.open();
        workspace.editItem(1);
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
            expect(text).toEqual('UndoRedo');
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
});
