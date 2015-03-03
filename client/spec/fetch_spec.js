
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace;

describe('Fetch', function() {

    beforeEach(openUrl('/#/workspace/content'));

    xit('can fetch from ingest and desk', function() {
        workspace.openDesk();

        var deskCount;
        element.all(by.repeater('items._items')).count().then(function(count) {
            deskCount = count;
        });

        browser.get('/#/workspace/ingest');
        workspace.openDesk();

        // select & fetch item
        var body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');

        // test item status change
        browser.sleep(500);
        expect(element(by.css('.list-item-view.active')).all(by.css('.media-box.archived')).count()).toBe(1);

        // go to content and see it there
        browser.get('/#/workspace/content');
        workspace.openDesk();
        element.all(by.repeater('items._items')).count().then(function(count) {
            expect(count).toBeGreaterThan(deskCount);
            deskCount = count;
        });

        browser.wait(function() {
            return deskCount != null;
        });

        // select first item
        $('body').sendKeys(protractor.Key.DOWN);

        // archive via dropdown menu
        browser.sleep(200);
        element(by.css('.action-menu button.dropdown-toggle')).click();
        browser.sleep(200);
        element(by.css('.action-menu .activity-archive-content')).click();

        // check that there are more items eventually
        browser.wait(function() {
            return element.all(by.repeater('items._items')).count().then(function(count) {
                return count > deskCount;
            });
        }, 3000);
    });
});
