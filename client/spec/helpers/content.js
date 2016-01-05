
'use strict';

var nav = require('./utils').nav;

module.exports = new Content();

function Content() {

    this.send = send;

    this.setListView = function(noNavigate) {
        if (noNavigate === undefined || !noNavigate) {
            nav('workspace/content');
        }

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
        return element.all(by.className('media-box'));
    };

    this.getItem = function(item) {
        return this.getItems().filter(testHeadline).first();

        function testHeadline(elem, index) {
            if (typeof item === 'number') {
                // BC: get item by its index
                return index === item;
            } else {
                return elem.element(by.className('item-heading')).getText()
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

    this.editItem = function(item) {
        return this.actionOnItem('Edit', item);
    };

    function waitFor(elem, time) {
        return browser.wait(function() {
            return elem.isDisplayed();
        }, time || 800);
    }

    this.openItemMenu = function(item) {
        this.getItem(item).click();

        var preview = element(by.id('item-preview'));
        waitFor(preview);

        var toggle = preview.element(by.className('icon-dots-vertical'));
        waitFor(toggle);

        toggle.click();

        var menu = element(by.css('.dropdown-menu.open'));
        waitFor(menu);
        return menu;
    };

    this.previewItem = function(item) {
        this.getItem(item).click();

        var preview = element(by.id('item-preview'));
        waitFor(preview);
    };

    this.closePreview = function() {
        element(by.className('close-preview')).click();
    };

    this.checkMarkedForHighlight = function(highlight, item) {
        var crtItem = this.getItem(item);
        expect(crtItem.element(by.className('icon-star')).isDisplayed()).toBeTruthy();
        expect(crtItem.element(by.className('icon-star')).getAttribute('tooltip-html-unsafe'))
            .toContain(highlight);
    };

    var list = element(by.className('list-view'));

    this.getCount = function () {
        waitFor(list);
        return list.all(by.css('.media-box')).count();
    };

    this.getItemCount = function () {
        waitFor(list);
        return list.all(by.css('.media-box')).count();
    };

    /**
     * @alias this.getCount
     */
    this.count = this.getCount;

    this.selectItem = function(item) {
        var crtItem = this.getItem(item);
        var typeIcon = crtItem.element(by.className('type-icon'));
        expect(typeIcon.isDisplayed()).toBe(true);
        browser.actions().mouseMove(typeIcon).perform();
        var checkbox = element(by.className('selectbox'));
        browser.wait(checkbox.isDisplayed, 10000);
        browser.pause();
        expect(checkbox.isDisplayed()).toBe(true);
        return checkbox.click();
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
        elem.element(by.className('big-icon-package-create')).click();
        browser.sleep(500);
    };

    this.getWidgets = function() {
        return element(by.className('navigation-tabs')).all(by.repeater('widget in widgets'));
    };

    this.getItemType = function(itemType) {
        var itemTypeClass = 'filetype-icon-' + itemType;
        return element(by.className('authoring-header__general-info')).all(by.className(itemTypeClass)).first();
    };

    function send() {
        return element(by.css('[ng-click="send()"]')).click();
    }
}
