
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
}
