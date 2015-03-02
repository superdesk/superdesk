
'use strict';

exports.workspace = new Workspace();
exports.content = new Content();
exports.authoring = new Authoring();

var browserManager = require('./utils').browserManager;

function Workspace() {
	this.getDesk = function(name) {
		var desks = browserManager.getElement().all(by.repeater('desk in userDesks'));
		return desks.all(by.css('[option="' + name.toUpperCase() + '"]'));
	};

    this.switchToDesk = function(desk) {
        var currElement = browserManager.getElement();
    	var selectedDesk = currElement(by.id('selected-desk'));
    	var personal = currElement(by.css('[option="PERSONAL"]'));
    	var getDesk = this.getDesk;

		browserManager.getBrowser().wait(function() {
			return selectedDesk.isPresent();
		});

		selectedDesk.getText().then(function(text) {
			if (text.toUpperCase() !== desk.toUpperCase()) {
				selectedDesk.click();
				if (desk.toUpperCase() === 'PERSONAL') {
					personal.click();
				} else {
			    	getDesk(desk).click();
				}
			}
		});
    };
}

function Content() {
    this.setListView = function() {
    	var list = browserManager.getElement()(by.css('[title="switch to list view"]'));
    	list.isDisplayed().then(function(isVisible) {
            if (isVisible) {
            	list.click();
            }
        });
    };
    this.setGridView = function() {
    	var grid = browserManager.getElement()(by.css('[title="switch to grid view"]'));
    	grid.then(function(isVisible) {
            if (isVisible) {
            	grid.click();
            }
        });
    };
    this.getItem = function(item) {
    	return browserManager.getElement().all(by.repeater('items._items')).get(item);
    };
    this.actionOnItem = function(action, item) {
    	var crtItem = this.getItem(item);
    	browserManager.getBrowser().actions().mouseMove(crtItem).perform();
    	crtItem.element(by.css('[title="' + action + '"]')).click();
    };
    this.checkMarkedForHighlight = function(highlight, item) {
    	var crtItem = this.getItem(item);
    	expect(crtItem.element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
    	expect(crtItem.element(by.className('icon-star-color')).getAttribute('tooltip')).toContain(highlight);
    };
}

function Authoring() {
    this.markAction = function() {
    	browserManager.getElement()(by.className('svg-icon-add-to-list')).click();
    };
    this.close = function() {
    	browserManager.getElement()(by.css('[ng-click="close()"]')).click();
    };
    this.save = function () {
    	browserManager.getElement()(by.css('[ng-click="save(item)"]')).click();
    };
    this.showSearch = function () {
    	browserManager.getElement()(by.id('Search')).click();
    };
    this.showVersions = function () {
    	browserManager.getElement()(by.css('[title="Versions"]')).click();
    };

    this.getSearchItem = function (item) {
    	return browserManager.getElement().all(by.repeater('pitem in contentItems')).get(item);
    };
    this.addToGroup = function (item, group) {
    	var crtItem = this.getSearchItem(item);
    	browserManager.getBrowser().actions().mouseMove(crtItem).perform();
    	crtItem.element(by.css('[title="Add to package"]')).click();
    	var groups = crtItem.all(by.repeater('t in groupList'));
    	groups.all(by.css('[option="' + group.toUpperCase() + '"]')).click();
    };
    this.addMultiToGroup = function (group) {
    	var addButton = browserManager.getElement()(by.css('[class="icon-package-plus"]'));
    	addButton.click();
    	var groups = browserManager.getElement()(by.repeater('t in groupList'));
    	groups.all(by.css('[option="' + group.toUpperCase() + '"]')).click();
    };
    this.getGroupItems = function (group) {
    	return browserManager.getElement()(by.id(group.toUpperCase())).all(by.repeater('item in group.items'));
    };
    this.getGroupItem = function (group, item) {
    	return this.getGroupItems(group).get(item);
    };
    this.moveToGroup = function (srcGroup, scrItem, dstGroup, dstItem) {
    	var src = this.getGroupItem(srcGroup, scrItem).element(by.css('[class="info"]'));
    	var dst = this.getGroupItem(dstGroup, dstItem).element(by.css('[class="info"]'));

    	browserManager.getBrowser().actions().
        mouseMove(src.getWebElement(), {x: 0, y: 0}).
        mouseDown().
        mouseMove(dst.getWebElement(), {x: 0, y: 0}).
        mouseUp().
        perform();
    };
    this.selectSearchItem = function (item) {
    	var crtItem = this.getSearchItem(item);
    	browserManager.getBrowser().actions().
        mouseMove(crtItem.element(by.tagName('i')).getWebElement()).
        perform();
    	crtItem.element(by.css('[ng-click="addToSelected(pitem)"]')).click();
    };
}
