
'use strict';

var authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring'),
    workspace = require('./helpers/workspace');

describe('monitoring view', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
    });

    it('configure a stage and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item6');
    });

    it('configure personal and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 1)).toBe('item1');
        expect(monitoring.getTextItem(0, 2)).toBe('item2');
    });

    it('configure a saved search and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
    });

    it('configure a stage and a saved search and show them on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item6');
        expect(monitoring.getTextItem(1, 0)).toBe('item3');
    });

    it('configure a stage and a saved search then unselect stage and show search on monitoring view',
    function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
    });

    it('configure stage and search and then reorder', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.moveOrderItem(0, 1);
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item1');
        expect(monitoring.getTextItem(1, 0)).toBe('item6');

        monitoring.showMonitoringSettings();
        monitoring.nextStages();
        monitoring.nextSearches();
        expect(monitoring.getOrderItemText(0)).toBe('saved search item');
        expect(monitoring.getOrderItemText(1)).toBe('Politic Desk : two');
    });

    it('configure a stage, a saved search and personal and then set max items', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.moveOrderItem(0, 1);
        monitoring.nextReorder();
        monitoring.setMaxItems(0, 1);
        monitoring.setMaxItems(1, 1);
        monitoring.setMaxItems(2, 1);
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('package1');
        expect(monitoring.getTextItem(1, 0)).toBe('item6');
        expect(monitoring.getTextItem(2, 0)).toBe('item1');
    });

    it('configure monitoring view for 2 desks', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        workspace.selectDesk('Sports Desk');
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(1);
        monitoring.toggleStage(1, 1);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        workspace.selectDesk('Politic Desk');
        expect(monitoring.getTextItem(0, 0)).toBe('item6');

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
    });

    it('can search content', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item6');
        expect(monitoring.getTextItem(1, 0)).toBe('item1');
        expect(monitoring.getTextItem(1, 1)).toBe('item2');
        expect(monitoring.getTextItem(1, 2)).toBe('item5');

        monitoring.searchAction('item6');
        expect(monitoring.getTextItem(0, 0)).toBe('item6');
        expect(monitoring.getTextItem(1, 0)).toBe('item6');
    });

    it('can preview content', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.previewAction(0, 0);
        expect(monitoring.getPreviewTitle()).toBe('item6');
    });

    it('can open read only content', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.openAction(0, 0);
        expect(authoring.save_button.isDisplayed()).toBe(true);
    });

    it('updates item group on single item spike-unspike', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        expect(monitoring.getGroupItems(0).count()).toBe(1);
        monitoring.actionOnItem('Spike', 0, 0);
        expect(monitoring.getGroupItems(0).count()).toBe(0);
        monitoring.openSpiked();
        expect(monitoring.getItemText(monitoring.getSpikedItem(0))).toBe('item5');
        monitoring.unspikeItem(0);
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });

    it('updates item group on multiple item spike-unspike', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        expect(monitoring.getGroupItems(1).count()).toBe(1);
        monitoring.selectItem(0, 0);
        monitoring.spikeMultipleItems();
        browser.sleep(4000);
        expect(monitoring.getGroupItems(0).count()).toBe(0);
        monitoring.openSpiked();
        expect(monitoring.getItemText(monitoring.getSpikedItem(0))).toBe('item5');
        monitoring.selectSpikedItem(0);
        monitoring.unspikeMultipleItems();
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });

    it('can show/hide monitoring list', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 2);
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.openAction(0, 0);
        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(true);

        browser.sleep(1000);

        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(false);
    });
});
