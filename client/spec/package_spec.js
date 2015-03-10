var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Content', function() {
    'use strict';

    beforeEach(function() {
        openUrl('/#/workspace/content')();
        workspace.switchToDesk('PERSONAL');
        content.setListView();
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    it('increment package version', function() {
        content.actionOnItem('Edit package', 0);

        // Open the item search tab
        element(by.id('Search')).click();

        // Add the first item to the package
        var item1 = element.all(by.repeater('pitem in contentItems')).first();
        browser.actions().mouseMove(item1).perform();

        element.all(by.id('Add-item')).first().click();
        element.all(by.css('[ng-click="addItemToGroup(t, pitem);"]')).first().click();
        element(by.css('[ng-click="save(item)"]')).click();

        // Open the versions tab
        element(by.css('[title="Versions"]')).click();

        // Expect 2 versions of the package
        expect(element.all(by.css('[ng-click="openVersion(version)"]')).count()).toBe(2);
    });
});
