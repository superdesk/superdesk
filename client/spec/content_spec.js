
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/content');

describe('Content', function() {

    function selectedHeadline() {
        return element(by.binding('selected.preview.headline')).getText();
    }

    beforeEach(function(done) {
        openUrl('/#/workspace/content').then(function() {
            workspace.switchToDesk('PERSONAL');
        }).then(done);
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

    function toggle(selectbox) {
        browser.actions().mouseMove(selectbox).perform();
        selectbox.element(by.css('.sd-checkbox')).click();
    }

    it('can select multiple items', function() {
        content.setListView();
        var count = element(by.id('multi-select-count')),
            boxes = element.all(by.css('.list-field.type-icon'));

        toggle(boxes.first());
        expect(count.getText()).toBe('1 Item selected');

        toggle(boxes.last());
        expect(count.getText()).toBe('2 Items selected');

        element(by.css('.big-icon-multiedit')).click();
        expect(browser.getCurrentUrl()).toMatch(/multiedit$/);
        expect(element.all(by.repeater('board in boards')).count()).toBe(2);
    });
});
