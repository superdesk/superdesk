
'use strict';

var authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring'),
    workspace = require('./helpers/workspace'),
    desks = require('./helpers/desks');

describe('monitoring view', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
    });

    it('configure a stage and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 3);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item6');
    });

    it('configure personal and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
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
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item1');

    });

    it('configure a stage and a saved search and show them on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 3);
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item6');
        expect(monitoring.getTextItem(1, 0)).toBe('item1');
    });

    it('configure a stage and a saved search then unselect stage and show search on monitoring view',
    function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 3);
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
        expect(monitoring.getTextItem(0, 0)).toBe('item1');
    });

    it('configure stage and search and then reorder', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 3);
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.toggleSearch(2);
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
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 3);
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.toggleSearch(1);
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

    it('configure a saved search that contain ingest items', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
    });

    it('configure a saved search that contain both ingest items and content items', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
        expect(monitoring.getTextItem(0, 1)).toBe('item5');
    });

    it('configure a saved search from other user', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleAllSearches();
        expect(monitoring.getSearchText(0)).toBe('saved search admin1');
        monitoring.toggleSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
        expect(monitoring.getTextItem(0, 1)).toBe('item5');

        monitoring.showMonitoringSettings();
        monitoring.nextStages();
        expect(monitoring.getSearchText(0)).toBe('saved search admin1');
        monitoring.toggleAllSearches();
        expect(monitoring.getSearchText(0)).toBe('saved search admin1');
    });

    it('configure monitoring view for 2 desks', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 3);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        workspace.selectDesk('Sports Desk');
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(1, 0);
        monitoring.toggleStage(1, 2);
        monitoring.toggleStage(1, 3);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        workspace.selectDesk('Politic Desk');
        expect(monitoring.getTextItem(0, 0)).toBe('item6');

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
    });

    it('configure a stage and then delete the stage', function() {
        expect(monitoring.getGroups().count()).toBe(4);

        desks.openDesksSettings();
        desks.edit('Politic Desk');
        desks.showTab('stages');
        desks.removeStage('three');
        desks.showTab('macros');
        desks.save();

        monitoring.openMonitoring();
        expect(monitoring.getGroups().count()).toBe(3);
    });

    it('can search content', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleDesk(1);
        monitoring.toggleStage(1, 1);
        monitoring.toggleStage(1, 3);
        monitoring.nextStages();
        monitoring.toggleSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
        expect(monitoring.getTextItem(1, 0)).toBe('item4');
        expect(monitoring.getTextItem(2, 0)).toBe('item1');
        expect(monitoring.getTextItem(2, 4)).toBe('item3');

        monitoring.searchAction('item3');
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
        expect(monitoring.getTextItem(2, 0)).toBe('item3');

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getTextItem(1, 0)).toBe('item3');
    });

    it('can filter content by file type', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('package1');
        expect(monitoring.getTextItem(0, 1)).toBe('item1');
        expect(monitoring.getTextItem(0, 2)).toBe('item2');

        monitoring.filterAction('composite');
        expect(monitoring.getTextItem(0, 0)).toBe('package1');

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getGroupItems(0).count()).toBe(0);
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        expect(monitoring.getGroupItems(2).count()).toBe(0);
        expect(monitoring.getGroupItems(3).count()).toBe(0);
    });

    it('can preview content', function() {
        monitoring.previewAction(2, 0);
        expect(monitoring.getPreviewTitle()).toBe('item6');
    });

    it('can open read only content', function() {
        monitoring.openAction(2, 0);
        expect(authoring.save_button.isDisplayed()).toBe(true);
    });

    it('can start content upload', function() {
        monitoring.openCreateMenu();
        monitoring.startUpload();
        expect(monitoring.uploadModal.isDisplayed()).toBe(true);
    });

    it('show personal', function() {
        monitoring.openPersonal();
        expect(monitoring.getPersonalItemText(0)).toBe('package1');
        expect(monitoring.getPersonalItemText(1)).toBe('item1');
        expect(monitoring.getPersonalItemText(2)).toBe('item2');
    });

    it('updates item group on single item spike-unspike', function() {
        expect(monitoring.getGroupItems(1).count()).toBe(1);
        monitoring.actionOnItem('Spike', 1, 0);
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        monitoring.openSpiked();
        expect(monitoring.getItemText(monitoring.getSpikedItem(0))).toBe('item5');
        monitoring.unspikeItem(0);
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });

    it('updates personal on single item spike-unspike', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getGroupItems(0).count()).toBe(3);
        monitoring.actionOnItem('Spike', 0, 0);
        expect(monitoring.getGroupItems(0).count()).toBe(2);
        monitoring.openSpiked();
        expect(monitoring.getItemText(monitoring.getSpikedItem(0))).toBe('package1');
        monitoring.unspikeItem(0);
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });

    it('updates item group on multiple item spike-unspike', function() {
        expect(monitoring.getGroupItems(1).count()).toBe(1);
        monitoring.selectItem(1, 0);
        monitoring.spikeMultipleItems();
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        monitoring.openSpiked();
        expect(monitoring.getItemText(monitoring.getSpikedItem(0))).toBe('item5');
        monitoring.selectSpikedItem(0);
        monitoring.unspikeMultipleItems();
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });

    it('can show/hide monitoring list', function() {
        monitoring.openAction(1, 0);
        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(true);

        browser.sleep(1000);

        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(false);
    });

    it('can fetch ingest item', function () {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.openAction(0, 0);

        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 0);
        monitoring.nextStages();
        monitoring.toggleSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
        expect(authoring.save_button.isDisplayed()).toBe(true);
    });
});
