
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace;

describe('Content', function() {

    function selectedHeadline() {
        return element(by.binding('selected.preview.headline')).getText();
    }

    beforeEach(function() {
        openUrl('/#/workspace/content')();
        workspace.switchToDesk('PERSONAL');
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    it('can navigate with keyboard', function() {
        var body = $('body');
        body.sendKeys(protractor.Key.UP);
        expect(selectedHeadline()).toBe('package1');

        body.sendKeys(protractor.Key.DOWN);
        expect(selectedHeadline()).toBe('item1');

        body.sendKeys(protractor.Key.RIGHT);
        expect(selectedHeadline()).toBe('item2');

        body.sendKeys(protractor.Key.LEFT);
        expect(selectedHeadline()).toBe('item1');

        body.sendKeys(protractor.Key.UP);
        expect(selectedHeadline()).toBe('package1');
    });

    it('can open search with s', function() {
        var body = $('body');
        body.sendKeys('s');
        expect(element(by.id('search-input')).isDisplayed()).toBe(true);
    });

    it('can toggle view with v', function() {
        var body = $('body'),
            gridBtn = element.all(by.css('.view-select button')).first();

        // reset to grid view first
        gridBtn.isDisplayed().then(function(isList) {
            if (isList) {
                gridBtn.click();
            }
        });

        expect(element.all(by.css('.state-border')).count()).toBe(0);
        body.sendKeys('v');
        expect(element.all(by.css('.state-border')).count()).toBe(3);
        body.sendKeys('v');
        expect(element.all(by.css('.state-border')).count()).toBe(0);
    });
});
