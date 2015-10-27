
'use strict';

var openUrl = require('./utils').open;
module.exports = new GlobalSearch();

function GlobalSearch() {
    this.ingestRepo = element(by.id('ingest-collection'));
    this.archiveRepo = element(by.id('archive-collection'));
    this.publishedRepo = element(by.id('published-collection'));
    this.archivedRepo = element(by.id('archived-collection'));
    this.goButton = element(by.buttonText('Go'));
    this.searchInput = element(by.id('search-input'));

    /**
     * Open dashboard for current selected desk/custom workspace.
     */
    this.openGlobalSearch = function() {
        openUrl('/#/search');
    };

    /**
     * Set the list view for global search list
     *
     * @return {promise}
     */
    this.setListView = function() {
        var list = element(by.css('i.icon-th-list'));
        return list.isDisplayed()
            .then(function(isVisible) {
                if (isVisible) {
                    list.click();
                    browser.sleep(1000);
                }
            });
    };

    /**
     * Set the grid view for global search list
     *
     * @return {promise}
     */
    this.setGridView = function() {
        var grid = element(by.css('[tooltip="switch to grid view"]'));
        return grid.then(function(isVisible) {
            if (isVisible) {
                grid.click();
                browser.sleep(1000);
            }
        });
    };

    /**
     * Get the list of items from global search
     *
     * @return {promise} list of elements
     */
    this.getItems = function() {
        return element.all(by.repeater('items._items'));
    };

    /**
     * Get the item at 'index' from global
     * search list
     *
     * @param {number} index
     * @return {promise} element
     */
    this.getItem = function(index) {
        return this.getItems().get(index);
    };

    this.itemClick = function(index) {
        var itemElem = this.getItem(index);
        itemElem.click();
    };

    /**
     * Get the search element text at 'index' row
     *
     * @param {number} index
     * @return {string}
     */
    this.getTextItem = function(index) {
        return this.getItem(index).element(by.id('title')).getText();
    };

    /**
     * Open the contextual menu for the 'index'
     * element from global search list
     *
     * @param {integer} index
     * @return {promise} menu element
     */
    this.openItemMenu = function(index) {
        var itemElem = this.getItem(index);
        itemElem.click();
        itemElem.element(by.className('icon-dots-vertical')).click();
        return element(by.css('.dropdown-menu.open'));
    };

    /**
     * Get the list of relatedItems from related tab
     *
     * @return {promise} list of elements
     */
    this.getRelatedItems = function() {
        return element.all(by.repeater('relatedItem in relatedItems._items'));
    };

    /**
     * Perform the 'action' operation of the
     * 'index' element of the global search list
     *
     * @param {string} action
     * @param {number} index
     */
    this.actionOnItem = function(action, index) {
        var menu = this.openItemMenu(index);
        menu.element(by.partialLinkText(action)).waitReady()
        .then(function(elem) {
            elem.click();
        });
    };

    /**
     * Check if on search view an item is marked for highlight
     *
     * @param {string} highlight
     * @param {number} item
     */
    this.checkMarkedForHighlight = function(highlight, item) {
        var crtItem = this.getItem(item);
        expect(crtItem.element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
        expect(crtItem.element(by.className('icon-star-color')).getAttribute('tooltip-html-unsafe'))
            .toContain(highlight);
    };

    /**
     * Show custom search right panel
     */
    this.showCustomSearch = function() {
        browser.sleep(500);
        element(by.className('filter-trigger'))
        .element(by.className('icon-filter-large')).click();
        browser.sleep(500);
    };

    /**
     * Toggle search by item type combobox
     *
     * @param {string} type
     */
    this.toggleByType = function(type) {
        browser.actions().mouseMove(element(by.className('filetype-icon-' + type))).perform();
        element(by.id('filetype-icon-' + type)).click();
    };

    /**
     * Open the filter panel
     */
    this.openFilterPanel = function() {
        element(by.css('.filter-trigger')).click();
    };

    /**
     * Open the search Parameters from
     */
    this.openParameters = function() {
        element(by.id('search-parameters')).click();
    };

    /**
     * Open the search Parameters from
     * @param {string} selectId - Id of the <select> element
     * @param {string} deskName - Name of the desk.
     */
    this.selectDesk = function(selectId, deskName) {
        element(by.id(selectId)).element(by.css('option[label="' + deskName + '"]')).click();
    };

    /**
     * Get the Element Heading by index
     * @param {number} index
     * @return {promise} headline element
     */
    this.getHeadlineElement = function(index) {
        element(by.id('search-parameters')).click();
        return this.getItem(index).element(by.className('item-heading'));
    };

    /**
     * Get the Priority Elements
     * @return {promise} Priority elements
     */
    this.getPriorityElements = function() {
        return element.all(by.repeater('(key,value) in aggregations.priority'));
    };

    /**
     * Get the Priority Element by Index
     * @param {number} index
     * @return {promise} Priority element
     */
    this.getPriorityElementByIndex = function(index) {
        return this.getPriorityElements().get(index);
    };
}
