
'use strict';

module.exports = new Content();

function Content() {
    this.setListView = function() {
        var list = element(by.css('[title="switch to list view"]'));
        return list.isDisplayed().then(function(isVisible) {
            if (isVisible) {
                list.click();
            }
        });
    };
    this.setGridView = function() {
        var grid = element(by.css('[title="switch to grid view"]'));
        return grid.then(function(isVisible) {
            if (isVisible) {
                grid.click();
            }
        });
    };
    this.getItem = function(item) {
        return element.all(by.repeater('items._items')).get(item);
    };
    this.actionOnItem = function(action, item) {
        var crtItem;
        return this.getItem(item)
            .waitReady().then(function(elem) {
                crtItem = elem;
                return browser.actions().mouseMove(crtItem).perform();
            }).then(function() {
                return crtItem
                    .element(by.css('[title="' + action + '"]'))
                    .click();
            });
    };
}
