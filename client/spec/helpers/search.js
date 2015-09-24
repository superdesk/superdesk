
'use strict';

var openUrl = require('./utils').open;
module.exports = new GlobalSearch();

function GlobalSearch() {

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
     * Perform the 'action' operation of the
     * 'index' element of the global search list
     *
     * @param {string} action
     * @param {number} index
     */
    this.actionOnItem = function(action, index) {
        var menu = this.openItemMenu(index);
        menu.element(by.partialLinkText(action)).click();
    };
}
