
'use strict';

module.exports = new Workspace();

var content = require('./content'),
    nav = require('./utils').nav;

function Workspace() {
    this.open = function() {
        return nav('workspace/content');
    };

    this.openContent = this.open;

    this.openIngest = function() {
        return nav('workspace/ingest');
    };

    this.getDesk = function(name) {
        var desks = element.all(by.repeater('desk in userDesks'));
        return desks.all(by.css('[option="' + name.toUpperCase() + '"]'));
    };

    this.switchToDesk = function(desk) {
        var selectedDesk = element(by.id('selected-desk'));
        var personal = element(by.css('[option="PERSONAL"]'));
        var getDesk = this.getDesk;

        return selectedDesk.waitReady().then(function(elem) {
            return elem.getText();
        }).then(function(text) {
            if (text.toUpperCase() !== desk.toUpperCase()) {
                selectedDesk.click();
                if (desk.toUpperCase() === 'PERSONAL') {
                    return personal.click();
                } else {
                    return getDesk(desk).click();
                }
            }
        }).then(function() {
            return browser.wait(function() {
                return element(by.css('.list-view')).isPresent();
            });
        });
    };

    this.editItem = function(itemIndex, desk) {
        return this.switchToDesk(desk || 'PERSONAL').then(
            content.setListView
        ).then(function() {
            return content.actionOnItem('Edit item', itemIndex == null ? 1 : itemIndex);
        });
    };
}
