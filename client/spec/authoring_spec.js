
'use strict';

var workspace = require('./helpers/workspace'),
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
});
