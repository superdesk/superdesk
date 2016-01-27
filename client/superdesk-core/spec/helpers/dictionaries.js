
'use strict';

var openUrl = require('./utils').open;

module.exports = new Dictionaries();

function Dictionaries() {
    this.list = element.all(by.repeater('dictionary in dictionaries._items'));
    this.name = element(by.model('dictionary.name'));
    this.languageId = element(by.model('dictionary.language_id'));

    this.get = function() {
        openUrl('/#/settings/dictionaries');
        browser.sleep(500);
    };

    this.getRow = function(name) {
        return this.list.filter(function(elem, index) {
            return elem.element(by.binding('dictionary.name')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    this.getPersonalRow = function(languageId) {
        return element(by.id(languageId));
    };

    this.getCount = function(index) {
        return this.list.count();
    };

    this.edit = function(name) {
        this.getRow(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-pencil')).click();
            browser.sleep(500);
        });
    };

    this.remove = function(name) {
        this.getRow(name).then(function(rows) {
            rows[0].click();
            rows[0].element(by.className('icon-trash')).click();
            browser.sleep(500);
            element(by.buttonText('OK')).click();
        });
    };

    this.getName = function() {
        return this.name.getText();
    };

    this.setName = function(name) {
        this.name.clear();
        this.name.sendKeys(name);
    };

    this.setLanguageId = function(languageId) {
        this.languageId.clear();
        this.languageId.sendKeys(languageId);
    };

    this.addDictionary = function() {
        element(by.id('createDictionary')).click();
        browser.sleep(100);
    };

    this.addPersonalDictionary = function() {
        element(by.id('createPersonalDictionary')).click();
        browser.sleep(100);
    };

    this.search = function(word) {
        element(by.id('words-search')).sendKeys(word);
    };

    this.save = function() {
        element(by.css('[ng-click="save()"]')).click();
    };

    this.cancel = function() {
        element(by.css('[ng-click="cancel()"]')).click();
    };

    this.saveWord = function() {
        element(by.buttonText('ADD WORD')).click();
    };

    this.getWord = function() {
        return this.word;
    };

    this.getAddWordButton = function() {
        return element(by.id('add-word-btn'));
    };

    this.getWordsCount = function () {
        return element.all(by.repeater('word in words')).count();
    };

    this.removeWord = function(index) {
        return element.all(by.repeater('word in words')).get(index || 0).element(by.css('button')).click();
    };
}
