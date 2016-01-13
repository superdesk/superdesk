'use strict';

var authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring'),
    workspace = require('./helpers/workspace'),
    dashboard = require('./helpers/dashboard'),
    desks = require('./helpers/desks');

describe('monitoring', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
    });

    it('configure a stage and show it on monitoring view', function() {
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 2)).toBe('item6');
    });

    it('can configure desk output as default when user switches desks and show it on monitoring view', function() {
        expect(monitoring.getGroups().count()).toBe(6);

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getGroups().count()).toBe(6);
    });

    it('can display the item in Desk Output when it\'s been submitted to a production desk', function () {
        workspace.selectDesk('Sports Desk');
        monitoring.actionOnItem('Edit', 2, 0);
        authoring.sendTo('Politic Desk', 'two');
        //Spell check confirmation modal save action
        authoring.confirmSendTo();
        expect(monitoring.getTextItem(5, 0)).toBe('item3');
    });

    it('can display the item in Desk Output when it\'s published in a production desk', function() {
        expect(monitoring.getTextItem(3, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 3, 2);
        authoring.publish();
        expect(monitoring.getTextItem(5, 0)).toBe('item6');
    });

    it('configure personal and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item1');
        expect(monitoring.getTextItem(0, 1)).toBe('item2');
    });

    it('configure a saved search and show it on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
    });

    it('configure a stage and a saved search and show them on monitoring view', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 0);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.toggleDeskOutput(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 2)).toBe('item6');
        expect(monitoring.getTextItem(1, 0)).toBe('ingest1');
    });

    it('configure a stage and a saved search then unselect stage and show search on monitoring view',
    function() {
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.toggleDeskOutput(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.showMonitoringSettings();
        monitoring.toggleStage(0, 3);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
    });

    it('configure stage and search and then reorder', function() {
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.toggleDeskOutput(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(0);
        monitoring.toggleGlobalSearch(1);
        monitoring.nextSearches();
        monitoring.moveOrderItem(0, 1);
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
        expect(monitoring.getTextItem(1, 2)).toBe('item6');

        monitoring.showMonitoringSettings();
        monitoring.nextStages();
        monitoring.nextSearches();
        expect(monitoring.getOrderItemText(0)).toBe('global saved search ingest1');
        expect(monitoring.getOrderItemText(1)).toBe('Politic Desk : two');
    });

    it('configure a stage, a saved search and personal and then set max items', function() {
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.toggleDeskOutput(0);
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(0);
        monitoring.nextSearches();
        monitoring.moveOrderItem(0, 1);
        monitoring.nextReorder();
        monitoring.setMaxItems(0, 1);
        monitoring.setMaxItems(1, 1);
        monitoring.setMaxItems(2, 1);
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item1');
        expect(monitoring.getTextItem(1, 2)).toBe('item6');
        expect(monitoring.getTextItem(2, 0)).toBe('ingest1');
    });

    it('configure a saved search that contain ingest items', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(0);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
    });

    it('configure a saved search that contain both ingest items and content items', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item5');
        expect(monitoring.getTextItem(0, 1)).toBe('item9');
        expect(monitoring.getTextItem(0, 3)).toBe('ingest1');
    });

    it('configure a saved search from other user', function() {
        workspace.createWorkspace('My Workspace');
        browser.sleep(500);
        monitoring.showMonitoringSettings();
        monitoring.nextStages();
        monitoring.switchGlobalSearchOn();
        monitoring.toggleGlobalSearch(3);
        expect(monitoring.getGlobalSearchText(3)).toBe('global saved search other user by first name1 last name1');
        monitoring.togglePrivateSearch(1);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item5');
        expect(monitoring.getTextItem(0, 1)).toBe('item9');
        monitoring.showMonitoringSettings();
        monitoring.nextStages();
        expect(monitoring.getGlobalSearchText(0)).toBe('global saved search ingest1 by first name last name');
        expect(monitoring.getPrivateSearchText(0)).toBe('saved search ingest1');
    });

    it('configure monitoring view for more than 1 desk', function() {
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        workspace.selectDesk('Sports Desk');
        monitoring.turnOffWorkingStage(1, false);
        monitoring.toggleStage(1, 1);
        monitoring.toggleStage(1, 3);
        monitoring.toggleStage(1, 4);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        workspace.selectDesk('Politic Desk');
        expect(monitoring.getTextItem(0, 2)).toBe('item6');

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
    });

    it('configure a stage and then delete the stage', function() {
        expect(monitoring.getGroups().count()).toBe(6);

        desks.openDesksSettings();
        desks.edit('Politic Desk');
        desks.showTab('stages');
        desks.removeStage('three');
        desks.showTab('macros');
        desks.save();

        monitoring.openMonitoring();
        expect(monitoring.getGroups().count()).toBe(5);
    });

    it('can search content', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleDesk(1);
        monitoring.toggleStage(1, 2);
        monitoring.toggleStage(1, 4);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(2);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
        expect(monitoring.getTextItem(1, 0)).toBe('item4');
        expect(monitoring.getTextItem(2, 0)).toBe('item1');
        expect(monitoring.getTextItem(2, 4)).toBe('item7');

        monitoring.searchAction('item3');
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
        expect(monitoring.getTextItem(2, 0)).toBe('item3');

        workspace.selectDesk('Sports Desk');
        monitoring.turnOffWorkingStage(1);
        expect(monitoring.getTextItem(1, 0)).toBe('item3');

        workspace.selectDesk('Politic Desk');
        dashboard.openDashboard();
        monitoring.openMonitoring();
        expect(monitoring.getTextItem(0, 0)).toBe('item3');
        expect(monitoring.getTextItem(1, 0)).toBe('item4');
        expect(monitoring.getTextItem(2, 0)).toBe('item1');
        expect(monitoring.getTextItem(2, 4)).toBe('item7');
    });

    it('can filter content by file type', function() {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(monitoring.getTextItem(2, 0)).toBe('item5');
        expect(monitoring.getTextItem(2, 1)).toBe('item9');

        monitoring.filterAction('composite');
        expect(monitoring.getTextItem(3, 2)).toBe('package1');

        workspace.selectDesk('Sports Desk');
        expect(monitoring.getGroupItems(0).count()).toBe(0);
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        expect(monitoring.getGroupItems(2).count()).toBe(0);
        expect(monitoring.getGroupItems(3).count()).toBe(0);
    });

    it('can order content', function() {
        monitoring.turnOffWorkingStage(0);
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        expect(monitoring.getTextItem(1, 1)).toBe('item9');
        expect(monitoring.getTextItem(1, 2)).toBe('item7');
        expect(monitoring.getTextItem(1, 3)).toBe('item8');
        monitoring.setOrder('Slugline', true);
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        expect(monitoring.getTextItem(1, 1)).toBe('item7');
        expect(monitoring.getTextItem(1, 2)).toBe('item8');
        expect(monitoring.getTextItem(1, 3)).toBe('item9');
    });

    it('can preview content', function() {
        monitoring.turnOffWorkingStage(0);
        monitoring.previewAction(2, 2);
        expect(monitoring.getPreviewTitle()).toBe('item6');
        monitoring.closePreview();
    });

    it('can open read only content', function() {
        monitoring.turnOffWorkingStage(0);
        monitoring.openAction(2, 0);
        expect(authoring.save_button.isDisplayed()).toBe(true);
    });

    it('can start content upload', function() {
        monitoring.openCreateMenu();
        monitoring.startUpload();
        expect(monitoring.uploadModal.isDisplayed()).toBe(true);
    });

    it('show personal', function() {
        monitoring.showPersonal();
        expect(monitoring.getPersonalItemText(0)).toBe('item1');
        expect(monitoring.getPersonalItemText(1)).toBe('item2');
    });

    it('can view items in related item tab', function() {
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        expect(monitoring.getGroupItems(2).count()).toBe(4);
        monitoring.actionOnItem('Duplicate', 2, 0);
        monitoring.filterAction('text');
        expect(monitoring.getGroupItems(0).count()).toBe(1);
        expect(monitoring.getTextItem(0, 0)).toBe('item5');
        monitoring.previewAction(0, 0);
        monitoring.tabAction('related');
        monitoring.openRelatedItem(0);
        expect(authoring.getHeadlineText()).toBe('item5');
    });

    it('updates item group on single item spike-unspike', function() {
        monitoring.turnOffWorkingStage(0);
        expect(monitoring.getGroupItems(1).count()).toBe(4);

        monitoring.actionOnItem('Spike', 1, 2);
        expect(monitoring.getGroupItems(1).count()).toBe(3);

        monitoring.showSpiked();
        expect(monitoring.getSpikedTextItem(0)).toBe('item7');

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
        expect(monitoring.getGroupItems(0).count()).toBe(2);
        monitoring.actionOnItem('Spike', 0, 0);
        expect(monitoring.getGroupItems(0).count()).toBe(1);
        monitoring.showSpiked();
        expect(monitoring.getSpikedTextItem(0)).toBe('item1');
        monitoring.unspikeItem(0);
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });

    it('updates item group on multiple item spike-unspike', function() {
        monitoring.turnOffWorkingStage(0);
        expect(monitoring.getGroupItems(1).count()).toBe(4);
        monitoring.selectItem(1, 2);
        monitoring.spikeMultipleItems();
        expect(monitoring.getGroupItems(1).count()).toBe(3);
        monitoring.showSpiked();
        expect(monitoring.getSpikedTextItem(0)).toBe('item7');
        monitoring.selectSpikedItem(0);
        monitoring.unspikeMultipleItems();
        expect(monitoring.getSpikedItems().count()).toBe(0);
    });
    it('can show/hide monitoring list', function() {
        monitoring.openAction(2, 0);
        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(true);

        browser.sleep(1000);

        monitoring.showHideList();
        expect(monitoring.hasClass(element(by.id('main-container')), 'hideMonitoring')).toBe(false);
    });

    it('can fetch item', function () {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.openAction(0, 3);
        browser.sleep(500);

        expect(monitoring.getTextItem(0, 4)).toBe('ingest1');
        expect(authoring.save_button.isDisplayed()).toBe(true);
    });

    it('can fetch as item', function () {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.openFetchAsOptions(0, 3);

        expect(element(by.id('publishScheduleTimestamp')).isPresent()).toBe(false);
        expect(element(by.id('embargoScheduleTimestamp')).isPresent()).toBe(false);

        monitoring.clickOnFetchButton();

        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.toggleStage(0, 1);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        expect(monitoring.getTextItem(0, 0)).toBe('ingest1');
    });

    it('can fetch as and open item', function () {
        monitoring.showMonitoringSettings();
        monitoring.toggleDesk(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(3);
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        monitoring.fetchAndOpen(0, 3);

        expect(authoring.save_button.isDisplayed()).toBe(true);
    });

    it('can display desk content in desk single view with their respective titles', function() {
        expect(monitoring.getGroups().count()).toBe(6);
        //exclude deskOutput
        monitoring.showMonitoringSettings();
        monitoring.toggleDeskOutput(0);
        monitoring.saveSettings();
        expect(monitoring.getGroups().count()).toBe(5);

        //ensure each stage items counts
        expect(monitoring.getGroupItems(0).count()).toBe(0);
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        expect(monitoring.getGroupItems(2).count()).toBe(4);
        expect(monitoring.getGroupItems(3).count()).toBe(4);
        expect(monitoring.getGroupItems(4).count()).toBe(0);

        //view all items in desk single view
        monitoring.actionOnDeskSingleView();
        expect(monitoring.getSingleViewItemCount()).toBe(8);
        expect(monitoring.getDeskSingleViewTitle()).toBe('Politic Desk desk 8');

        //Monitoring Home
        monitoring.actionMonitoringHome();
        expect(monitoring.getMonitoringHomeTitle()).toBe('Monitoring');

        //Stage single view
        monitoring.actionOnStageSingleView();
        expect(monitoring.getSingleViewItemCount()).toBe(0);
        expect(monitoring.getStageSingleViewTitle()).toBe('Politic Desk / Working Stage stage 0');
    });

    it('can remember multi selection even after scrolling and can reset multi-selection', function() {
        //Initial steps to setup global saved search group as a test group for this case
        monitoring.turnOffWorkingStage(0, false);
        monitoring.toggleStage(0, 1);
        monitoring.toggleStage(0, 2);
        monitoring.toggleStage(0, 4);
        monitoring.toggleDeskOutput(0);
        monitoring.nextStages();
        monitoring.toggleGlobalSearch(2);
        monitoring.nextSearches();
        // bring global search group in first place in monitoring view
        monitoring.moveOrderItem(0, 1);
        monitoring.nextReorder();

        //limit the size of group for the sake of scroll bar
        monitoring.setMaxItems(0, 3);
        monitoring.saveSettings();
        expect(monitoring.getGroupItems(0).count()).toBe(9);

        //select first item
        monitoring.selectItem(0, 0);
        expect(monitoring.getItem(0, 0).element(by.model('item.selected')).getAttribute('checked')).toBeTruthy();

        //scroll down and select last item
        browser.executeScript('window.scrollTo(0,250);').then(function () {
            monitoring.selectItem(0, 8);
            expect(monitoring.getItem(0, 8).element(by.model('item.selected')).getAttribute('checked')).toBeTruthy();
        });

        //scroll up to top again to see if selection to first item is remembered?
        browser.executeScript('window.scrollTo(0,0);').then(function () {
            expect(monitoring.getItem(0, 0).element(by.model('item.selected')).getAttribute('checked')).toBeTruthy();
        });

        //scroll down again to see if selection to last item is remembered?
        browser.executeScript('window.scrollTo(0,250);').then(function () {
            expect(monitoring.getItem(0, 8).element(by.model('item.selected')).getAttribute('checked')).toBeTruthy();
        });

        expect(monitoring.getMultiSelectCount()).toBe('2 Items selected');
        //Now reset multi-selection
        monitoring.clickOnCancelButton();
        expect(monitoring.getItem(0, 0).element(by.model('item.selected')).getAttribute('checked')).toBeFalsy();
        expect(monitoring.getItem(0, 8).element(by.model('item.selected')).getAttribute('checked')).toBeFalsy();
    });

    it('can view published duplicated item in duplicate tab of non-published original item', function() {
        expect(monitoring.getGroupItems(1).count()).toBe(0);
        expect(monitoring.getGroupItems(2).count()).toBe(4);
        expect(monitoring.getTextItem(2, 0)).toBe('item5'); // original item
        monitoring.actionOnItem('Duplicate', 2, 0);
        monitoring.filterAction('text');
        expect(monitoring.getGroupItems(0).count()).toBe(1);
        expect(monitoring.getTextItem(0, 0)).toBe('item5'); // duplicated item
        //publish this duplicated item
        monitoring.actionOnItem('Edit', 0, 0);
        authoring.publish();
        //now preview original item's duplicate tab for duplicated published item
        monitoring.previewAction(2, 0);
        monitoring.tabAction('related');
        expect(authoring.getDuplicatedItemState(0)).toBe('PUBLISHED');
    });

    it('can view published item as readonly when opened in multiEdit ', function() {
        monitoring.turnOffWorkingStage(0);
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.publish();

        //open published text item
        monitoring.filterAction('text');
        monitoring.actionOnItem('Correct item', 4, 0);

        //press multiEdit button to open publish item in multiEdit
        authoring.multieditOption.click();
        element(by.buttonText('Ok')).click();
        expect(element(by.className('state-label')).getText()).toEqual('PUBLISHED');

        var btnSave = element(by.css('[ng-click="save(item, articleEdit)"]'));
        expect(btnSave.isDisplayed()).toBeFalsy();  // Save button hidden for publish item

        var textField = element(by.className('text-editor'));
        // expect contenteditable=true attribute is missing/null for text-editor field,
        // hence editing is disabled for published item
        expect(textField.getAttribute('contenteditable')).toBe(null);
    });
});
