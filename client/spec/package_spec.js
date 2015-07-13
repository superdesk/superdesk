var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content,
    authoring = require('./helpers/pages').authoring;

describe('Package', function() {
    'use strict';

    beforeEach(function(done) {
        openUrl('/#/workspace/content').then(done);
    });

    it('increment package version', function() {
        workspace.switchToDesk('PERSONAL');
        content.setListView();
        content.actionOnItem('Edit package', 0);
        authoring.showSearch();
        authoring.addToGroup(0, 'MAIN');
        authoring.save();
        authoring.showVersions();
        expect(element.all(by.css('[ng-click="openVersion(version)"]')).count()).toBe(2);
    });

    it('reorder item on package', function() {
        workspace.switchToDesk('Personal').then(
            content.setListView
        ).then(function() {
            content.actionOnItem('Edit package', 0);
        });
        authoring.showSearch();
        authoring.addToGroup(0, 'MAIN');
        authoring.addToGroup(1, 'STORY');
        authoring.addToGroup(2, 'STORY');
        authoring.addToGroup(3, 'SIDEBARS');
        authoring.moveToGroup('MAIN', 0, 'STORY', 1);
        expect(authoring.getGroupItems('MAIN').count()).toBe(0);
        expect(authoring.getGroupItems('STORY').count()).toBe(3);
        authoring.save();
    });

    it('add multiple items to package', function() {
        addItemsToPackage();
        expect(authoring.getGroupItems('MAIN').count()).toBe(3);
    });

    it('can preview package in a package', function() {
        // populate package
        addItemsToPackage();

        // package existing package
        workspace.openContent('/#/workspace/content');
        workspace.switchToDesk('Personal');
        content.setListView();
        content.actionOnItem('Package item', 0);

        // select package
        workspace.openContent('/#/workspace/content');
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
