'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring');

describe('send', function() {
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

    // NOTE: Commented because spellchecker is now disabled until we fix it
    // it('warns that there are spelling mistakes', function () {
    //     workspace.open();
    //     workspace.editItem(1);
    //     authoring.writeText('mispeled word');
    //     authoring.sendTo('Sports Desk');
    //     expect(element(by.className('modal-content')).isDisplayed()).toBe(true);
    // });
    //
    // it('can submit item to a desk although there are spelling mistakes', function () {
    //     workspace.open();
    //     workspace.editItem(1);
    //     authoring.writeText('mispeled word');
    //     authoring.sendTo('Sports Desk');
    //     element(by.className('modal-content')).all(by.css('[ng-click="ok()"]')).click();
    //     workspace.switchToDesk('SPORTS DESK');
    //     expect(
    //             element.all(by.repeater('items._items'))
    //             .first()
    //             .element(by.css('.state-label'))
    //             .getText()
    //             ).toBe('SUBMITTED');
    // });
    //
    // it('can cancel submit request because there are spelling mistakes', function () {
    //     workspace.open();
    //     workspace.editItem(1);
    //     authoring.writeText('mispeled word');
    //     authoring.sendTo('Sports Desk');
    //     element(by.className('modal-content')).all(by.css('[ng-click="cancel()"]')).click();
    //     expect(element(by.className('authoring-embedded')).isDisplayed()).toBe(true);
    // });

    it('can open send to panel when monitoring list is hidden', function() {
        monitoring.openMonitoring();
        monitoring.openAction(2, 0);
        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(true);

        authoring.sendToButton.click();
        expect(authoring.sendItemContainer.isDisplayed()).toBe(true);
    });

    it('can display monitoring after submitting an item to a desk using full view of authoring', function() {
        monitoring.openMonitoring();
        workspace.selectDesk('Sports Desk');
        monitoring.openAction(2, 0);
        monitoring.showHideList();

        authoring.sendTo('Politic Desk');
        expect(monitoring.getGroups().count()).toBe(6);
    });

});
