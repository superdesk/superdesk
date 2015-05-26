
'use strict';

module.exports = new Content();

function Content() {

    this.getItem = getItem;
    this.editItem = editItem;
    this.getCount = getCount;

    this.setListView = function() {
        var list = element(by.css('.list-layout'));
        return list.isDisplayed();
    };

    this.setGridView = function() {
        var grid = element(by.css('[tooltip="switch to grid view"]'));
        return grid.then(function(isVisible) {
            if (isVisible) {
                grid.click();
            }
        });
    };

    this.actionOnItem = function(action, item) {
        var crtItem;
        return this.getItem(item)
            .then(function(elem) {
                crtItem = elem;
                return browser.actions().mouseMove(crtItem).perform();
            }).then(function() {
                return crtItem
                    .element(by.css('[title="' + action + '"]'))
                    .click();
            });
    };

    this.checkMarkedForHighlight = function(highlight, item) {
        var crtItem = this.getItem(item);
        expect(crtItem.element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
        expect(crtItem.element(by.className('icon-star-color')).getAttribute('tooltip-html-unsafe')).toContain(highlight);
    };

    function getCount() {
        return items().count();
    }

    function getItem(index) {
        var item = items().get(index || 0);
        browser.wait(function() {
            return item.isPresent();
        });
        return item;
    }

    function editItem(index) {
        var item = getItem(index);
        item.element(by.css('.headline')).click();
        return element(by.id('authoring-edit-btn')).click();
    }

    function items() {
        return element.all(by.repeater('items._items'));
    }
}
