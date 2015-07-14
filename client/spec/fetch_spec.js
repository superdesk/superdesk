
'use strict';

var workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Fetch', function() {
    beforeEach(function() {
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
    });

    fit('items in personal should have copy icon and in desk should have duplicate icon',
        function() {
            var itemEL = content.getItem('item4');
            browser.actions().mouseMove(itemEL).perform();
            itemEL.element(by.className('more-activity-toggle')).click();
            expect(itemEL.element(by.css('[title="Duplicate"]')).isDisplayed()).toBe(true);
            expect(browser.driver.isElementPresent(by.css('[title="Copy"]'))).toBe(false);

            workspace.switchToDesk('PERSONAL');
            content.setListView();
            itemEL = content.getItem('item1');
            browser.actions().mouseMove(itemEL).perform();
            expect(itemEL.element(by.css('[title="Copy"]')).isDisplayed()).toBe(true);
            expect(browser.driver.isElementPresent(by.css('[title="Duplicate"]'))).toBe(false);
        }
    );

    it('can fetch from ingest with keyboards', function() {
        var body;
        workspace.openIngest();
        // select & fetch item
        body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');
        workspace.open();
        workspace.switchToDesk('SPORTS DESK');
        expect(content.count()).toBe(3);
    });

    it('can fetch from ingest with menu', function() {
        workspace.openIngest();
        content.actionOnItem('Fetch', 0);
        workspace.openContent();
        expect(content.count()).toBe(3);
    });

    it('can fetch from content with menu', function() {
        workspace.openIngest();
        content.actionOnItem('Fetch', 0);
        workspace.openContent();
        workspace.switchToDesk('PERSONAL');
        expect(content.count()).toBe(3);
        content.actionOnItem('Copy', 'item1');
        expect(content.count()).toBe(4);
    });

    it('can fetch as', function() {
        workspace.openIngest();
        content.actionOnItem('Fetch As', 0);
        content.send();
        workspace.openContent();
        expect(content.count()).toBe(3);
    });

    it('can fetch multiple items', function() {
        workspace.openIngest();
        content.selectItem(0);
        element(by.id('fetch-all-btn')).click();
        workspace.openContent();
        expect(content.count()).toBe(3);
    });

    it('can fetch as multiple items', function() {
        workspace.openIngest();
        content.selectItem(0);
        element(by.id('fetch-all-as-btn')).click();
        content.send();
        workspace.openContent();
        expect(content.count()).toBe(3);
    });
});
