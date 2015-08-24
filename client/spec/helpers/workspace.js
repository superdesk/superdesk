
'use strict';

module.exports = new Workspace();

var content = require('./content'),
    nav = require('./utils').nav,
    authoring = require('./authoring');

function Workspace() {
    function openContent() {
        return nav('workspace/content');
    }

    function openIngest() {
        return nav('workspace/ingest');
    }

    this.open = this.openContent = openContent;
    this.openIngest = openIngest;

    this.getDesk = function(name) {
        var desks = element.all(by.repeater('desk in userDesks'));
        return desks.all(by.css('[option="' + name.toUpperCase() + '"]'));
    };

    /**
     * Open a workspace of given name, can be both desk or custom
     *
     * @param {string} desk Desk or workspace name.
     * @return {Promise}
     */
    this.switchToDesk = function(desk) {

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

        return openContent();
    };

    this.selectStage = function(stage) {
        var stages = element(by.css('.desk-stages'));
        return stages.element(by.cssContainingText('.stage-label', stage)).click();
    };

    this.editItem = function(item, desk) {
        return this.switchToDesk(desk || 'PERSONAL')
        .then(content.setListView)
        .then(function() {
            return content.actionOnItem('Edit item', item);
        });
    };

    this.actionOnItem = function(action, item, desk, stage) {
        if (desk !== undefined) {
            this.switchToDesk(desk || 'PERSONAL');
        }
        if (stage !== undefined) {
            this.selectStage(stage);
        }
        return content.setListView(desk !== undefined).then(function() {
            return content.actionOnItem(action, item);
        });
    };

    this.duplicateItem = function(item, desk, stage) {
        return this.switchToDesk(desk || 'PERSONAL')
        .then(content.setListView)
        .then(function() {
            return content.actionOnItem('Duplicate', item);
        }).then(function() {
            return authoring.sendToSidebarOpened(desk, stage);
        });
    };

    this.filterItems = function(type) {
        element(by.css('.filter-trigger')).click();
        element(by.css('.content-type-filters')).element(by.css('.filetype-icon-' + type)).click();
    };
}
