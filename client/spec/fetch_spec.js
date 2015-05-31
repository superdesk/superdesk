
'use strict';

var openUrl = require('./helpers/utils').open,
    changeUrl = require('./helpers/utils').changeUrl,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Fetch', function() {

    beforeEach(function(done) {openUrl('/#/workspace/content').then(done);});

    it('items in personal should have copy icon and in desk should have duplicate icon',
        function() {
            var itemEL;

            workspace.switchToDesk('SPORTS DESK').then(content.setListView);
            content.getItem(0).waitReady().then(
                function(elem) {
                    itemEL = elem;
                    return browser.actions().mouseMove(itemEL).perform();
                }).then(function() {
                    itemEL.element(by.className('more-activity-toggle')).click();
                    expect(itemEL.element(by.css('[title="Duplicate"]')).isDisplayed()).toBe(true);
                    expect(browser.driver.isElementPresent(by.css('[title="Copy"]'))).toBe(false);
                });

            workspace.switchToDesk('PERSONAL').then(content.setListView);
            content.getItem(0).waitReady().then(
                function(elem) {
                    itemEL = elem;
                    return browser.actions().mouseMove(itemEL).perform();
                }).then(function() {
                    expect(itemEL.element(by.css('[title="Copy"]')).isDisplayed()).toBe(true);
                    expect(browser.driver.isElementPresent(by.css('[title="Duplicate"]'))).toBe(false);
                });
        }
    );

    it('can fetch from ingest with keyboards', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var body;
        changeUrl('/#/workspace/ingest').then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        }).then(function() {
            // select & fetch item
            body = $('body');
            return body.sendKeys(protractor.Key.DOWN);
        }).then(function() {
            return body.sendKeys('f');
        }).then(function() {
            // go to content and see it there
            return changeUrl('/#/workspace/content');
        }).then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        }).then(
            content.setListView
        );
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    it('can fetch from ingest with menu', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);
        changeUrl('/#/workspace/ingest').then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        }).then(
            content.setListView
        ).then(function() {
            return content.actionOnItem('Fetch', 0);
        }).then(function() {
            return changeUrl('/#/workspace/content');
        }).then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        }).then(
            content.setListView
        );
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    xit('can fetch from content with keyboards', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        browser.get('/#/workspace/ingest');
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        content.actionOnItem('Fetch', 0);
        browser.get('/#/workspace/content');
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        expect(element.all(by.repeater('items._items')).count()).toBe(3);

        // select & fetch item
        var body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');

        // go to content and see it there
        workspace.switchToDesk('PERSONAL');
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        expect(element.all(by.repeater('items._items')).count()).toBe(4);
    });

    it('can fetch from content with menu', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);
        changeUrl('/#/workspace/ingest').then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        }).then(
            content.setListView
        ).then(function() {
            return content.actionOnItem('Fetch', 0);
        }).then(function() {
            return changeUrl('/#/workspace/content');
        }).then(function() {
            return workspace.switchToDesk('PERSONAL');
        }).then(
            content.setListView
        );
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
        content.actionOnItem('Copy', 0).then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        }).then(function() {
            return workspace.switchToDesk('PERSONAL');
        });
        expect(element.all(by.repeater('items._items')).count()).toBe(4);
    });
});
