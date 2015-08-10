
'use strict';

module.exports = new Authoring();

//var openUrl = require('./utils').open;
var nav = require('./utils').nav;

function Authoring() {

    this.lock = element(by.css('[ng-click="lock()"]'));
    this.publish_button = element(by.css('[ng-click="publish()"]'));
    this.close_button = element(by.css('[ng-click="close()"]'));

    this.navbarMenuBtn = $('.dropdown-toggle.sd-create-btn');
    this.newEmptyPackageLink = element(by.id('create_package'));
    this.infoIconsBox = $('.info-icons');

    /**
     * Navigate to the initial authoring page.
     *
     * @return {Object} a promise
     */
    this.openAuthoringHome = function () {
        //return openUrl('/#/authoring');  //authoring main page;
        return nav('authoring');
    };

    /**
     * Find all file type icons in the item's info icons box matching the
     * given file type.
     *
     * @param {string} itemType - the item type of interest, e.g. 'text',
     *   'composite', 'picture', etc.
     * @return {Object} a promise that is resolved with all DOM elements found
     */
    this.findItemTypeIcons = function (itemType) {
        var selector = '.filetype-icon-' + itemType;
        return this.infoIconsBox.all(by.css(selector));
    };

    /**
     * Send item to given desk
     *
     * @param {string} desk Desk name
     * @param {string} stage Stage name
     */
    this.sendTo = function(desk, stage) {
        element(by.id('send-to-btn')).click();
        this.sendToSidebarOpened(desk, stage);
    };

    this.confirmSendTo = function() {
        element(by.className('modal-content')).all(by.css('[ng-click="ok()"]')).click();
    };

    this.sendToSidebarOpened = function(desk, stage) {
        var sidebar = element(by.css('.send-to-pane')),
            dropdown = sidebar.element(by.css('.desk-select .dropdown-toggle'));

        dropdown.waitReady();
        dropdown.click();
        sidebar.element(by.buttonText(desk)).click();
        if (stage !== undefined) {
            sidebar.element(by.buttonText(stage)).click();
        }
        sidebar.element(by.buttonText('send')).click();
    };

    this.markAction = function() {
        return element(by.className('svg-icon-add-to-list')).click();
    };

    this.createTextItem = function() {
        return element(by.css('[class="dropdown-toggle sd-create-btn"]')).click().then(function() {
            return element(by.id('create_text_article')).click();
        });
    };

    this.close = function() {
        return this.close_button.click();
    };

    this.publish = function() {
        return this.publish_button.click();
    };

    this.save = function() {
        element(by.css('[ng-click="save(item)"]')).click();
        return browser.wait(function() {
            return element(by.buttonText('SAVE')).getAttribute('disabled');
        });
    };

    this.edit = function() {
        return element(by.id('Edit')).click();
    };

    this.showSearch = function() {
        return element(by.id('Search')).click();
    };

    this.showMulticontent = function() {
        element(by.id('Aggregate')).click();
    };

    this.showVersions = function() {
        return element(by.id('Versioning')).click();
    };

    this.showHistory = function() {
        this.showVersions();
        return element(by.css('[ng-click="tab = \'history\'"]')).click();
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

    this.getGroupedItems = function(group) {
        return element(by.css('[data-title="' + group.toLowerCase() + '"]'))
            .all(by.repeater('child in item.childData'));
    };

    this.getGroupItems = function(group) {
        return element(by.id(group.toUpperCase())).all(by.repeater('item in group.items'));
    };

    this.getHistoryItems = function() {
        return element.all(by.repeater('version in versions'));
    };

    this.getHistoryItem = function(index) {
        return this.getHistoryItems().get(index);
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
        element(by.className('icon-dots-vertical')).click();
        browser.actions().mouseMove(element(by.css('.highlights-toggle .dropdown-toggle'))).perform();
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
