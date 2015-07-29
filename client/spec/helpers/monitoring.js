
'use strict';

var openUrl = require('./utils').open;
module.exports = new Monitoring();

function Monitoring() {

    var config = element(by.className('aggregate-settings'));

    this.openMonitoring = function() {
        openUrl('/#/workspace/monitoring');
    };

    this.getGroup = function(group) {
        return element.all(by.repeater('group in aggregate.getGroups()')).get(group);
    };

    this.getItem = function(group, item) {
        return this.getGroup(group).all(by.repeater('item in items')).get(item);
    };

    this.getTextItem = function(group, item) {
        return this.getItem(group, item).element(by.id('title')).getText();
    };

    this.searchAction = function(search) {
        element(by.model('query')).sendKeys(search);
    };

    this.previewAction = function(group, item) {
        this.getItem(group, item).click();
    };

    this.getPreviewTitle = function() {
        return element(by.css('.content-container'))
        .element(by.binding('selected.preview.headline'))
        .getText();
    };

    this.openAction = function(group, item) {
        browser.actions().doubleClick(
                this.getItem(group, item)
        ).perform();
    };

    this.showMonitoringSettings = function() {
        element(by.css('.icon-dots-vertical')).click();
        browser.wait(function() {
            return element(by.css('.icon-settings')).isDisplayed();
        });
        element(by.css('.icon-settings')).click();
        browser.wait(function() {
            return element.all(by.css('.aggregate-widget-config')).isDisplayed();
        });
        element(by.css('[ng-click="goTo(step)"]')).click();
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

    this.getDesk = function(desk) {
        return config.all(by.repeater('desk in desks')).get(desk);
    };

    this.getStage = function(desk, stage) {
        return this.getDesk(desk).all(by.repeater('stage in deskStages[desk._id]')).get(stage);
    };

    this.getSearch = function(search) {
        return config.all(by.repeater('search in searches')).get(search);
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
}
