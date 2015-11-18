'use strict';

var workspace = require('./helpers/workspace'),
    content = require('./helpers/content'),
    authoring = require('./helpers/authoring'),
    legalArchive = require('./helpers/legal_archive');

describe('Legal Archive', function() {
    it('can display Legal Archive option in hamburger menu', function () {
        workspace.open();

        expect(legalArchive.getLegalArchiveMenuOption().isDisplayed()).toBe(true);
    });

    it('can display items in Legal Archive', function() {
        legalArchive.open();
        expect(content.getItems().count()).toBe(4);
    });

    it('can display only OPEN option in the Actions Menu for items in Legal Archive', function () {
        legalArchive.open();
        var menu = content.openItemMenu('item1 in legal archive');
        var menuItems = menu.all(by.repeater('activity in actions.default'));

        expect(menuItems.count()).toBe(1);
    });

    it('can preview text item in a Legal Archive', function () {
        legalArchive.open();

        content.actionOnItem('Open', 'item1 in legal archive');

        expect(content.getItemType('text').isDisplayed()).toBe(true);
        expect(content.getWidgets().count()).toBe(2);
        assertAuthoringTopbarAndItemState();
    });

    it('can preview package in a Legal Archive', function () {
        legalArchive.open();

        content.actionOnItem('Open', 'package1 in legal archive');

        expect(content.getItemType('composite').isDisplayed()).toBe(true);
        expect(content.getWidgets().count()).toBe(2);
        assertAuthoringTopbarAndItemState();
    });

    it('can open items in the package', function() {
        legalArchive.open();

        content.actionOnItem('Open', 'package1 in legal archive');

        element.all(by.repeater('child in item.childData')).then(function (itemsInPackage) {
            itemsInPackage[0].element(by.className('open-item')).click();
            assertAuthoringTopbarAndItemState();
        });
    });

    it('can show version and item history for an item', function() {
        legalArchive.open();
        content.actionOnItem('Open', 'item2 in legal archive');

        authoring.showVersions();
        expect(authoring.getHistoryItems().count()).toBe(3);
        authoring.showVersions();

        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
    });

    function assertAuthoringTopbarAndItemState() {
        expect(authoring.close_button.isDisplayed()).toBe(true);
        expect(authoring.save_button.isPresent()).toBe(false);
        expect(authoring.edit_button.isPresent()).toBe(false);
        expect(authoring.edit_correct_button.isPresent()).toBe(false);
        expect(authoring.edit_kill_button.isPresent()).toBe(false);
        expect(authoring.navbarMenuBtn.isPresent()).toBe(false);
        expect(authoring.sendToButton.isDisplayed()).toBe(false);
        expect(authoring.multieditOption.isPresent()).toBe(false);

        authoring.showInfo();

        element(by.className('state-label')).getText().then(function(state) {
            var isPublished = (['published', 'corrected', 'killed'].indexOf(state.toLowerCase()) !== -1);
            expect(isPublished).toBe(true);
        });
    }
});
