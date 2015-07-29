
'use strict';

module.exports = new Authoring();

function Authoring() {

    this.lock = element(by.css('[ng-click="lock()"]'));
    this.publish = element(by.css('[ng-click="publish()"]'));
    this.close_button = element(by.css('[ng-click="close()"]'));

    /**
     * Send item to given desk
     *
     * @param {string} desk Desk name
     */
    this.sendTo = function sendTo(desk) {
        var sidebar = element(by.css('.send-to-pane')),
            dropdown = sidebar.element(by.css('.desk-select .dropdown-toggle'));

        element(by.id('send-to-btn')).click();
        dropdown.waitReady();
        dropdown.click();

        sidebar.element(by.buttonText(desk)).click();
        sidebar.element(by.buttonText('send')).click();
    };

    this.markAction = function() {
        return element(by.className('svg-icon-add-to-list')).click();
    };

    this.close = function() {
        return this.close_button.click();
    };

    this.save = function() {
        element(by.css('[ng-click="save(item)"]')).click();
        return browser.wait(function() {
            return element(by.buttonText('SAVE')).getAttribute('disabled');
        });
    };

    this.showSearch = function() {
        return element(by.id('Search')).click();
    };

    this.showMulticontent = function() {
        element(by.id('Aggregate')).click();
    };

    this.showVersions = function() {
        return element(by.id('Versions')).click();
    };

    this.getSearchItem = function(item) {
        return element.all(by.repeater('pitem in contentItems')).get(item);
    };

    this.getSearchItemCount = function () {
        return element.all(by.repeater('pitem in contentItems')).count();
    };

    this.addToGroup = function(item, group) {
        var crtItem = this.getSearchItem(item);
        browser.actions().mouseMove(crtItem).perform();
        crtItem.element(by.css('[title="Add to package"]')).click();
        var groups = crtItem.all(by.repeater('t in groupList'));
        return groups.all(by.css('[option="' + group.toUpperCase() + '"]')).click();
    };

    this.addMultiToGroup = function(group) {
        return element.all(by.css('[class="icon-package-plus"]')).first()
            .waitReady()
            .then(function(elem) {
                return elem.click();
            }).then(function() {
                var groups = element(by.repeater('t in groupList'));
                return groups.all(by.css('[option="' + group.toUpperCase() + '"]'))
                    .click();
            });
    };

    this.getGroupItems = function(group) {
        return element(by.id(group.toUpperCase())).all(by.repeater('item in group.items'));
    };

    this.getGroupItem = function(group, item) {
        return this.getGroupItems(group).get(item);
    };

    this.moveToGroup = function(srcGroup, scrItem, dstGroup, dstItem) {
        var src = this.getGroupItem(srcGroup, scrItem).element(by.css('[class="info"]'));
        var dst = this.getGroupItem(dstGroup, dstItem).element(by.css('[class="info"]'));
        return src.waitReady().then(function() {
            browser.actions()
                .mouseMove(src, {x: 0, y: 0})
                .mouseDown()
                .perform()
                .then(function() {
                    dst.waitReady().then(function () {
                        browser.actions()
                            .mouseMove(dst, {x: 0, y: 0})
                            .mouseUp()
                            .perform();
                    });
                });
        });
    };

    this.selectSearchItem = function(item) {
        var crtItem = this.getSearchItem(item);
        var icon = crtItem.element(by.tagName('i'));
        return icon.waitReady().then(function() {
            browser.actions()
                .mouseMove(icon)
                .perform();
        }).then(function() {
            crtItem.element(by.css('[ng-click="addToSelected(pitem)"]')).click();
        });
    };

    this.markForHighlights = function() {
        element(by.className('svg-icon-add-to-list')).click();
    };

    this.getSubnav = function() {
        return element(by.id('subnav'));
    };

    this.checkMarkedForHighlight = function(highlight, item) {
        expect(element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
        expect(element(by.className('icon-star-color')).getAttribute('tooltip-html-unsafe'))
            .toContain(highlight);
    };

    this.writeText = function (text) {
        element(by.model('item.body_html')).all(by.className('editor-type-html')).sendKeys(text);
    };
    this.writeTextToHeadline = function (text) {
        element(by.model('item.headline')).all(by.className('editor-type-html')).sendKeys(text);
    };
    this.writeTextToAbstract = function (text) {
        element(by.model('item.abstract')).all(by.className('editor-type-html')).sendKeys(text);
    };

}
