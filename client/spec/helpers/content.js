
'use strict';

var nav = require('./utils').nav;

module.exports = new Content();

function Content() {

    this.send = send;

    this.setListView = function() {
        nav('workspace/content');

        var list = element(by.css('i.icon-th-list'));
        return list.isDisplayed()
            .then(function(isVisible) {
                if (isVisible) {
                    list.click();
                }
            });
    };

    this.setGridView = function() {
        var grid = element(by.css('[tooltip="switch to grid view"]'));
        return grid.then(function(isVisible) {
            if (isVisible) {
                grid.click();
            }
        });
    };

    this.getItems = function() {
        return element.all(by.repeater('items._items'));
    };

    this.getItem = function(item) {
        return this.getItems().filter(testHeadline).first();

        function testHeadline(elem, index) {
            if (typeof item === 'number') {
                // BC: get item by its index
                return index === item;
            } else {
                return elem.element(by.className('headline')).getText()
                    .then(function(text) {
                        return text.toLowerCase().indexOf(item) >= 0;
                    });
            }
        }
    };

    this.actionOnItem = function(action, item) {
        var menu = this.openItemMenu(item);
        return menu.element(by.partialLinkText(action)).click();
    };

    this.openItemMenu = function(item) {
        var itemElem = this.getItem(item);
        browser.actions().mouseMove(itemElem).perform();
        itemElem.element(by.className('icon-dots-vertical')).click();
        return element(by.css('.dropdown-menu.active'));
    };

    this.checkMarkedForHighlight = function(highlight, item) {
        var crtItem = this.getItem(item);
        expect(crtItem.element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
        expect(crtItem.element(by.className('icon-star-color')).getAttribute('tooltip-html-unsafe'))
            .toContain(highlight);
    };

    this.getCount = function () {
        browser.wait(function() {
            // make sure list is there before counting
            return element(by.css('.list-view')).isPresent();
        });
        return element.all(by.repeater('items._items')).count();
    };

    /**
     * @alias this.getCount
     */
    this.count = this.getCount;

    this.selectItem = function(item) {
        var crtItem = this.getItem(item);
        browser.actions().mouseMove(crtItem.element(by.className('filetype-icon-text'))).perform();
        return crtItem.element(by.css('[ng-change="toggleSelected(item)"]')).click();
    };

    this.spikeItems = function() {
        element(by.css('[ng-click="action.spikeItems()"]')).click();
    };

    this.unspikeItems = function() {
        element(by.css('[ng-click="action.unspikeItems()"]')).click();
    };

    this.selectSpikedList = function() {
        element(by.css('[ng-click="toggleSpike()"')).click();
    };

    this.createPackageFromItems = function() {
        var elem = element(by.css('[class="multi-action-bar ng-scope"]'));
        elem.element(by.className('icon-package-plus')).click();
        browser.sleep(500);
    };

    function send() {
        return element(by.id('send-item-btn')).click();
    }
}
