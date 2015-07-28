
'use strict';

var openUrl = require('./utils').open;
var content = require('./content');

module.exports = new Highlights();

function Highlights() {
    this.list = element.all(by.repeater('config in configurations._items'));
    this.name = element(by.model('configEdit.name'));
    this.desks = element.all(by.repeater('desk in assignedDesks'));
    this.groups = element.all(by.repeater('group in configEdit.groups'));

    this.get = function() {
        openUrl('/#/settings/highlights');
    };

    this.getRow = function(name) {
        return this.list.filter(function(elem, index) {
            return elem.element(by.binding('config.name')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    this.getCount = function(index) {
        return this.list.count();
    };

    this.add = function() {
        element(by.className('icon-plus-sign')).click();
        browser.sleep(500);
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

    this.getDesk = function(name) {
        return this.desks.filter(function(elem, index) {
            return elem.element(by.binding('desk.name')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    this.toggleDesk = function(name) {
        this.getDesk(name).then(function(desks) {
            desks[0].element(by.className('sd-checkbox')).click();
        });
    };

    this.expectDeskSelection = function(name, selected) {
        this.getDesk(name).then(function(desks) {
            if (selected) {
                expect(desks[0].element(by.className('sd-checkbox')).getAttribute('checked')).toBe('true');
            } else {
                expect(desks[0].element(by.className('sd-checkbox')).getAttribute('checked')).toBe(null);
            }
        });
    };

    this.getGroup = function(name) {
        return this.groups.filter(function(elem, index) {
            return elem.element(by.binding('group')).getText().then(function(text) {
                return text.toUpperCase() === name.toUpperCase();
            });
        });
    };

    this.addGroup = function(name) {
        element(by.css('[ng-click="editGroup(\'\'); selectedGroup = null"]')).click();
        element(by.id('insert-group')).sendKeys(name);
        element(by.css('[ng-click="saveGroup()"]')).click();
    };

    this.editGroup = function(name, newName) {
        this.getGroup(name).click();
        this.getGroup(name).then(function(groups) {
            groups[0].element(by.css('[ng-click="editGroup(group)"]')).click();
        });
        element(by.id('edit-group')).clear();
        element(by.id('edit-group')).sendKeys(newName);
        element(by.css('[ng-click="saveGroup()"]')).click();
    };

    this.deleteGroup = function(name) {
        this.getGroup(name).click();
        this.getGroup(name).then(function(groups) {
            groups[0].element(by.css('[ng-click="removeGroup(group)"]')).click();
        });
    };

    this.save = function() {
        element(by.css('[ng-click="save()"]')).click();
    };

    this.cancel = function() {
        element(by.css('[ng-click="cancel()"]')).click();
    };

    this.getHighlights = function(elem) {
        return elem.all(by.repeater('h in highlights')).filter(function(highlight, index) {
            return highlight.getText().then(function(text) {
                return text;
            });
        });
    };

    this.selectHighlight = function(elem, name) {
        elem.all(by.repeater('h in highlights')).all(by.partialButtonText(name.toUpperCase())).click();
    };

    this.createHighlightsPackage = function(highlight) {
        element(by.className('svg-icon-create-list')).click();
        this.selectHighlight(element(by.id('highlightPackage')), highlight);
    };

    this.switchHighlightFilter = function(name) {
        element(by.id('search-highlights')).element(by.className('icon-dots-vertical')).click();
        element(by.id('search-highlights')).element(by.css('[option="' + name.toUpperCase() + '"]')).click();
    };

    this.exportHighlights = function() {
        element(by.id('export')).click();
    };

    this.multiMarkHighlight = function(name) {
        var elem = element(by.css('[class="multi-action-bar ng-scope"]'));
        elem.element(by.className('svg-icon-add-to-list')).click();
        browser.sleep(200);
        elem.all(by.repeater('h in highlights')).all(by.css('[option="' + name.toUpperCase() + '"]')).click();
        browser.sleep(200);
    };

    this.mark = function(highlight, item) {
        var menu = content.openItemMenu(item);
        return menu.element(by.partialButtonText(highlight.toUpperCase())).click();
    };
}
