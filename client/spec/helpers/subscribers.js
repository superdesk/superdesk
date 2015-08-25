'use strict';

var openUrl = require('./utils').open;

module.exports = new Subscribers();

function Subscribers() {
    this.list = element.all(by.repeater('subscriber in subscribers._items'));
    this.saveSubscriberButton = element(by.css('[ng-click="save()"]'));
    this.cancelSubscriberButton = element(by.css('[ng-click="cancel()"]'));

    this.get = function() {
        openUrl('/#/settings/publish');
        browser.sleep(500);
    };

    this.getSubscriber = function(name) {
        return this.list.filter(function(elem, index) {
            return elem.element(by.binding('subscriber.name')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    this.getCount = function(index) {
        return this.list.count();
    };

    this.edit = function(name) {
        this.getSubscriber(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-pencil')).click();
            browser.sleep(500);
        });
    };

    this.setType = function(type) {
        element(by.css('#subType option[value="string:' + type + '"]')).click();
    };

    this.cancel = function() {
        this.cancelSubscriberButton.click();
    };
}
