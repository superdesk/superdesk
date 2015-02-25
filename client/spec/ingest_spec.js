
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace;

describe('Ingest', function() {

    beforeEach(openUrl('/#/workspace/ingest'));

    it('can fetch with keyboard', function() {
        workspace.openDesk();
        expect(element.all(by.repeater('items._items')).count()).toBe(1);

        // select & fetch item
        var body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');

        // go to content and see it there
        browser.get('/#/workspace/content');
        workspace.openDesk();
        expect(element.all(by.repeater('item in items')).count()).toBe(1);
    });
});
