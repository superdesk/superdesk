
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring'),
    content = require('./helpers/content'),
    multicontent = require('./helpers/multicontent');

// todo(petr): those features should go to list
xdescribe('multi content view', function() {

    beforeEach(function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        content.editItem(0);
        authoring.showMulticontent();
    });

    it('configure a stage and show it on multicontent view', function() {
        expect(multicontent.getTextItem(1, 0)).toBe('item5');
        expect(multicontent.getTextItem(2, 0)).toBe('item6');
        expect(multicontent.getTextItem(5, 0)).toBe('item3');
        expect(multicontent.getTextItem(7, 0)).toBe('item4');
    });

    it('configure a stage and show it on multicontent view', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.nextSearches();
        multicontent.saveSettings();
        expect(multicontent.getTextItem(0, 0)).toBe('item6');
    });

    it('configure a saved search and show it on multicontent view', function() {
        multicontent.showMulticontentSettings();
        multicontent.nextStages();
        multicontent.toggleSearch(1);
        multicontent.nextSearches();
        multicontent.saveSettings();
        expect(multicontent.getTextItem(0, 0)).toBe('item3');
    });

    it('configure a stage and a saved search and show them on multicontent view', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(1);
        multicontent.nextSearches();
        multicontent.saveSettings();
        expect(multicontent.getTextItem(0, 0)).toBe('item6');
        expect(multicontent.getTextItem(1, 0)).toBe('item3');
    });

    it('configure a stage and a saved search then unselect stage and show search on multicontent view', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(1);
        multicontent.nextSearches();
        multicontent.saveSettings();

        multicontent.showMulticontentSettings();
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.nextSearches();
        multicontent.saveSettings();
        expect(multicontent.getTextItem(0, 0)).toBe('item3');
    });

    it('configure stage and search and then reorder', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(0);
        multicontent.toggleSearch(1);
        multicontent.nextSearches();
        multicontent.moveOrderItem(0, 1);
        multicontent.saveSettings();
        expect(multicontent.getTextItem(0, 0)).toBe('item1');
        expect(multicontent.getTextItem(1, 0)).toBe('item6');

        multicontent.showMulticontentSettings();
        multicontent.nextStages();
        multicontent.nextSearches();
        expect(multicontent.getOrderItemText(0)).toBe('saved search item');
        expect(multicontent.getOrderItemText(1)).toBe('Politic Desk : two');
    });

    it('can search content', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(0);
        multicontent.nextSearches();
        multicontent.saveSettings();
        expect(multicontent.getTextItem(0, 0)).toBe('item6');
        expect(multicontent.getTextItem(1, 0)).toBe('item1');
        expect(multicontent.getTextItem(1, 1)).toBe('item2');
        expect(multicontent.getTextItem(1, 2)).toBe('item5');

        multicontent.searchAction('item5');
        expect(multicontent.getTextItem(1, 0)).toBe('item5');
    });

    it('can preview content', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(0);
        multicontent.nextSearches();
        multicontent.saveSettings();

        multicontent.previewAction(0, 0);
        expect(multicontent.getPreviewTitle()).toBe('item6');
    });

    it('can open read only content', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(0);
        multicontent.nextSearches();
        multicontent.saveSettings();

        multicontent.openAction(0, 0);
        expect(authoring.lock.isDisplayed()).toBe(true);
    });

    it('can edit content', function() {
        multicontent.showMulticontentSettings();
        multicontent.toggleDesk(0);
        multicontent.toggleStage(0, 2);
        multicontent.nextStages();
        multicontent.toggleSearch(0);
        multicontent.nextSearches();
        multicontent.saveSettings();

        multicontent.editAction(0, 0);
        expect(authoring.publish.isDisplayed()).toBe(true);
    });

});
