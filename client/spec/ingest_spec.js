
var openUrl = require('./helpers/utils').open;

describe('Ingest', function() {
    'use strict';

    beforeEach(openUrl('/#/workspace/ingest'));

    it('can fetch with keyboard', function() {

        // select a desk
        // element(by.partialButtonText('PERSONAL')).click();
        // element(by.buttonText('Sports Desk')).click();
        expect(element.all(by.repeater('items._items')).count()).toBe(1);

        // select & fetch item
        var body = $('body');
        body.sendKeys(protractor.Key.DOWN);
        body.sendKeys('f');

        // go to content and see it there
        browser.get('/#/workspace/content');
        expect(element.all(by.repeater('items._items')).count()).toBe(1);
    });
});
