
'use strict';

var openUrl = require('./utils').open;
module.exports = new Dashboard();

function Dashboard() {

    /**
     * Open dashboard for current selected desk/custom workspace.
     */
    this.openDashboard = function() {
        openUrl('/#/workspace');
    };

    /**
     * Open the dashboard setting. The dashboard page should be already opened.
     */
    this.showDashboardSettings = function() {
        element.all(by.className('svg-icon-plus')).first().click();
    };

    /**
     * Get the list of available widgets on dashboard settings.
     *
     * @return {promise} list of widgets
     */
    this.getSettingsWidgets = function() {
        return element.all(by.repeater('widget in dashboard.availableWidgets'));
    };

    /**
     * Get the widget at index 'index' from the list of available widgets on
     * dashboard settings.
     *
     * @param {number} index
     * @return {promise} widget element
     */
    this.getSettingsWidget = function(index) {
        return this.getSettingsWidgets().get(index);
    };

    /**
     * Add to current dashboard the widget at index 'index' from the list
     * of available widgets on dashboard settings.
     *
     * @param {number} index
     */
    this.addWidget = function(index) {
        this.getSettingsWidget(index).click();
        element.all(by.css('[ng-click="dashboard.addWidget(dashboard.selectedWidget)"]')).first().click();
    };

    /**
     * Close the dashboard settings.
     */
    this.doneAction = function() {
        element.all(by.css('[ng-click="dashboard.add = false"]')).first().click();
    };

    /**
     * Get the list of widgets from current dashboard
     *
     * @return {promise} widgets list
     **/
    this.getWidgets = function() {
        return element.all(by.repeater('widget in widgets'));
    };

    /**
     * Get the widget at index 'index' from the current dashboard.
     *
     * @param {number} index
     * @return {promise} widget element
     */
    this.getWidget = function(index) {
        return this.getWidgets().get(index);
    };

    /**
     * Get the label for widget at index 'index'
     * from the current dashboard.
     *
     * @param {number} index
     * @return {text} label
     */
    this.getWidgetLabel = function(index) {
        return this.getWidget(index).all(by.css('.widget-title')).first().getText();
    };

    /**
     * Show the monitoring settings for 'index' widget
     *
     * @param {number} index
     */
    this.showMonitoringSettings = function(index) {
        this.getWidget(index).all(by.css('[ng-click="openConfiguration()"]')).first().click();
        browser.wait(function() {
            return element.all(by.css('.aggregate-widget-config')).isDisplayed();
        });
    };

    /**
     * Get groups for widget
     *
     * @param {number} widget index
     * @return {promise} list of groups elements
     */
    this.getGroups = function(widget) {
        return this.getWidget(widget).all(by.repeater('group in agg.cards'));
    };

    /**
     * Get a group for a widget
     *
     * @param {number} widget index
     * @param {number} group index
     * @return {promise} group element
     */
    this.getGroup = function(widget, group) {
        return this.getGroups(widget).get(group);
    };

    /**
     * Get the list of items from a group for a widget
     *
     * @param {number} widget index
     * @param {number} group index
     * @return {promise} items element list
     */
    this.getGroupItems = function(widget, group) {
        return this.getGroup(widget, group).all(by.repeater('item in items'));
    };

    /**
     * Get an item from a group for a widget
     *
     * @param {number} widget index
     * @param {number} group index
     * @param {number} item index
     * @return {promise} item element
     */
    this.getItem = function(widget, group, item) {
        return this.getGroupItems(widget, group).get(item);
    };

    /**
     * Get an item from a group for a widget
     *
     * @param {number} widget index
     * @param {number} group index
     * @param {number} item index
     * @return {promise} item element
     */
    this.getTextItem = function(widget, group, item) {
        return this.getItem(widget, group, item).element(by.id('title')).getText();
    };

    /**
     * Get an search text box widget
     *
     * @param {number} widget index
     * @return {promise} item element
     */
    this.getSearchTextBox = function(widget) {
        return this.getWidget(widget).element(by.css('.search-box input'));
    };

    /**
     * Get an search text box widget
     *
     * @param {number} widget index
     * @param {string} searchText search string
     */
    this.doSearch = function(widget, searchText) {
        this.getSearchTextBox(widget).sendKeys(searchText);
    };
}
