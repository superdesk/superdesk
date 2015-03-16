var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content,
    authoring = require('./helpers/pages').authoring;

describe('Content', function() {
    'use strict';

    beforeEach(function() {
        openUrl('/#/workspace/content')();
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

    it('edit title and description', function() {
        workspace.switchToDesk('Personal');
        content.setListView();
        content.actionOnItem('Edit package', 0);
        // Edit title and description
        element(by.id('keyword')).clear();
        element(by.id('keyword')).sendKeys('new keyword');
        element(by.id('title')).clear();
        element(by.id('title')).sendKeys('new title');
        authoring.save();
        authoring.close();
        //Check saved values
        browser.get('/#/workspace/content');
        workspace.switchToDesk('Personal');
        content.setListView();
        expect(content.getItem(0).element(by.css('[title="new keyword"]')).isPresent()).toBe(true);
        expect(content.getItem(0).element(by.css('[title="new title"]')).isPresent()).toBe(true);
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
        authoring.moveToGroup('MAIN', 0, 'STORY', 1);
        expect(authoring.getGroupItems('MAIN').count()).toBe(0);
        expect(authoring.getGroupItems('STORY').count()).toBe(3);
        authoring.save();
    });

    it('add multiple items to package', function() {
        workspace.switchToDesk('Personal');
        content.setListView();
        content.actionOnItem('Edit package', 0);
        authoring.showSearch();
        authoring.selectSearchItem(0);
        authoring.selectSearchItem(1);
        authoring.selectSearchItem(2);
        authoring.addMultiToGroup('MAIN');
        expect(authoring.getGroupItems('MAIN').count()).toBe(3);
    });
});
