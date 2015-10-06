
'use strict';

module.exports = new Workspace();

var content = require('./content'),
    nav = require('./utils').nav;

function Workspace() {
    this.sideMenu = element(by.id('side-menu'));
    function openContent() {
        return nav('workspace/content');
    }

    function openIngest() {
        return nav('workspace/ingest');
    }

    this.open = this.openContent = openContent;
    this.openIngest = openIngest;

    this.getDesk = function(name) {
        var desks = element.all(by.repeater('desk in userDesks'));
        return desks.all(by.css('[option="' + name.toUpperCase() + '"]'));
    };

    /**
     * Open a workspace of given name, can be both desk or custom
     *
     * @param {string} desk Desk or workspace name.
     */
    this.selectDesk = function(desk) {
        var dropdownBtn = element(by.id('selected-desk')),
        dropdownMenu = element(by.id('select-desk-menu'));

        // open dropdown
        dropdownBtn.click();

        function textFilter(elem) {
            return elem.element(by.tagName('button')).getText()
            .then(function(text) {
                return text.toUpperCase().indexOf(desk.toUpperCase()) >= 0;
            });
        }

        function clickFiltered(filtered) {
            if (filtered.length) {
                return filtered[0].click();
            }
        }

        // try to open desk
        dropdownMenu.all(by.repeater('desk in desks'))
            .filter(textFilter)
            .then(clickFiltered);

        // then try to open custom workspace
        dropdownMenu.all(by.repeater('workspace in wsList'))
            .filter(textFilter)
            .then(clickFiltered);

        // close dropdown if opened
        dropdownMenu.isDisplayed().then(function(shouldClose) {
            if (shouldClose) {
                dropdownBtn.click();
            }
        });
    };

    /**
     * Show name list from right menu
     *
     * @param {string} name
     */
    this.showList = function(name) {
        this.sideMenu.element(by.css('[title="' + name + '"]')).click();
    };

    /**
     * Show the name highlight list
     *
     * @param {string} name
     */
    this.showHighlightList = function(name) {
        var menu = element(by.id('highlightPackage'));
        browser.actions().mouseMove(menu).perform();
        menu.element(by.css('[option="' + name + '"]')).click();
    };

    /**
     * Get the list of items from list
     *
     * @return {promise} list of elements
     */
    this.getItems = function() {
        return element.all(by.repeater('item in items'));
    };

    /**
     * Get the item at 'index' from list
     *
     * @param {number} index
     * @return {promise} element
     */
    this.getItem = function(index) {
        return this.getItems().get(index);
    };

    /** Get the title of the 'index' element
     * of the list
     *
     * @param {number} index
     * @return {promise} title
     */
    this.getItemText = function(index) {
        return this.getItem(index).all(by.id('title')).first().getText();
    };

    /**
     * Open contextual menu for item
     *
     * @param {number} index
     * @return {promise} menu element
     */
    this.openItemMenu = function(index) {
        var itemElem = this.getItem(index);
        browser.actions().mouseMove(itemElem).perform();
        itemElem.element(by.className('icon-dots-vertical')).click();
        return element(by.css('.dropdown-menu.open'));
    };

    /**
     * Perform the 'action' operation on the
     * 'item' element
     *
     * @param {string} action
     * @param {number} item
     */
    this.actionOnItem = function(action, item) {
        var menu = this.openItemMenu(item);
        menu.element(by.partialLinkText(action)).click();
    };

    /**
     * Perform 'submenu' operation on the 'action' menu from
     * 'item' element
     *
     * @param {string} action
     * @param {string} submenu
     * @param {number} item
     */
    this.actionOnItemSubmenu = function(action, submenu, item) {
        var menu = this.openItemMenu(item);
        browser.actions().mouseMove(menu.element(by.partialLinkText(action))).perform();
        menu.element(by.css('[option="' + submenu + '"]')).click();
    };

    /**
     * Open a workspace of given name, can be both desk or custom and then navigate
     * to content view
     *
     * @param {string} desk Desk or workspace name.
     * @return {Promise}
     */
    this.switchToDesk = function(desk) {
        this.selectDesk(desk);

        openContent();

        return browser.wait(function() {
            return element(by.className('list-view')).isPresent();
        }, 300);
    };

    this.selectStage = function(stage) {
        var stages = element(by.css('.desk-stages'));
        return stages.element(by.cssContainingText('.stage-label', stage)).click();
    };

    this.editItem = function(item, desk) {
        this.switchToDesk(desk || 'PERSONAL');
        content.setListView();
        return content.editItem(item);
    };

    this.duplicateItem = function(item, desk) {
        return this.switchToDesk(desk || 'PERSONAL')
        .then(content.setListView)
        .then(function() {
            return content.actionOnItem('Duplicate', item);
        });
    };

    this.filterItems = function(type) {
        element(by.css('.filter-trigger')).click();
        element(by.css('.content-type-filters')).element(by.css('.filetype-icon-' + type)).click();
    };
}
