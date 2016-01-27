'use strict';

var openUrl = require('./helpers/utils').open,
    globalSearch = require('./helpers/search'),
    authoring = require('./helpers/authoring'),
    content = require('./helpers/content'),
    monitoring = require('./helpers/monitoring');

describe('archived', function() {

    beforeEach(function() {
        openUrl('/#/search').then(globalSearch.setListView());
    });

    it('display items from archived.', function() {
        expect(globalSearch.getItems().count()).toBe(14);
        globalSearch.getArchivedContent();
        expect(globalSearch.getItems().count()).toBe(3);
    });

    it('open an item preview', function() {
        expect(globalSearch.getItems().count()).toBe(14);
        globalSearch.getArchivedContent();
        expect(globalSearch.getItems().count()).toBe(3);
        var itemText = globalSearch.getTextItem(0);
        globalSearch.itemClick(0);
        expect(monitoring.getPreviewTitle()).toBe(itemText);
    });

    it('open an item in authoring', function() {
        expect(globalSearch.getItems().count()).toBe(14);
        globalSearch.getArchivedContent();
        expect(globalSearch.getItems().count()).toBe(3);
        globalSearch.actionOnItem('Open', 0);
        expect(content.getWidgets().count()).toBe(1);
        expect(authoring.close_button.isDisplayed()).toBe(true);
        expect(authoring.save_button.isPresent()).toBe(false);
        expect(authoring.edit_button.isDisplayed()).toBe(false);
        expect(authoring.edit_correct_button.isDisplayed()).toBe(false);
        expect(authoring.edit_kill_button.isDisplayed()).toBe(false);
        expect(authoring.navbarMenuBtn.isPresent()).toBe(false);
        expect(authoring.sendToButton.isDisplayed()).toBe(false);
        expect(authoring.multieditOption.isPresent()).toBe(false);
        authoring.showInfo();
        expect(authoring.isPublishedState()).toBe(true);
    });

});
