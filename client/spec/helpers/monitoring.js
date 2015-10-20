
'use strict';

var openUrl = require('./utils').open;
module.exports = new Monitoring();

function Monitoring() {

    this.config = element(by.className('aggregate-settings'));
    this.label = element(by.model('widget.configuration.label'));

    this.openMonitoring = function() {
        openUrl('/#/workspace/monitoring');
    };

    this.showMonitoring = function() {
        element(by.className('big-icon-view')).click();
    };

    this.showSpiked = function() {
        element(by.className('big-icon-spiked')).click();
    };

    /**
     * Open personal monitoring view
     */
    this.showPersonal = function() {
        element(by.className('big-icon-personal')).click();
    };

    /**
     * Open global search view
     */
    this.showSearch = function() {
        element(by.className('big-icon-global-search')).click();
    };

    /**
     * On monitoring view create a new item
     *
     * @param {string} action - the create item action can be: create_text_article,
     * create_preformatted_article and create_package
     */
    this.createItemAction = function(action) {
        element(by.className('svg-icon-plus')).click();
        element(by.id(action)).click();
        browser.sleep(500);
    };

    this.getGroup = function(group) {
        return this.getGroups().get(group);
    };

    this.getGroups = function() {
        return element.all(by.repeater('group in aggregate.groups'));
    };

    this.getItem = function(group, item) {
        return this.getGroup(group).all(by.repeater('item in items')).get(item);
    };

    this.getGroupItems = function(group) {
        return this.getGroup(group).all(by.repeater('item in items'));
    };

    this.getSpikedItems = function() {
        return element.all(by.repeater('item in items'));
    };

    /**
     * Get the personal element at 'index' row
     *
     * @param {number} index
     * @return {object}
     */
    this.getPersonalItem = function(index) {
        return element.all(by.repeater('item in items')).get(index);
    };

    /**
     * Get the personal element text at 'index' row
     *
     * @param {number} index
     * @return {string}
     */
    this.getPersonalItemText = function(index) {
        return this.getPersonalItem(index).element(by.id('title')).getText();
    };

    this.getSpikedItem = function(item) {
        return this.getSpikedItems().get(item);
    };

    this.getSpikedTextItem = function(index) {
        return this.getSpikedItem(index).element(by.id('title')).getText();
    };

    this.getTextItem = function(group, item) {
        return this.getItem(group, item).element(by.id('title')).getText();
    };

    this.searchAction = function(search) {
        element(by.css('.flat-searchbar')).click();
        element(by.model('query')).sendKeys(search);
    };

    /**
     * Perform filter by filterType that can be
     * all, audio, video, text, picture and composite
     *
     * @param {string} fileType
     */
    this.filterAction = function(fileType) {
        element(by.className('filetype-icon-' + fileType)).click();
    };

    this.previewAction = function(group, item) {
        this.getItem(group, item).click();
    };

    this.closePreview = function() {
        element(by.className('close-preview')).click();
    };

    this.getPreviewTitle = function() {
        return element(by.css('.content-container'))
        .element(by.binding('selected.preview.headline'))
        .getText();
    };

    this.setOrder = function(field, switchDir) {
        element(by.id('order_button')).click();
        element(by.id('order_selector')).element(by.partialLinkText(field)).click();
        if (switchDir !== undefined && switchDir) {
            element(by.css('[ng-click="toggleDir()"]')).click();
        }
    };

    this.openAction = function(group, item) {
        browser.actions().doubleClick(
                this.getItem(group, item)
        ).perform();
    };

    this.tabAction = function(tab) {
        element.all(by.css('[ng-click="tab = \'' + tab + '\'"]')).click();
    };

    this.openRelatedItem = function(index) {
        var relatedItem = element.all(by.repeater('relatedItem in relatedItems._items')).get(index);
        relatedItem.all(by.className('related-item')).get(index).click();
    };

    /**
     * Perform the 'action' operation on the
     * 'item' element from 'group'
     *
     * @param {string} action
     * @param {number} group
     * @param {number} item
     */
    this.actionOnItem = function(action, group, item) {
        var menu = this.openItemMenu(group, item);
        menu.element(by.partialLinkText(action)).click();
    };

    /**
     * Perform 'submenu' operation on the 'action' menu from
     * 'item' element from 'group'
     *
     * @param {string} action
     * @param {string} submenu
     * @param {number} group
     * @param {number} item
     */
    this.actionOnItemSubmenu = function(action, submenu, group, item) {
        var menu = this.openItemMenu(group, item);
        browser.actions().mouseMove(menu.element(by.partialLinkText(action))).perform();
        menu.element(by.css('[option="' + submenu + '"]')).click();
    };

    this.selectItem = function(group, item) {
        return this.selectGivenItem(this.getItem(group, item));
    };

    this.selectSpikedItem = function(item) {
        return this.selectGivenItem(this.getSpikedItem(item));
    };

    this.selectGivenItem = function(item) {
        var itemTypeIcon = item.element(by.css('.type-icon'));
        browser.actions().mouseMove(itemTypeIcon).perform();
        return item.element(by.model('item.selected')).click();
    };

    this.spikeMultipleItems = function() {
        return element(by.css('[ng-click="action.spikeItems()"]')).click();
    };

    this.unspikeMultipleItems = function() {
        return element(by.css('[ng-click="action.unspikeItems()"]')).click();
    };

    this.unspikeItem = function(item) {
        var itemElem = this.getSpikedItem(item);
        browser.actions().mouseMove(itemElem).perform();
        itemElem.element(by.className('icon-dots-vertical')).click();
        var menu = element(by.css('.dropdown-menu.open'));
        return menu.element(by.partialLinkText('Unspike')).click();
    };

    this.openItemMenu = function(group, item) {
        var itemElem = this.getItem(group, item);
        browser.actions().mouseMove(itemElem).perform();
        itemElem.element(by.className('icon-dots-vertical')).click();
        return element(by.css('.dropdown-menu.open'));
    };

    this.showMonitoringSettings = function() {
        element.all(by.className('icon-dots-vertical')).first().click();
        browser.wait(function() {
            return element(by.css('.icon-settings')).isDisplayed();
        });
        element(by.css('.icon-settings')).click();
        browser.wait(function() {
            return element.all(by.css('.aggregate-widget-config')).isDisplayed();
        });
        element.all(by.css('[ng-click="goTo(step)"]')).first().click();
    };

    /**
     * Set the label for the current monitoring view widget
     *
     * @param {string} label
     */
    this.setLabel = function(label) {
        this.label.clear();
        this.label.sendKeys(label);
    };

    this.nextStages = function() {
        element(by.id('nextStages')).click();
        browser.sleep(500);
    };

    this.nextSearches = function() {
        element(by.id('nextSearches')).click();
        browser.sleep(500);
    };

    this.previousSearches = function() {
        element(by.id('previousSearches')).click();
        browser.sleep(500);
    };

    this.nextReorder = function() {
        element(by.id('nextReorder')).click();
        browser.sleep(500);
    };

    this.previousReorder = function() {
        element(by.id('previousReorder')).click();
        browser.sleep(500);
    };

    this.previousMax = function() {
        element(by.id('previousMax')).click();
        browser.sleep(500);
    };

    this.cancelSettings = function() {
        element(by.css('[ng-click="cancel()"]')).click();
    };

    this.saveSettings = function() {
        element(by.css('[ng-click="save()"]')).click();
    };

    /**
     * Get the desk at the 'index' row
     *
     *  @param {index} index
     *  @return {promise}
     */
    this.getDesk = function(index) {
        return this.config.all(by.repeater('desk in desks')).get(index);
    };

    this.getStage = function(desk, stage) {
        return this.getDesk(desk).all(by.repeater('stage in deskStages[desk._id]')).get(stage);
    };

    /**
     * Get the search at the 'index' row
     *
     *  @param {index} index
     *  @return {promise}
     */
    this.getSearch = function(index) {
        return this.config.all(by.repeater('search in currentSavedSearches')).get(index);
    };

    this.getSearchText = function(search) {
        return this.getSearch(search).element(by.css('.desk-title')).getText();
    };

    this.toggleDesk = function(desk) {
        this.getDesk(desk).element(by.model('editGroups[desk._id].selected')).click();
    };

    this.toggleStage = function(desk, stage) {
        this.getStage(desk, stage).element(by.css('[ng-click="setStageInfo(stage._id)"]')).click();
    };

    this.togglePersonal = function() {
        element(by.css('[ng-click="setPersonalInfo()"]')).click();
    };

    this.toggleSearch = function(search) {
        this.getSearch(search).element(by.css('[ng-click="setSearchInfo(search._id)"]')).click();
    };

    this.toggleAllSearches = function() {
        element(by.css('[ng-click="initSavedSearches(showAllSavedSearches)"]')).click();
    };

    this.getOrderItem = function(item) {
        return element.all(by.repeater('item in getValues()')).get(item);
    };

    this.getOrderItemText = function(item) {
        return this.getOrderItem(item).element(by.css('.group-title')).getText();
    };

    this.moveOrderItem = function(start, end) {
        var src = this.getOrderItem(start);
        var dst = this.getOrderItem(end);
        return src.waitReady().then(function() {
            browser.actions()
                .mouseMove(src, {x: 0, y: 0})
                .mouseDown()
                .perform()
                .then(function() {
                    dst.waitReady().then(function () {
                        browser.actions()
                            .mouseMove(dst, {x: 5, y: 5})
                            .mouseUp()
                            .perform();
                    });
                });
        });
    };

    this.getMaxItem = function(item) {
        return element.all(by.repeater('max in getValues()')).get(item);
    };

    this.setMaxItems = function(item, value) {
        var maxItemsInput = this.getMaxItem(item).element(by.id('maxItems'));
        maxItemsInput.clear();
        maxItemsInput.sendKeys(value);
    };

    this.hasClass = function (element, cls) {
        return element.getAttribute('class').then(function (classes) {
            return classes.split(' ').indexOf(cls) !== -1;
        });
    };

    this.showHideList = function() {
        element(by.className('big-icon-view')).click();
    };

    this.openCreateMenu = function() {
        element(by.className('sd-create-btn')).click();
        browser.sleep(100);
    };

    this.openSendMenu = function() {
        element(by.className('svg-icon-sendto')).click();
        browser.sleep(100);
    };

    this.publish = function() {
        element(by.css('[ng-click="_publish()"]')).click();
    };

    this.startUpload = function() {
        element(by.id('start-upload-btn')).click();
    };

    this.uploadModal = element(by.className('upload-media'));

    this.fetchAs = function(group, item) {
        this.actionOnItem('Fetch To', group, item);
        return element(by.css('[ng-click="send()"]')).click();
    };

    this.fetchAndOpen = function(group, item) {
        this.actionOnItem('Fetch To', group, item);
        return element(by.css('[ng-click="send(true)"]')).click();
    };

    /**
     * Create a package and include selected items
     */
    this.createPackageFromItems = function() {
        element(by.css('[ng-click="action.createPackage()"]')).click();
    };

    /**
     * Check if on monitoring view an item from group is marked for highlight
     * @param {string} highlight
     * @param {number} group
     * @param {number} item
     */
    this.checkMarkedForHighlight = function(highlight, group, item) {
        var crtItem = this.getItem(group, item);
        expect(crtItem.element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
        browser.actions().mouseMove(crtItem.element(by.className('icon-star-color'))).perform();
        element.all(by.css('.dropdown-menu.open li')).then(function (items) {
            expect(items[1].getText()).toContain(highlight);
        });
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
     * Open a workspace of given name, can be both desk or custom and then navigate
     * to content view
     *
     * @param {string} desk Desk or workspace name.
     * @return {Promise}
     */
    this.switchToDesk = function(desk) {
        this.selectDesk(desk);

        this.openMonitoring();

        return browser.wait(function() {
            return element(by.className('list-view')).isPresent();
        }, 300);
    };

}
