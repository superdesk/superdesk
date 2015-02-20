
var openUrl = require('./helpers/utils').open;

describe('Content', function() {
    'use strict';

    beforeEach(openUrl('/#/workspace/content'));

    function selectedHeadline() {
        return element(by.binding('selected.preview.headline')).getText();
    }

    beforeEach(function() {
        element(by.partialButtonText('SPORTS DESK')).click();
        element(by.buttonText('PERSONAL')).click();
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    it('can navigate with keyboard', function() {
        var body = $('body');
        body.sendKeys(protractor.Key.UP);
        expect(selectedHeadline()).toBe('item1');

        body.sendKeys(protractor.Key.DOWN);
        expect(selectedHeadline()).toBe('item2');

        body.sendKeys(protractor.Key.RIGHT);
        expect(selectedHeadline()).toBe('item3');

        body.sendKeys(protractor.Key.LEFT);
        expect(selectedHeadline()).toBe('item2');

        body.sendKeys(protractor.Key.UP);
        expect(selectedHeadline()).toBe('item1');
    });

    it('can open search with s', function() {
        var body = $('body');
        body.sendKeys('s');
        expect(element(by.id('search-input')).isDisplayed()).toBe(true);
    });

    it('can toggle view with v', function() {
        var body = $('body');
        expect(element.all(by.css('.state-border')).count()).toBe(0);
        body.sendKeys('v');
        expect(element.all(by.css('.state-border')).count()).toBe(3);
        body.sendKeys('v');
        expect(element.all(by.css('.state-border')).count()).toBe(0);
    });
});
