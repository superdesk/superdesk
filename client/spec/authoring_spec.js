
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
        authoring.writeText('Words');

        var Key = protractor.Key;
        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        var focused = browser.driver.switchTo().activeElement().getText();
        expect(focused).toEqual('Two');
        // headline editor
        authoring.writeTextToHeadline('headline');

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        focused = browser.driver.switchTo().activeElement().getText();
        expect(focused).toEqual('item1');

    });
    it('Can Redo content', function () {
        workspace.open();
        workspace.editItem(1);
        authoring.writeText('Undo');
        authoring.writeText('Redo');

        var Key = protractor.Key;
        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        var focused = browser.driver.switchTo().activeElement().getText();
        expect(focused).toEqual('Undo');

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'y')).perform();

        focused = browser.driver.switchTo().activeElement().getText();
        expect(focused).toEqual('UndoRedo');
        // abstract editor
        authoring.writeTextToAbstract('Redo');
        browser.sleep(200);

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'z')).perform();

        focused = browser.driver.switchTo().activeElement().getText();
        expect(focused).toEqual('R');

        browser.actions().sendKeys(Key.chord(Key.CONTROL, 'y')).perform();

        focused = browser.driver.switchTo().activeElement().getText();
        expect(focused).toEqual('Redo');

    });
});
