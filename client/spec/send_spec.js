
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring');

describe('Send To', function() {
    it('can submit item to a desk', function() {
        workspace.open();
        workspace.editItem(1);
        authoring.sendTo('Sports Desk');
        workspace.switchToDesk('SPORTS DESK');
        expect(
            element.all(by.repeater('items._items'))
                .first()
                .element(by.css('.state-label'))
                .getText()
        ).toBe('SUBMITTED');
    });
    it('warns that there are spelling mistakes', function () {
        workspace.open();
        workspace.editItem(1);
        authoring.writeText('mispeled word');
        authoring.sendTo('Sports Desk');
        expect(element(by.className('modal-content')).isDisplayed()).toBe(true);
    });
    it('can submit item to a desk although there are spelling mistakes', function () {
        workspace.open();
        workspace.editItem(1);
        authoring.writeText('mispeled word');
        authoring.sendTo('Sports Desk');
        element(by.className('modal-content')).all(by.css('[ng-click="ok()"]')).click();
        workspace.switchToDesk('SPORTS DESK');
        expect(
                element.all(by.repeater('items._items'))
                .first()
                .element(by.css('.state-label'))
                .getText()
                ).toBe('SUBMITTED');
    });
    it('can cancel submit request because there are spelling mistakes', function () {
        workspace.open();
        workspace.editItem(1);
        authoring.writeText('mispeled word');
        authoring.sendTo('Sports Desk');
        element(by.className('modal-content')).all(by.css('[ng-click="cancel()"]')).click();
        expect(browser.getCurrentUrl()).toMatch(/authoring/);
    });
});
