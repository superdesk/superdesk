'use strict';

module.exports = new UserPrefs();

var openUrl = require('./utils').open;

/**
 * A helper for working with the user preference settings located in the
 * User Profile section.
 */
function UserPrefs() {

    // the Preferences tab
    this.prefsTab = element.all(by.css('.nav-tabs button')).get(1);

    this.btnCheckNone = element.all(by.css('.actions > a')).get(1);
    this.categoryCheckboxes = element.all(
        by.repeater('cat in categories')).all(by.css('[type="checkbox"]'));

    this.btnSave = element.all(by.css('.action-bar > button')).get(0);

    this.navigateTo = function () {
        return openUrl('/#/profile');
    };
}
