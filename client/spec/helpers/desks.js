
'use strict';

var openUrl = require('./utils').open;

module.exports = new Desks();

function Desks() {
    /** List of desks on desk settings list **/
    this.list = element.all(by.repeater('desk in desks._items'));
    /** For an item from desks settings list, get his name **/
    this.name = element(by.model('desk.name'));
    /** The list of tabs in desk settings wizard **/
    this.tabs = element.all(by.repeater('step in steps'));
    /** The list of stages from stages tab on desks settings wizard **/
    this.stages = element.all(by.repeater('stage in stages'));

    /**
     * Open the desk settings wizard
     **/
    this.openDesksSettings = function() {
        openUrl('/#/settings/desks');
        browser.sleep(500);
    };

    /**
     * Get a desk item by name on desks settings list
     * @param {string} name of desk
     * @return {promise} desk element
     **/
    this.getRow = function(name) {
        return this.list.filter(function(elem, index) {
            return elem.element(by.binding('desk.name')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    /**
     * Return the numbers of desks on desks settings list
     * @return {integer}
     **/
    this.getCount = function() {
        return this.list.count();
    };

    /**
     * Starts the edit action for named desk from desks settings list
     * @param {string} name of desk
     **/
    this.edit = function(name) {
        this.getRow(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-dots-vertical')).click();
            rows[0].element(by.className('icon-pencil')).click();
            browser.sleep(500);
        });
    };

    /**
     * Remove named desk from desks settings list
     * @param {string} name of desk
     **/
    this.remove = function(name) {
        this.getRow(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-dots-vertical')).click();
            rows[0].element(by.className('icon-trash')).click();
            browser.sleep(500);
            element(by.buttonText('OK')).click();
        });
    };

    /**
     * Get desk settings wizard tab by name
     * @param {string} name of tab
     * @return {promise} tab element
     **/
    this.getTab = function(name) {
        return this.tabs.filter(function(elem, index) {
            return elem.element(by.binding('step.title')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    /**
     * Set named tab as the current one on desk settings wizard
     * @param {string} name of tab
     **/
    this.showTab = function(name) {
        this.getTab(name).then(function(rows) {
            rows[0].click();
            browser.sleep(500);
        });
    };

    /**
     * Get a named stage on desk wizard, stages tab
     * @param {string} name of stage
     * @return {promise} stage element
     **/
    this.getStage = function(name) {
        return this.stages.filter(function(elem, index) {
            return elem.element(by.binding('stage.name')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    /**
     * Edit a named stage on desk settings wizard, stages tab
     * @param {string} name of stage
     **/
    this.editStage = function(name) {
        this.getStage(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-pencil')).click();
            browser.sleep(500);
        });
    };

    /**
     * Delete a named stage on desk settings wizard, stages tab
     * @param {string} name of stage
     **/
    this.removeStage = function(name) {
        this.getStage(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-trash')).click();
        });
    };

    /**
     * Saves desk settings and close the desk settings wizard
     **/
    this.save = function() {
        element(by.id('save')).click();
    };
}
