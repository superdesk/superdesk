var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace;

describe('Content', function() {
    'use strict';

    beforeEach(openUrl('/#/workspace/content'));

    beforeEach(function() {
        openUrl('/#/workspace/content')();
        workspace.openPersonal();
        expect(element.all(by.repeater('items._items')).count()).toBe(4);
    });

    it('increment package version', function() {
        var packageItem = element.all(by.repeater('items._items')).first().element(by.className('type-icon'));

        // Edit package
        browser.actions().mouseMove(packageItem).perform();
        element.all(by.repeater('activity in activities')).
        each(function(activity_el, index) {
            if (index === 1) {
                activity_el.click();
            }
        });

        // Open the item search tab
        browser.sleep(300);
        // element(by.className("big-icon-view")).click();
        element.all(by.repeater('widget in widgets')).first().click();

        // Add the first item to the package
        var item1 = element.all(by.repeater('pitem in contentItems')).first();
        browser.actions().mouseMove(item1).perform();
        element.all(by.className('icon-package-plus')).first().click();
        element.all(by.repeater('t in groupList')).first().click();
        element(by.buttonText('SAVE')).click();

        // Open the versions tab
        element(by.className('big-icon-revision')).click();

        // Expect 2 versions of the package
        expect(element.all(by.repeater('version')).count()).toBe(2);
    });
});
