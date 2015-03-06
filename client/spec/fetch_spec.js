
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
	content = require('./helpers/pages').content;

describe('Fetch', function() {

    beforeEach(openUrl('/#/workspace/content'));

    it('can fetch from ingest with keyboards', function() {
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(2);
        browser.get('/#/workspace/ingest');
        workspace.switchToDesk('SPORTS DESK');

        // select & fetch item
        var body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');

        // go to content and see it there
        browser.get('/#/workspace/content');
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    it('can fetch from ingest with menu', function() {
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(2);
        browser.get('/#/workspace/ingest');
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();

        content.actionOnItem('Fetch', 0);

        browser.get('/#/workspace/content');
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    xit('can fetch from content with keyboards', function() {
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        browser.get('/#/workspace/ingest');
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        content.actionOnItem('Fetch', 0);
        browser.get('/#/workspace/content');
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(3);

        // select & fetch item
        var body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');

        // go to content and see it there
        workspace.switchToDesk('PERSONAL');
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(4);
    });

    it('can fetch from ingest with menu', function() {
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        browser.get('/#/workspace/ingest');
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();
        content.actionOnItem('Fetch', 0);
        browser.get('/#/workspace/content');
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(3);

        content.setListView();
        content.actionOnItem('Fetch', 0);

        workspace.switchToDesk('PERSONAL');
        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).count()).toBe(4);
    });
});
