
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring');

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
        expect(element(by.className('authoring-embedded')).isDisplayed()).toBe(true);
    });

    it('can open send to panel when monitoring list is hidden', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(true);
        browser.sleep(3000);

        authoring.sendToButton.click();
        expect(authoring.sendItemContainer.isDisplayed()).toBe(true);
    });
});
