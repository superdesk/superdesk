
'use strict';

module.exports = new Authoring();

function Authoring() {
    /**
     * Send item to given desk
     */
    this.sendTo = function sendTo(desk) {
        var sidebar = element(by.css('.send-to-pane')),
            dropdown = sidebar.element(by.css('.desk-select .dropdown-toggle'));

        element(by.id('send-to-btn')).click();
        dropdown.waitReady();
        dropdown.click();

        sidebar.element(by.buttonText(desk)).click();
        sidebar.element(by.buttonText('send')).click();
    };

    this.markAction = function() {
        return element(by.className('svg-icon-add-to-list')).click();
    };
    this.close = function() {
        return element(by.css('[ng-click="close()"]')).click();
    };
    this.save = function() {
        return element(by.css('[ng-click="save(item)"]')).click();
    };
    this.showSearch = function() {
        return element(by.id('Search')).click();
    };
    this.showVersions = function() {
        return element(by.css('[title="Versions"]')).click();
    };

    this.getSearchItem = function(item) {
        return element.all(by.repeater('pitem in contentItems')).get(item);
    };
    this.addToGroup = function(item, group) {
        var crtItem = this.getSearchItem(item);
        browser.actions().mouseMove(crtItem).perform();
        crtItem.element(by.css('[title="Add to package"]')).click();
        var groups = crtItem.all(by.repeater('t in groupList'));
        return groups.all(by.css('[option="' + group.toUpperCase() + '"]')).click();
    };
    this.addMultiToGroup = function(group) {
        return element.all(by.css('[class="icon-package-plus"]')).first()
            .waitReady()
            .then(function(elem) {
                return elem.click();
            }).then(function() {
                var groups = element(by.repeater('t in groupList'));
                return groups.all(by.css('[option="' + group.toUpperCase() + '"]'))
                    .click();
            });
    };
    this.getGroupItems = function(group) {
        return element(by.id(group.toUpperCase())).all(by.repeater('item in group.items'));
    };
    this.getGroupItem = function(group, item) {
        return this.getGroupItems(group).get(item);
    };
    this.moveToGroup = function(srcGroup, scrItem, dstGroup, dstItem) {
        var src = this.getGroupItem(srcGroup, scrItem).element(by.css('[class="info"]'));
        var dst = this.getGroupItem(dstGroup, dstItem).element(by.css('[class="info"]'));
        return src.waitReady().then(function() {
            browser.actions()
                .mouseMove(src, {x: 0, y: 0})
                .mouseDown()
                .perform()
                .then(function() {
                    dst.waitReady().then(function () {
                        browser.actions()
                            .mouseMove(dst, {x: 0, y: 0})
                            .mouseUp()
                            .perform();
                    });
                });
        });
    };
    this.selectSearchItem = function(item) {
      var crtItem = this.getSearchItem(item);
      var icon = crtItem.element(by.tagName('i'));
      return icon.waitReady().then(function() {
          browser.actions()
              .mouseMove(icon)
              .perform();
      }).then(function() {
          crtItem.element(by.css('[ng-click="addToSelected(pitem)"]')).click();
      });
    };
}
