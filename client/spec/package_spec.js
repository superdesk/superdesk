var route = require('./helpers/utils').route,
    search = require('./helpers/search'),
    authoring = require('./helpers/pages').authoring,
    monitoring = require('./helpers/monitoring');

describe('Package', function() {
    'use strict';

    beforeEach(route('/workspace/monitoring'));

    it('increment package version', function() {
        monitoring.actionOnItem('Edit', 2, 0);
        monitoring.actionOnItemSubmenu('Add to current', 'main', 1, 0);
        authoring.save();
        authoring.showVersions();
        expect(element.all(by.repeater('version in versions')).count()).toBe(2);
    });

    it('reorder item on package', function() {
        monitoring.actionOnItem('Edit', 2, 0);
        monitoring.actionOnItemSubmenu('Add to current', 'main', 1, 0);
        monitoring.actionOnItemSubmenu('Add to current', 'story', 2, 1);
        authoring.moveToGroup('MAIN', 0, 'STORY', 0);
        expect(authoring.getGroupItems('MAIN').count()).toBe(0);
        expect(authoring.getGroupItems('STORY').count()).toBe(2);
    });

    xit('add multiple items to package', function() {
        monitoring.actionOnItem('Edit', 2, 0);
        monitoring.selectItem(1, 0);
        monitoring.selectItem(2, 1);
        //TODO: operation not implemented yet, it will be implemented by SD-3308
        //monitoring.addToCurrentMultipleItems('MAIN');
        expect(authoring.getGroupItems('MAIN').count()).toBe(2);
    });

    xit('can preview package in a package', function() {
        monitoring.actionOnItem('Edit', 2, 0);
        monitoring.actionOnItemSubmenu('Add to current', 'main', 2, 1);
        authoring.save();
        authoring.close();
        monitoring.previewAction(2, 0);
        //There is no preview in preview, SD-3319
    });

    it('create package from multiple items', function() {
        monitoring.selectItem(1, 0);
        monitoring.selectItem(1, 1);
        monitoring.createPackageFromItems();
        expect(authoring.getGroupItems('MAIN').count()).toBe(2);
    });

    it('can add an item to an existing package only once', function() {
        monitoring.actionOnItem('Edit', 2, 0);
        monitoring.actionOnItemSubmenu('Add to current', 'main', 1, 0);
        monitoring.actionOnItemSubmenu('Add to current', 'story', 1, 0);
        authoring.save();
        expect(authoring.getGroupItems('MAIN').count()).toBe(1);
        expect(authoring.getGroupItems('STORY').count()).toBe(0);
    });

    it('create package from published item', function() {
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.writeText('some text');
        authoring.save();
        authoring.publish();
        monitoring.showSearch();
        search.setListView();
        search.showCustomSearch();
        search.toggleByType('text');
        expect(search.getTextItem(0)).toBe('item5');
        search.actionOnItem('Create package', 0);
        expect(authoring.getGroupItems('MAIN').count()).toBe(1);
    });

    it('create package by combining an item with open item', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        browser.sleep(500);
        monitoring.actionOnItem('Combine with current', 2, 0);
        expect(authoring.getGroupItems('MAIN').count()).toBe(2);
    });

});
