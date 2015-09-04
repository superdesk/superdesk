var route = require('./helpers/utils').route,
    workspace = require('./helpers/workspace'),
    content = require('./helpers/pages').content,
    authoring = require('./helpers/pages').authoring,
    monitoring = require('./helpers/monitoring');

describe('Package', function() {
    'use strict';

    beforeEach(route('/workspace/content'));

    it('increment package version', function() {
        workspace.switchToDesk('PERSONAL');
        content.setListView();
        content.actionOnItem('Edit package', 0);
        authoring.showSearch();
        authoring.addToGroup(0, 'MAIN');
        authoring.save();
        authoring.showVersions();
        expect(element.all(by.repeater('version in versions')).count()).toBe(2);
    });

    it('reorder item on package', function() {
        workspace.switchToDesk('Personal');
        content.setListView();
        content.actionOnItem('Edit package', 0);
        authoring.showSearch();
        authoring.addToGroup(0, 'MAIN');
        authoring.addToGroup(1, 'STORY');
        authoring.addToGroup(2, 'STORY');
        authoring.addToGroup(3, 'SIDEBARS');
        authoring.showSearch();
        authoring.moveToGroup('MAIN', 0, 'STORY', 1);
        expect(authoring.getGroupItems('MAIN').count()).toBe(0);
        expect(authoring.getGroupItems('STORY').count()).toBe(3);
    });

    it('add multiple items to package', function() {
        addItemsToPackage();
        expect(authoring.getGroupItems('MAIN').count()).toBe(3);
    });

    it('can preview package in a package', function() {
        // populate package
        addItemsToPackage();

        // package existing package
        workspace.openContent();
        workspace.switchToDesk('Personal');
        content.setListView();
        content.actionOnItem('Package item', 0);

        // select package
        workspace.openContent();
        workspace.switchToDesk('Personal');
        element.all(by.repeater('item in items')).first().click();

        // preview package via preview
        browser.sleep(100);
        element.all(by.repeater('child in item')).first().click();
        browser.sleep(100);
        expect(element(by.css('h5.lightbox-title')).getText()).toBe('package1');

        expect(element(by.css('.condensed-preview')).all(by.repeater('child in item')).count()).toBe(3);
    });

    it('create package from multiple items', function() {
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        content.selectItem(0);
        content.selectItem(1);
        content.createPackageFromItems();
        expect(authoring.getGroupItems('MAIN').count()).toBe(2);
    });

    it('can add items to an existing package', function() {
        monitoring.openMonitoring();
        monitoring.showMonitoringSettings();
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        monitoring.openAction(4, 0);
        browser.sleep(500);
        expect(authoring.getGroupItems('MAIN').count()).toBe(0);
        monitoring.actionOnItem('Add to package', 1, 0);
        expect(authoring.getGroupItems('MAIN').count()).toBe(1);
    });

    it('can add items to a package only once', function() {
        monitoring.openMonitoring();
        monitoring.showMonitoringSettings();
        monitoring.togglePersonal();
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        monitoring.openAction(4, 0);
        browser.sleep(1000);
        monitoring.actionOnItem('Add to package', 1, 0);
        browser.sleep(1000);
        authoring.save();
        browser.refresh();
        monitoring.openAction(4, 0);
        browser.sleep(500);
        var menu = monitoring.openItemMenu(1, 0);
        expect(menu.element(by.partialLinkText('Add to package')).isPresent()).toBe(false);
    });

    it('create package from published item', function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        workspace.editItem('item5', 'Politic');
        authoring.writeText('some text');
        authoring.save();
        authoring.publish();
        browser.sleep(500);
        workspace.selectStage('Published');
        browser.sleep(500);
        workspace.filterItems('text');
        content.actionOnItem('Package item', 0);
        expect(authoring.getGroupItems('MAIN').count()).toBe(1);
    });

    function addItemsToPackage() {
        workspace.switchToDesk('Personal').then(
            content.setListView
        ).then(function() {
            content.actionOnItem('Edit package', 0);
        });
        authoring.showSearch();
        authoring.selectSearchItem(0);
        authoring.selectSearchItem(1);
        authoring.selectSearchItem(2);
        authoring.addMultiToGroup('MAIN');
        authoring.save();
    }
});
